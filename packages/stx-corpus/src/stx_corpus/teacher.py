"""The generation client of the teacher campaign.

The client prompts the teacher for technical and instructional
sentences, and it runs two annotation passes for each sentence against
the localhost endpoint (training.md TRN-TEACH). The transport verb
tunnels the endpoint to the local port (TRN-TEACH-3).

A few-shot example comes from the train splits only: an eval-lane
sentence or a dev-split sentence must not enter a prompt (COR-LANES-4,
TRN-SFT-3). The two passes sample at a low temperature, with one fixed
seed for each pass, and training.md records the choice.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zlib
from pathlib import Path
from typing import Any

from . import schema
from .lanes import Record

#: The sampling of the generation call: diverse sentences. The seed
#: derives from the run and the batch, so a re-run of one batch
#: repeats its sentences.
GENERATION_TEMPERATURE = 0.9

#: The sampling of the two annotation passes. One fixed seed per pass
#: keeps the passes independent under one endpoint, and a batch stays
#: reproducible.
PASS_TEMPERATURE = 0.2
PASS_SEEDS = (11, 23)

#: Qwen3 opens a thinking block by default, and the judge compares
#: raw completions, so every request turns the mode off.
_CHAT_TEMPLATE_KWARGS = {"enable_thinking": False}

#: Sentences per generation call.
_SENTENCES_PER_CALL = 20

#: Few-shot examples per annotation prompt.
_EXAMPLE_COUNT = 3

_GENERATION_PROMPT = (
    "Write {count} short English sentences for a technical writing corpus. "
    "Make half of them technical statements about computer systems, and "
    "make the other half step-style instructions. Use 5 to 15 words per "
    "sentence. Write one sentence per line, with no numbering and no "
    "extra text."
)

_ANNOTATION_PROMPT = """Annotate the tokens of one English sentence with Universal Dependencies labels.

The input is one line per token: the 1-based index, one tab, and the token form. An empty line ends the input.

Reply with exactly one record line per token, in token order, and nothing else. A record holds five tab-separated fields: UPOS, lemma, head, deprel, and feats. The head field holds the 1-based index of the head token, or 0 for the root. The feats field holds "_", or Name=Value pairs joined with "|".

{examples}Input:
{tokens}Output:
"""

_EXAMPLE_TEMPLATE = "Input:\n{tokens}Output:\n{labels}\n"


class TeacherError(RuntimeError):
    """The endpoint reply does not hold a usable completion."""


#: The English clitics that the treebanks split from their host word.
#: Both apostrophe forms count: the token pattern admits both.
_CLITIC = re.compile(r"(?i)^(\w+?)(n['’]t|['’](?:s|re|ve|ll|d|m))$")


def tokenize(text: str) -> list[str]:
    """One deterministic token list for a generated sentence.

    The engine tokenizer of ENG-SPLIT labels shipped text. This split
    only shapes corpus records, and both annotation passes read the
    same forms. A clitic splits from its host word, as the treebank
    pairs do.
    """
    tokens: list[str] = []
    for raw in re.findall(r"\w+(?:['’-]\w+)*|[^\w\s]", text):
        match = _CLITIC.match(raw)
        tokens.extend(match.groups() if match else (raw,))
    return tokens


def batch_seed(run_id: str, batch: str) -> int:
    """The generation seed of one batch, stable across a re-run."""
    return zlib.crc32(f"{run_id}/{batch}".encode())


def chat(
    endpoint: str,
    model: str,
    prompt: str,
    *,
    temperature: float,
    seed: int | None = None,
    max_tokens: int = 2048,
    timeout: float = 600.0,
) -> str:
    """One chat completion against the tunneled endpoint."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "chat_template_kwargs": _CHAT_TEMPLATE_KWARGS,
    }
    if seed is not None:
        payload["seed"] = seed
    request = urllib.request.Request(
        f"{endpoint}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            reply = json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TeacherError(f"the endpoint {endpoint} gave no usable reply: {error}") from error
    try:
        content = reply["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise TeacherError(f"the endpoint reply holds no completion: {reply!r}") from error
    if not isinstance(content, str):
        raise TeacherError(f"the completion is not text: {content!r}")
    return content


def select_examples(records: list[Record], count: int = _EXAMPLE_COUNT) -> list[Record]:
    """The few-shot examples: short train-split treebank sentences only.

    The filter keeps the lane rule at the prompt boundary: a dev-split
    record and a non-treebank record never leave this function.
    """
    examples = [
        record
        for record in records
        if record.source in ("ewt", "gum")
        and record.split == "train"
        and 3 <= len(record.sentence.tokens) <= 12
    ]
    return examples[:count]


def generation_prompt(count: int) -> str:
    return _GENERATION_PROMPT.format(count=count)


def annotation_prompt(forms: list[str], examples: list[Record]) -> str:
    rendered = "".join(
        _EXAMPLE_TEMPLATE.format(
            tokens=schema.render_tokens([token.form for token in example.sentence.tokens]),
            labels=schema.render_labels(example.sentence.tokens),
        )
        for example in examples
    )
    return _ANNOTATION_PROMPT.format(examples=rendered, tokens=schema.render_tokens(forms))


def generate(endpoint: str, model: str, count: int, seed: int) -> list[str]:
    """Prompt the teacher for `count` fresh sentences.

    The seed offsets by the call index: one seed for each call, and
    the whole batch stays reproducible.
    """
    sentences: list[str] = []
    seen: set[str] = set()
    for call in range(1, 100):
        if len(sentences) >= count:
            break
        batch = min(_SENTENCES_PER_CALL, count - len(sentences))
        reply = chat(
            endpoint,
            model,
            generation_prompt(batch),
            temperature=GENERATION_TEMPERATURE,
            seed=seed + call,
        )
        fresh: list[str] = []
        for line in (line.strip() for line in reply.splitlines()):
            if line and line not in seen and len(tokenize(line)) >= 3:
                seen.add(line)
                fresh.append(line)
        if not fresh:
            raise TeacherError("the generation call returned no usable sentence")
        sentences.extend(fresh[: count - len(sentences)])
    if len(sentences) < count:
        raise TeacherError(f"{len(sentences)} sentences for a count of {count}")
    return sentences


def annotate(endpoint: str, model: str, forms: list[str], examples: list[Record]) -> list[str]:
    """The two annotation passes for one token list."""
    prompt = annotation_prompt(forms, examples)
    return [
        chat(endpoint, model, prompt, temperature=PASS_TEMPERATURE, seed=seed)
        for seed in PASS_SEEDS
    ]


def propose(
    endpoint: str,
    model: str,
    records: list[Record],
    count: int,
    run_id: str,
    batch: str,
) -> list[dict[str, Any]]:
    """The proposed records of one bounded batch."""
    examples = select_examples(records)
    seed = batch_seed(run_id, batch)
    proposals: list[dict[str, Any]] = []
    for index, text in enumerate(generate(endpoint, model, count, seed), start=1):
        forms = tokenize(text)
        proposals.append(
            {
                "sent_id": f"teach-{run_id}-{batch}-{index}",
                "text": text,
                "forms": forms,
                "passes": annotate(endpoint, model, forms, examples),
            }
        )
    return proposals


def write_proposals(proposals: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for proposal in proposals:
            handle.write(json.dumps(proposal) + "\n")


def main(argv: list[str] | None = None) -> int:
    from .lanes import read_records

    parser = argparse.ArgumentParser(description="The FuguSTX generation client.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000")
    parser.add_argument("--model", required=True)
    parser.add_argument("--records", type=Path, required=True, help="the lane JSONL file")
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    records = read_records(args.records)
    try:
        proposals = propose(args.endpoint, args.model, records, args.count, args.run_id, args.batch)
    except TeacherError as error:
        print(f"teacher: {error}", file=sys.stderr)
        return 1
    write_proposals(proposals, args.out)
    print(f"teacher: {len(proposals)} proposals -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

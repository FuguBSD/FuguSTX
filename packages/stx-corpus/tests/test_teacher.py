"""Run the generation client against a stub endpoint.

The stub answers like the vLLM OpenAI-compatible endpoint, and it
records each request body. The tests prove the prompt rule: no
eval-lane and no dev-split sentence enters a prompt.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus.conllu import parse_sentences
from stx_corpus.lanes import Record, build_lanes
from stx_corpus.schema import render_tokens
from stx_corpus.teacher import (
    GENERATION_TEMPERATURE,
    PASS_SEEDS,
    PASS_TEMPERATURE,
    annotation_prompt,
    batch_seed,
    propose,
    select_examples,
    tokenize,
)

#: The stub reply repeats one sentence: the client must drop the
#: duplicate inside one reply.
_SENTENCES = [
    "The daemon writes one log file.",
    "Restart the service after each change.",
    "Restart the service after each change.",
    "The kernel maps each page once.",
    "Check the exit status of the call.",
]


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(body)
        prompt = body["messages"][0]["content"]
        if prompt.startswith("Write"):
            content = "\n".join(_SENTENCES)
        else:
            tokens = prompt.rsplit("Input:\n", 1)[1].split("\n\n", 1)[0]
            content = "NOUN\tx\t0\troot\t_\n" * len(tokens.splitlines())
        data = json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        pass


@pytest.fixture
def endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    server.requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}", server.requests
    server.shutdown()
    thread.join()


def _records():
    ewt = {
        "train": parse_sentences(EWT_TRAIN),
        "dev": parse_sentences(EWT_DEV),
        "test": parse_sentences(EWT_TEST),
    }
    gum = {"train": parse_sentences(GUM_TRAIN), "dev": [], "test": []}
    pud = parse_sentences(PUD_TEST)
    prose = [
        Record(
            "prose",
            "train",
            "37134",
            parse_sentences("# sent_id = prose-1\n# text = Prose text.\n")[0],
        )
    ]
    lanes = build_lanes(ewt, gum, pud, prose, tag="r2.18")
    return list(lanes.training) + list(lanes.eval)


def test_tokenize_is_deterministic_and_splits_punctuation():
    assert tokenize("Restart the daemon.") == ["Restart", "the", "daemon", "."]
    assert tokenize("x = 1;") == ["x", "=", "1", ";"]


def test_tokenize_splits_a_clitic_like_the_treebanks():
    assert tokenize("Don't stop.") == ["Do", "n't", "stop", "."]
    assert tokenize("It's the kernel's job.") == ["It", "'s", "the", "kernel", "'s", "job", "."]
    assert tokenize("Don’t stop.") == ["Do", "n’t", "stop", "."]  # the curly apostrophe


def test_batch_seed_is_stable_and_batch_specific():
    assert batch_seed("run-1", "b1") == batch_seed("run-1", "b1")
    assert batch_seed("run-1", "b1") != batch_seed("run-1", "b2")


def test_select_examples_takes_train_split_treebank_records_only():
    examples = select_examples(_records(), count=10)
    assert examples
    assert all(example.split == "train" for example in examples)
    assert all(example.source in ("ewt", "gum") for example in examples)


def test_propose_runs_two_passes_per_sentence(endpoint):
    url, requests = endpoint
    proposals = propose(url, "stub-model", _records(), 3, "run-1", "batch-1")

    assert len(proposals) == 3
    assert [p["sent_id"] for p in proposals] == [f"teach-run-1-batch-1-{i}" for i in (1, 2, 3)]
    texts = [proposal["text"] for proposal in proposals]
    assert len(set(texts)) == 3  # the reply duplicate is dropped
    for proposal in proposals:
        assert proposal["forms"] == tokenize(proposal["text"])
        assert len(proposal["passes"]) == 2

    annotations = [
        body for body in requests if not body["messages"][0]["content"].startswith("Write")
    ]
    assert len(annotations) == 6
    assert {body["seed"] for body in annotations} == set(PASS_SEEDS)
    assert all(body["temperature"] == PASS_TEMPERATURE for body in annotations)

    generations = [body for body in requests if body["messages"][0]["content"].startswith("Write")]
    assert all(body["temperature"] == GENERATION_TEMPERATURE for body in generations)
    # A re-run of one batch repeats its sentences: the generation call
    # seeds on the run and the batch.
    assert all(body["seed"] == batch_seed("run-1", "batch-1") + 1 for body in generations)

    # Qwen3 opens a thinking block by default, and the judge compares
    # raw completions, so every request turns the mode off.
    assert all(body["chat_template_kwargs"] == {"enable_thinking": False} for body in requests)


def test_no_eval_lane_and_no_dev_split_sentence_enters_a_prompt(endpoint):
    url, requests = endpoint
    records = _records()
    propose(url, "stub-model", records, 2, "run-1", "batch-1")

    guarded = [
        record
        for record in records
        if record.split != "train" or record.source not in ("ewt", "gum")
    ]
    guarded_texts = {record.sentence.text for record in guarded}
    assert "Dogs run." in guarded_texts  # the dev split
    assert "Birds fly." in guarded_texts  # the eval lane
    prompts = "\n".join(body["messages"][0]["content"] for body in requests)
    for record in guarded:
        assert record.sentence.text not in prompts
        if record.sentence.tokens:
            rendered = render_tokens([token.form for token in record.sentence.tokens])
            assert rendered not in prompts
    # A train-split few-shot example enters as the token serialization.
    assert "1\tA\n2\tcat\n3\tsat\n" in prompts


def test_a_non_json_reply_is_a_clean_teacher_error(monkeypatch):
    # A half-up endpoint can answer 200 with a non-JSON body.
    import io
    import urllib.request

    from stx_corpus.teacher import TeacherError, chat

    monkeypatch.setattr(urllib.request, "urlopen", lambda *_args, **_kwargs: io.BytesIO(b"<html>"))
    with pytest.raises(TeacherError, match="no usable reply"):
        chat("http://127.0.0.1:1", "stub", "prompt", temperature=0.2)


def test_the_annotation_prompt_holds_the_schema_serialization():
    examples = select_examples(_records())
    prompt = annotation_prompt(["Reboot", "now", "."], examples)
    assert "1\tReboot\n2\tnow\n3\t.\n\n" in prompt
    assert "DET\ta\t2\tdet\t_\n" in prompt  # the train example labels

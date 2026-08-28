import json

from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus.conllu import Sentence, parse_sentences
from stx_corpus.lanes import Record, build_lanes
from stx_corpus.upload import write_corpus_files, write_eval_files


def _lanes():
    ewt = {
        "train": parse_sentences(EWT_TRAIN),
        "dev": parse_sentences(EWT_DEV),
        "test": parse_sentences(EWT_TEST),
    }
    gum = {"train": parse_sentences(GUM_TRAIN), "dev": [], "test": []}
    prose = [Record("prose", "train", "37134", Sentence("gutenberg-37134-0", "Omit words.", ()))]
    return build_lanes(ewt, gum, parse_sentences(PUD_TEST), prose, tag="r2.18")


def test_write_corpus_files_holds_the_training_lane_only(tmp_path):
    paths = write_corpus_files(_lanes(), tmp_path)
    names = {path.name for path in paths}
    assert names == {"training.jsonl", "prose.jsonl", "pairs.jsonl", "manifest.json"}

    # COR-LANES-4: no eval sentence reaches the corpus bucket files.
    text = (tmp_path / "training.jsonl").read_text(encoding="utf-8")
    assert "ewt-test-1" not in text
    assert "pud-test-1" not in text

    prose = (tmp_path / "prose.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(prose[0]) == {"text": "Omit words."}

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["ud_release"] == "r2.18"
    assert manifest["pairs"] == 3


def test_write_eval_files_holds_the_eval_lane_only(tmp_path):
    write_eval_files(_lanes(), tmp_path)
    text = (tmp_path / "eval.jsonl").read_text(encoding="utf-8")
    assert "ewt-test-1" in text and "pud-test-1" in text
    assert "ewt-train-1" not in text and "ewt-dev-1" not in text

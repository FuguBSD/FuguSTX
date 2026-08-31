import json

from corpus_fakes import EWT_DEV, EWT_TEST, EWT_TRAIN, GUM_TRAIN, PUD_TEST
from stx_corpus import upload as upload_module
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


def test_upload_builds_one_client_for_every_file(monkeypatch, tmp_path):
    # Each client call resolves the credential, so one client writes
    # the corpus files and the eval files of one upload.
    seen = {"built": [], "used": []}
    monkeypatch.setattr(
        upload_module.bucket, "client", lambda: seen["built"].append("client-0") or "client-0"
    )
    monkeypatch.setattr(
        upload_module.bucket,
        "put_file",
        lambda name, key, path, s3=None: seen["used"].append((name, key, s3)),
    )

    upload_module.upload(_lanes(), tmp_path)

    assert seen["built"] == ["client-0"]
    assert [name for name, _, _ in seen["used"]] == ["stx-corpus"] * 4 + ["stx-evalcorpus"] * 2
    assert {s3 for _, _, s3 in seen["used"]} == {"client-0"}


def test_write_eval_files_holds_the_eval_lane_only(tmp_path):
    write_eval_files(_lanes(), tmp_path)
    text = (tmp_path / "eval.jsonl").read_text(encoding="utf-8")
    assert "ewt-test-1" in text and "pud-test-1" in text
    assert "ewt-train-1" not in text and "ewt-dev-1" not in text

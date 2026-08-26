import json

from corpus_fakes import fake_fetch_treebank, patch_fetch
from stx_corpus import fetch, pipeline


def test_build_fetches_filters_and_splits(monkeypatch):
    patch_fetch(monkeypatch, fetch)

    lanes = pipeline.build()

    training_ids = {record.sentence.sent_id for record in lanes.training}
    eval_ids = {record.sentence.sent_id for record in lanes.eval}

    # ewt train/dev and the un-excluded gum doc join training; the whow
    # doc (GUM_whow_sample) is excluded, per COR-SOURCES-3.
    assert "ewt-train-1" in training_ids
    assert "ewt-dev-1" in training_ids
    assert "gum-train-1" in training_ids
    assert "gum-train-2" not in training_ids

    # the prose lane (3 books x 2 paragraphs) joins training too.
    prose_records = [record for record in lanes.training if record.source == "prose"]
    assert len(prose_records) == len(fetch.GUTENBERG_BOOKS) * 2
    assert prose_records[0].sentence.text == "First paragraph."

    # ewt test, gum test, and pud test go to the eval lane.
    assert eval_ids == {"ewt-test-1", "gum-test-1", "pud-test-1"}


def test_build_excludes_a_sentence_with_no_doc_id(monkeypatch):
    # A sentence with no newdoc id carries no provable license, so
    # COR-SOURCES-3 must exclude it rather than default to including it.
    gum_no_doc_id = (
        "# sent_id = gum-orphan-1\n# text = Orphan.\n1\tOrphan\torphan\tNOUN\t_\t_\t0\troot\t_\t_\n"
    )

    def fake_treebank_with_orphan(name):
        splits = fake_fetch_treebank(name)
        return {**splits, "train": gum_no_doc_id} if name == "gum" else splits

    patch_fetch(monkeypatch, fetch)
    monkeypatch.setattr(fetch, "fetch_treebank", fake_treebank_with_orphan)

    lanes = pipeline.build()

    training_ids = {record.sentence.sent_id for record in lanes.training}
    assert "gum-orphan-1" not in training_ids


def test_write_lanes_writes_valid_jsonl(tmp_path, monkeypatch):
    patch_fetch(monkeypatch, fetch)

    lanes = pipeline.build()
    output = tmp_path / "corpus"
    pipeline.write_lanes(lanes, output)

    training_lines = (output / "training.jsonl").read_text(encoding="utf-8").splitlines()
    eval_lines = (output / "eval.jsonl").read_text(encoding="utf-8").splitlines()

    assert len(training_lines) == len(lanes.training)
    assert len(eval_lines) == len(lanes.eval)

    first = json.loads(training_lines[0])
    assert first["source"] == "ewt"
    assert first["tokens"][0]["form"] == "A"


def test_main_writes_to_the_given_output_directory(tmp_path, monkeypatch, capsys):
    patch_fetch(monkeypatch, fetch)

    output = tmp_path / "out"
    exit_code = pipeline.main(["--output", str(output)])

    assert exit_code == 0
    assert (output / "training.jsonl").exists()
    assert (output / "eval.jsonl").exists()
    assert "training:" in capsys.readouterr().out

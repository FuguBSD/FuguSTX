import json

from stx_corpus import cards, t1

# One dev card of two treebanks, one shard card, and one tier T1 card
# of three treebanks. The tier T1 card holds no shard key, and the
# thread count of a GPU run is null. The bucket also holds objects
# that are not scorecards.
DEV_CARD = {
    "counts": {
        "ewt": {"failures": 0, "las": 8, "lemma": 9, "sentences": 2, "tokens": 10, "upos": 9},
        "gum": {"failures": 0, "las": 7, "lemma": 9, "sentences": 2, "tokens": 10, "upos": 9},
    },
    "device": "gpu",
    "label": "sft-cpt",
    "llama_version": "b10666",
    "model_hash": "abc",
    "run_id": "gh-1",
    "scores": {
        "ewt": {"las": 0.8, "lemma": 0.9, "upos": 0.9},
        "gum": {"las": 0.7, "lemma": 0.9, "upos": 0.9},
    },
    "shard": None,
    "split": "dev",
    "threads": None,
    "ud_release": "r2.18",
}

SHARD_CARD = {
    "counts": {},
    "device": "cpu",
    "label": "sft-aug",
    "llama_version": "b10666",
    "model_hash": "def",
    "run_id": "gh-2",
    "scores": {"ewt": {"las": 0.5, "lemma": 0.6, "upos": 0.7}},
    "shard": "0/2",
    "split": "eval",
    "threads": 4,
    "ud_release": "r2.18",
}

T1_CARD = {
    "counts": {},
    "device": "cpu",
    "label": "sft-aug",
    "llama_version": "b10666",
    "model_hash": "def",
    "run_id": "gh-2",
    "scores": {
        "ewt": {"las": 0.7738, "lemma": 0.9506, "upos": 0.9377},
        "gum": {"las": 0.7673, "lemma": 0.9569, "upos": 0.9386},
        "pud": {"las": 0.7848, "lemma": 0.9637, "upos": 0.9543},
    },
    "split": "eval",
    "threads": 4,
    "ud_release": "r2.18",
}

OBJECTS = {
    "runs/gh-1/scorecard-dev-sft-cpt.json": DEV_CARD,
    "runs/gh-1/stx-sft-cpt.gguf": None,
    "runs/gh-2/scorecard-eval-sft-aug-shard0of2.json": SHARD_CARD,
    "runs/gh-2/scorecard-t1-sft-aug.json": T1_CARD,
    "runs/gh-2/scorecard-notes.txt": None,
    "runs/gh-2/teach-report-gh-3.json": None,
    "runs/gh-2/teach-rejects-gh-3.jsonl": None,
    "kvm-test/result.txt": None,
}

HEADER = "run   label    split  device  shard  treebank    upos   lemma     las"


def _fake_bucket(monkeypatch, objects=None):
    """Answer every bucket call from a dictionary, so no test reaches
    the network. The return value records each client that the reader
    builds, and each client that reaches a call."""
    store = OBJECTS if objects is None else objects
    seen = {"built": [], "used": [], "names": []}

    def client():
        built = f"client-{len(seen['built'])}"
        seen["built"].append(built)
        return built

    def list_keys(name, prefix="", s3=None):
        seen["used"].append(s3)
        seen["names"].append(name)
        return sorted(key for key in store if key.startswith(prefix))

    def get_text(name, key, s3=None):
        seen["used"].append(s3)
        seen["names"].append(name)
        return json.dumps(store[key])

    monkeypatch.setattr(cards.bucket, "client", client)
    monkeypatch.setattr(cards.bucket, "list_keys", list_keys)
    monkeypatch.setattr(cards.bucket, "get_text", get_text)
    return seen


def test_card_keys_drops_every_other_object():
    # A scorecard key ends with .json (EVL-TIERS-8), so a note file
    # with the same name prefix reaches no json.loads call.
    assert cards.card_keys(sorted(OBJECTS)) == [
        "runs/gh-1/scorecard-dev-sft-cpt.json",
        "runs/gh-2/scorecard-eval-sft-aug-shard0of2.json",
        "runs/gh-2/scorecard-t1-sft-aug.json",
    ]


def test_read_cards_builds_one_client(monkeypatch):
    # Each client call resolves the credential, so the reader must
    # build one client, and that client must reach the listing call
    # and every read call.
    seen = _fake_bucket(monkeypatch)

    cards.read_cards("stx-other")
    assert seen["built"] == ["client-0"]
    assert seen["used"] == ["client-0"] * 4  # one listing, three reads
    # The bucket name of the caller must reach each call, because
    # make scorecards names the bucket of train/config.env.
    assert seen["names"] == ["stx-other"] * 4


def test_rows_holds_one_row_for_each_scorecard_and_treebank(monkeypatch):
    _fake_bucket(monkeypatch)
    table = cards.rows(cards.read_cards())
    assert [(row[0], row[4], row[5]) for row in table] == [
        ("gh-1", "-", "ewt"),
        ("gh-1", "-", "gum"),
        ("gh-2", "0/2", "ewt"),
        ("gh-2", "-", "ewt"),
        ("gh-2", "-", "gum"),
        ("gh-2", "-", "pud"),
    ]
    assert table[3] == ("gh-2", "sft-aug", "eval", "cpu", "-", "ewt", "0.9377", "0.9506", "0.7738")


def test_the_run_option_keeps_one_run(monkeypatch):
    _fake_bucket(monkeypatch)
    assert {card["run_id"] for card in cards.read_cards(run="gh-2")} == {"gh-2"}
    assert cards.read_cards(run="no-such-run") == []


def test_the_reader_takes_the_key_form_of_the_writer():
    # EVL-TIERS-8: one definition serves the write and the read, so a
    # key that t1 builds must reach the reader.
    keys = [
        t1.scorecard_key(DEV_CARD),
        t1.scorecard_key(SHARD_CARD),
        t1.scorecard_key(T1_CARD, aggregate=True),
    ]
    assert keys == [
        "runs/gh-1/scorecard-dev-sft-cpt.json",
        "runs/gh-2/scorecard-eval-sft-aug-shard0of2.json",
        "runs/gh-2/scorecard-t1-sft-aug.json",
    ]
    assert cards.card_keys(keys) == keys
    assert all(key.startswith(cards.prefix()) for key in keys)
    assert cards.prefix("gh-2") == "runs/gh-2/"


def test_an_empty_read_names_the_place(monkeypatch, capsys):
    # An empty table and a mistyped name look the same on the output,
    # so the reader reports the place that holds no scorecard.
    _fake_bucket(monkeypatch)
    assert cards.main(["--run", "no-such-run"]) == 0
    reply = capsys.readouterr()
    assert reply.err.strip() == "no scorecard under s3://stx-artifacts/runs/no-such-run/"
    assert reply.out.splitlines() == [
        "run  label  split  device  shard  treebank  upos  lemma  las"
    ]


def test_render_aligns_each_column(monkeypatch):
    _fake_bucket(monkeypatch)
    lines = cards.render(cards.rows(cards.read_cards())).splitlines()
    assert lines[0] == HEADER
    # A rate column aligns to the right, and every other column
    # aligns to the left.
    assert lines[4] == "gh-2  sft-aug  eval   cpu     -      ewt       0.9377  0.9506  0.7738"


def test_a_treebank_without_a_score_gives_no_row(monkeypatch):
    # t1.scores drops a treebank with zero tokens, so a scorecard can
    # hold an empty scores object. The reader must print no row, and
    # it must raise nothing.
    empty = {**DEV_CARD, "counts": {}, "scores": {}}
    _fake_bucket(monkeypatch, {"runs/gh-1/scorecard-dev-empty.json": empty})
    assert cards.rows(cards.read_cards()) == []
    assert cards.render([]).splitlines() == [
        "run  label  split  device  shard  treebank  upos  lemma  las"
    ]


def test_main_prints_the_table_and_the_json(monkeypatch, capsys):
    _fake_bucket(monkeypatch)
    assert cards.main(["--run", "gh-1"]) == 0
    out = capsys.readouterr().out
    assert "gh-1" in out and "gh-2" not in out

    assert cards.main(["--json"]) == 0
    assert [card["run_id"] for card in json.loads(capsys.readouterr().out)] == [
        "gh-1",
        "gh-2",
        "gh-2",
    ]

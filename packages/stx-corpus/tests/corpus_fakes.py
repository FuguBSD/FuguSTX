"""Fake corpus sources shared by test_pipeline.py and test_t0.py.

Not a test module: pytest only collects files named `test_*`.
"""

EWT_TRAIN = "# sent_id = ewt-train-1\n# text = A cat sat.\n1\tA\ta\tDET\t_\t_\t2\tdet\t_\t_\n2\tcat\tcat\tNOUN\t_\t_\t3\tnsubj\t_\t_\n3\tsat\tsit\tVERB\t_\t_\t0\troot\t_\t_\n"
EWT_DEV = "# sent_id = ewt-dev-1\n# text = Dogs run.\n1\tDogs\tdog\tNOUN\t_\t_\t2\tnsubj\t_\t_\n2\trun\trun\tVERB\t_\t_\t0\troot\t_\t_\n"
EWT_TEST = "# sent_id = ewt-test-1\n# text = Birds fly.\n1\tBirds\tbird\tNOUN\t_\t_\t2\tnsubj\t_\t_\n2\tfly\tfly\tVERB\t_\t_\t0\troot\t_\t_\n"

GUM_TRAIN = (
    "# newdoc id = GUM_bio_sample\n"
    "# sent_id = gum-train-1\n"
    "# text = She wrote.\n"
    "1\tShe\tshe\tPRON\t_\t_\t2\tnsubj\t_\t_\n"
    "2\twrote\twrite\tVERB\t_\t_\t0\troot\t_\t_\n"
    "\n"
    "# newdoc id = GUM_whow_sample\n"
    "# sent_id = gum-train-2\n"
    "# text = Fold it.\n"
    "1\tFold\tfold\tVERB\t_\t_\t0\troot\t_\t_\n"
    "2\tit\tit\tPRON\t_\t_\t1\tobj\t_\t_\n"
)
GUM_DEV = "# newdoc id = GUM_bio_sample\n# sent_id = gum-dev-1\n# text = We saw.\n1\tWe\twe\tPRON\t_\t_\t2\tnsubj\t_\t_\n2\tsaw\tsee\tVERB\t_\t_\t0\troot\t_\t_\n"
GUM_TEST = "# newdoc id = GUM_bio_sample\n# sent_id = gum-test-1\n# text = He read.\n1\tHe\the\tPRON\t_\t_\t2\tnsubj\t_\t_\n2\tread\tread\tVERB\t_\t_\t0\troot\t_\t_\n"

PUD_TEST = "# sent_id = pud-test-1\n# text = It rains.\n1\tIt\tit\tPRON\t_\t_\t2\tnsubj\t_\t_\n2\trains\train\tVERB\t_\t_\t0\troot\t_\t_\n"

GUM_LICENSE = (
    "wikiHow texts are made available under a CC-BY-NC-SA license, as are the fiction texts."
)

GUTENBERG_BOOK = (
    "Header noise.\n\n"
    "*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE ***\n\n"
    "First paragraph.\n\n"
    "Second paragraph.\n\n"
    "*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE ***\n\n"
    "Footer noise.\n"
)


def fake_fetch_treebank(name):
    return {
        "ewt": {"train": EWT_TRAIN, "dev": EWT_DEV, "test": EWT_TEST},
        "gum": {"train": GUM_TRAIN, "dev": GUM_DEV, "test": GUM_TEST},
        "pud": {"test": PUD_TEST},
    }[name]


def patch_fetch(monkeypatch, fetch_module):
    """Patch every network call of `fetch_module` with the fakes above."""
    monkeypatch.setattr(fetch_module, "fetch_treebank", fake_fetch_treebank)
    monkeypatch.setattr(fetch_module, "fetch_gum_license", lambda: GUM_LICENSE)
    monkeypatch.setattr(fetch_module, "fetch_gutenberg_book", lambda ebook_id: GUTENBERG_BOOK)

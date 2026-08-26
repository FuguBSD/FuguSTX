from stx_corpus import fetch


def test_treebank_url_pins_the_ud_release_tag():
    url = fetch.treebank_url("UD_English-EWT", "en_ewt", "dev")
    assert url == (
        "https://raw.githubusercontent.com/UniversalDependencies/"
        "UD_English-EWT/r2.18/en_ewt-ud-dev.conllu"
    )


def test_gum_license_url_pins_the_same_release_tag():
    assert fetch.UD_RELEASE_TAG in fetch.GUM_LICENSE_URL
    assert fetch.GUM_LICENSE_URL.endswith("/LICENSE.txt")


def test_gutenberg_url_uses_the_ebook_id():
    assert fetch.gutenberg_url(37134) == "https://www.gutenberg.org/cache/epub/37134/pg37134.txt"


def test_treebanks_table_matches_the_source_table():
    # corpus.md's source table: PUD ships one test split only.
    assert fetch.TREEBANKS["pud"][2] == ("test",)
    assert fetch.TREEBANKS["ewt"][2] == ("train", "dev", "test")
    assert fetch.TREEBANKS["gum"][2] == ("train", "dev", "test")

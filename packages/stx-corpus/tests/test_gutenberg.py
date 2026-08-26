import pytest
from stx_corpus.gutenberg import strip_boilerplate

SAMPLE = """\
The Project Gutenberg eBook of A Sample Book

Header noise line one.
Header noise line two.

*** START OF THE PROJECT GUTENBERG EBOOK A SAMPLE BOOK ***

Chapter One

This is the body text.

*** END OF THE PROJECT GUTENBERG EBOOK A SAMPLE BOOK ***

Footer noise line one.
"""


def test_strip_boilerplate_keeps_only_the_body():
    body = strip_boilerplate(SAMPLE)
    assert body == "Chapter One\n\nThis is the body text."
    assert "Header noise" not in body
    assert "Footer noise" not in body


def test_strip_boilerplate_requires_both_markers():
    with pytest.raises(ValueError, match="marker"):
        strip_boilerplate("no markers here")


SAMPLE_WITH_SCAN_ARTIFACTS = """\
The Project Gutenberg eBook of A Sample Book

*** START OF THE PROJECT GUTENBERG EBOOK A SAMPLE BOOK ***

</pre>



Produced by Jane Doe and the Online Distributed
Proofreading Team at http://www.pgdp.net



Chapter One

This is the body text.

<pre id="pg-footer">

*** END OF THE PROJECT GUTENBERG EBOOK A SAMPLE BOOK ***
"""


def test_strip_boilerplate_drops_a_repeated_credits_paragraph_and_html_tags():
    # Some Gutenberg transcriptions, for example ebook 37134, repeat a
    # "Produced by ..." credits paragraph, a bare stray HTML tag right
    # after the start marker, and an attribute-bearing tag before the end
    # marker.
    body = strip_boilerplate(SAMPLE_WITH_SCAN_ARTIFACTS)
    assert body == "Chapter One\n\nThis is the body text."

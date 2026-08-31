from types import SimpleNamespace

import pytest
from botocore.exceptions import ProfileNotFound
from stx_corpus import bucket

# Every credential name that client() reads. A test clears each one,
# so the environment of the operator changes no result.
_NAMES = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "SCW_ACCESS_KEY",
    "SCW_SECRET_KEY",
    "AWS_PROFILE",
    "SCW_PROFILE",
)


def _fake_boto3(monkeypatch):
    """Replace boto3 with a recorder, so no test builds a real client."""
    calls = {}

    def client(service, **arguments):
        calls["client"] = {"service": service, **arguments}
        return "key-client"

    class Session:
        def __init__(self, profile_name):
            calls["profile"] = profile_name

        def client(self, service, **arguments):
            calls["client"] = {"service": service, **arguments}
            return "profile-client"

    for name in _NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        bucket, "boto3", SimpleNamespace(client=client, session=SimpleNamespace(Session=Session))
    )
    return calls


def test_the_key_pair_of_the_environment_comes_first(monkeypatch):
    calls = _fake_boto3(monkeypatch)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setenv("AWS_PROFILE", "fugustx")

    assert bucket.client() == "key-client"
    assert calls["client"] == {
        "service": "s3",
        "endpoint_url": bucket.ENDPOINT,
        "region_name": bucket.REGION,
        "aws_access_key_id": "key",
        "aws_secret_access_key": "secret",
    }
    assert "profile" not in calls


def test_the_scw_key_names_work(monkeypatch):
    calls = _fake_boto3(monkeypatch)
    monkeypatch.setenv("SCW_ACCESS_KEY", "key")
    monkeypatch.setenv("SCW_SECRET_KEY", "secret")

    assert bucket.client() == "key-client"
    assert calls["client"]["aws_access_key_id"] == "key"
    assert calls["client"]["aws_secret_access_key"] == "secret"


@pytest.mark.parametrize(
    "names",
    [
        {"AWS_ACCESS_KEY_ID": "key"},
        {"AWS_SECRET_ACCESS_KEY": "secret"},
        {"SCW_ACCESS_KEY": "key"},
        {"SCW_SECRET_KEY": "secret"},
        # Two families give two identities, and the pair of one
        # family must answer alone.
        {"AWS_ACCESS_KEY_ID": "key", "SCW_SECRET_KEY": "secret"},
    ],
)
def test_half_a_key_pair_raises(monkeypatch, names):
    _fake_boto3(monkeypatch)
    for name, value in names.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("AWS_PROFILE", "fugustx")

    # A fall through to the profile would give a different identity.
    with pytest.raises(RuntimeError, match="half"):
        bucket.client()


def test_the_profile_path_names_the_identity(monkeypatch):
    calls = _fake_boto3(monkeypatch)
    monkeypatch.setenv("AWS_PROFILE", "fugustx")

    assert bucket.client() == "profile-client"
    assert calls["profile"] == "fugustx"
    assert calls["client"] == {
        "service": "s3",
        "endpoint_url": bucket.ENDPOINT,
        "region_name": bucket.REGION,
    }


def test_the_scw_profile_reaches_no_client(monkeypatch):
    # boto3 reads no scw configuration file, so SCW_PROFILE selects
    # nothing here.
    _fake_boto3(monkeypatch)
    monkeypatch.setenv("SCW_PROFILE", "fugustx")

    with pytest.raises(RuntimeError, match="no Object Storage credential"):
        bucket.client()


def test_an_unknown_profile_raises_the_module_error(monkeypatch):
    # botocore raises ProfileNotFound, and the operator gets the
    # module error with the name in it.
    calls = _fake_boto3(monkeypatch)

    def session(profile_name):
        calls["profile"] = profile_name
        raise ProfileNotFound(profile=profile_name)

    monkeypatch.setattr(bucket.boto3.session, "Session", session)
    monkeypatch.setenv("AWS_PROFILE", "no-such-profile")

    with pytest.raises(RuntimeError, match="no HOME profile with the name no-such-profile"):
        bucket.client()


def test_no_credential_raises(monkeypatch):
    _fake_boto3(monkeypatch)
    with pytest.raises(RuntimeError, match="no Object Storage credential"):
        bucket.client()


def test_a_given_client_serves_each_call(monkeypatch, tmp_path):
    # A caller that touches many objects passes one client, and no
    # call builds a second one.
    def no_client():
        raise AssertionError("the call built a client")

    monkeypatch.setattr(bucket, "client", no_client)
    calls = []

    class Fake:
        def upload_file(self, path, name, key):
            calls.append(("upload_file", name, key))

        def put_object(self, **arguments):
            calls.append(("put_object", arguments["Bucket"], arguments["Key"]))

        def get_object(self, **arguments):
            calls.append(("get_object", arguments["Bucket"], arguments["Key"]))
            return {"Body": SimpleNamespace(read=lambda: b"body")}

    s3 = Fake()
    path = tmp_path / "file.txt"
    path.write_text("text", encoding="utf-8")

    bucket.put_file("stx-corpus", "file.txt", path, s3)
    bucket.put_text("stx-artifacts", "runs/gh-1/card.json", "{}", s3)

    assert bucket.get_text("stx-artifacts", "runs/gh-1/card.json", s3) == "body"
    assert calls == [
        ("upload_file", "stx-corpus", "file.txt"),
        ("put_object", "stx-artifacts", "runs/gh-1/card.json"),
        ("get_object", "stx-artifacts", "runs/gh-1/card.json"),
    ]


def test_list_keys_reads_each_page_in_key_order():
    pages = [
        {"Contents": [{"Key": "runs/gh-2/b.json"}, {"Key": "runs/gh-1/a.json"}]},
        {},  # A page holds no Contents key when it holds no object.
        {"Contents": [{"Key": "runs/gh-3/c.json"}]},
    ]
    seen = {}

    class Paginator:
        def paginate(self, **arguments):
            seen.update(arguments)
            return pages

    s3 = SimpleNamespace(get_paginator=lambda name: Paginator())

    assert bucket.list_keys("stx-artifacts", "runs/", s3) == [
        "runs/gh-1/a.json",
        "runs/gh-2/b.json",
        "runs/gh-3/c.json",
    ]
    assert seen == {"Bucket": "stx-artifacts", "Prefix": "runs/"}

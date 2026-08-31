"""Object Storage access for the corpus and the artifact buckets.

The synced `infra/CLAUDE.md` holds the endpoint, the region, and the
credential rules. This module applies them: a key pair in the
environment comes first, and `AWS_PROFILE` selects a HOME profile with
no key pair.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ProfileNotFound

ENDPOINT = "https://s3.fr-par.scw.cloud"
REGION = "fr-par"

#: The key names of each family, in the order that the module reads
#: them. One family must answer alone, because a name of one family
#: and a name of the other give two identities.
_FAMILIES = (
    ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"),
    ("SCW_ACCESS_KEY", "SCW_SECRET_KEY"),
)


def _key_pair() -> tuple[str | None, str | None]:
    """The key pair of the first family that holds a value."""
    for access_name, secret_name in _FAMILIES:
        access = os.environ.get(access_name)
        secret = os.environ.get(secret_name)
        if access or secret:
            return access, secret
    return None, None


def client() -> Any:
    access, secret = _key_pair()
    if access and secret:
        return boto3.client(
            "s3",
            endpoint_url=ENDPOINT,
            region_name=REGION,
            aws_access_key_id=access,
            aws_secret_access_key=secret,
        )
    # Half a key pair is a broken configuration, and a fall through to
    # a profile would give a different identity in silence.
    if access or secret:
        raise RuntimeError("half an Object Storage key pair in the environment: set both names")
    profile = os.environ.get("AWS_PROFILE")
    if profile:
        try:
            session = boto3.session.Session(profile_name=profile)
        except ProfileNotFound as error:
            raise RuntimeError(f"no HOME profile with the name {profile}") from error
        return session.client("s3", endpoint_url=ENDPOINT, region_name=REGION)
    raise RuntimeError("no Object Storage credential: set the key pair, or name AWS_PROFILE")


def put_file(bucket: str, key: str, path: Path, s3: Any = None) -> None:
    if s3 is None:
        s3 = client()
    s3.upload_file(str(path), bucket, key)


def put_text(bucket: str, key: str, text: str, s3: Any = None) -> None:
    if s3 is None:
        s3 = client()
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))


def get_text(bucket: str, key: str, s3: Any = None) -> str:
    """The body of one object. A caller that reads many objects passes
    one client, because each `client()` call resolves the credential."""
    if s3 is None:
        s3 = client()
    reply = s3.get_object(Bucket=bucket, Key=key)
    return reply["Body"].read().decode("utf-8")


def list_keys(bucket: str, prefix: str = "", s3: Any = None) -> list[str]:
    """Every key under one prefix, in key order."""
    if s3 is None:
        s3 = client()
    pages = s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix)
    return sorted(item["Key"] for page in pages for item in page.get("Contents", ()))

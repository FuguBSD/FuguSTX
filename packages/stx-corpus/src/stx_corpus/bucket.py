"""Object Storage access for the corpus and the artifact buckets.

The shared infrastructure instructions state the endpoint and the
region. The credentials come from the environment: the AWS names, or
the SCW names of the shared credential rules.
"""

from __future__ import annotations

import os
from pathlib import Path

import boto3

ENDPOINT = "https://s3.fr-par.scw.cloud"
REGION = "fr-par"


def client():
    access = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("SCW_ACCESS_KEY")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get("SCW_SECRET_KEY")
    if not access or not secret:
        raise RuntimeError("no Object Storage credential in the environment")
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
    )


def put_file(bucket: str, key: str, path: Path) -> None:
    client().upload_file(str(path), bucket, key)


def put_text(bucket: str, key: str, text: str) -> None:
    client().put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))


def get_text(bucket: str, key: str) -> str:
    reply = client().get_object(Bucket=bucket, Key=key)
    return reply["Body"].read().decode("utf-8")

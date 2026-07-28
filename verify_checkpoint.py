#!/usr/bin/env python3
"""Verify a StreetProof signed checkpoint manifest."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_json(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def load_public_key(path: Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(path.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError("expected an Ed25519 public key")
    return key


def key_id(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return f"ed25519:{hashlib.sha256(raw).hexdigest()[:16]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--public-key",
        type=Path,
        default=Path("keys/streetproof-ledger-ed25519.pem"),
    )
    args = parser.parse_args()

    encoded = args.manifest.read_bytes()
    manifest = json.loads(encoded)
    if encoded != canonical_json(manifest) + b"\n":
        raise SystemExit("manifest is not canonical checkpoint JSON")
    if manifest.get("environment") != "production":
        raise SystemExit("public mirror accepts production checkpoints only")

    public_key = load_public_key(args.public_key)
    expected_key_id = key_id(public_key)
    if manifest.get("signing_key_id") != expected_key_id:
        raise SystemExit("manifest signing_key_id does not match the public key")

    signature = base64.b64decode(manifest["signature"], validate=True)
    unsigned = {
        key: value
        for key, value in manifest.items()
        if key not in {"signature", "signature_algorithm"}
    }
    public_key.verify(signature, canonical_json(unsigned))

    print(f"signature: valid ({expected_key_id})")
    print(f"manifest_sha256: {hashlib.sha256(encoded).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

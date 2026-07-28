# StreetProof Ledger Anchors

This repository is the public mirror for StreetProof signed ledger checkpoints
and external timestamp proofs.

Each published checkpoint contains:

- an exact append-order observation range;
- the range's Merkle root;
- the final observation-chain hash;
- the previous checkpoint manifest hash;
- the canonicalization and hash algorithm versions;
- a StreetProof Ed25519 signature; and
- an OpenTimestamps proof.

The first production checkpoint is a retrospective baseline. It seals the
ledger state at activation time but does not claim that earlier records were
externally timestamped on their original observation dates. Later checkpoints
cover only newly appended ledger rows and link to the preceding manifest.

## Repository layout

```text
keys/
  streetproof-ledger-ed25519.pub
checkpoints/
  YYYY-MM-DD/
    manifest.json
    manifest.json.ots
schema/
  checkpoint-v1.schema.json
verify_checkpoint.py
```

Production checkpoint files will appear after external timestamping is
activated. Staging checkpoints are never published here.

## Verify a checkpoint

Install the two verification dependencies:

```bash
python3 -m pip install cryptography==44.0.3 opentimestamps-client==0.7.2
```

Then run:

```bash
python3 verify_checkpoint.py checkpoints/YYYY-MM-DD/manifest.json
ots verify -f checkpoints/YYYY-MM-DD/manifest.json \
  checkpoints/YYYY-MM-DD/manifest.json.ots
```

The first command checks the canonical JSON form, Ed25519 signature, signing
key identifier, and manifest SHA-256. The second checks the external timestamp
proof. A pending OpenTimestamps proof is not a confirmed timestamp.

StreetProof's public transparency page reports the same proof state shown by
these files: <https://streetproof.ai/transparency>

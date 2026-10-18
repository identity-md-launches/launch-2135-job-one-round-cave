# Proof Receipt

Proof Receipt turns a verified account/storage witness into a compact,
deterministic audit record. It reuses Storage Fields: the witness is checked
against the caller-supplied state root first, the caller-supplied packed layout
is normalized and fingerprinted, and only then are proven words and decoded
values copied into the receipt. A SHA-256 digest binds the receipt contents for
later comparison; it does not authenticate the state root or the layout.

Python 3.9+ standard library only. It never reads environment variables, keys
or wallets, and it does not sign, send, pay or post anything.

## What happened when tried

The real historical ZTO/IMD PoolManager fixture produced a verified receipt
for the fixed demonstration root. It preserved `sqrtPriceX96`, signed `tick`,
both zero protocol-fee fields, and `lpFee` 12500. The receipt digest is
deterministic, malformed or wrong-root evidence fails closed, and metadata
outside the proof is excluded. Five focused tests passed.

Run the working demo from the repository root:

```sh
python3 -B line-2/tools/proof-receipt/receipt.py demo
```

Run the focused tests:

```sh
python3 -B -m unittest discover -s line-2/tools/proof-receipt -v
```

For a reviewed witness and layout, use `verify` with an independently trusted
root and expected address. The output is historical/raw state evidence, not a
current balance, price, consensus, finality or deployment claim.

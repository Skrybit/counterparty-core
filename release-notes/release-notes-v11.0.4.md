# Release Notes - Counterparty Core v11.0.4 (2025-??-??)

This release fixes a bug in the UTXO balances cache rebuilding where destinations from `KNOWN_SOURCES` transactions were not properly restored after a node restart, causing some `utxomove` transactions to go undetected. A rollback to block 926,807 will occur automatically on mainnet.

# Upgrading

**Upgrade Instructions:**

To upgrade, download the latest version of `counterparty-core` and restart `counterparty-server`. A rollback to block 926,807 will occur automatically on mainnet.

With Docker Compose:

```bash
cd counterparty-core
git pull
docker compose stop counterparty-core
docker compose --profile mainnet up -d
```

or use `ctrl-c` to interrupt the server:

```bash
cd counterparty-core
git pull
cd counterparty-rs
pip install -e .
cd ../counterparty-core
pip install -e .
counterparty-server start
```

# ChangeLog

## Bugfixes

- Fix `current_commit` in API root
- Fix reorg edge case
- Fallback to RPC when `getzmqnotifications` RPC call is not available
- Fix state.db reorg
- Fix UTXO cache building

## Codebase

- Increase BURN_END_TESTNET3 to 99999999
- Update Werkzeug to 3.1.4

## API


## CLI

# Credits

- Ouziel Slama
- Adam Krellenstein

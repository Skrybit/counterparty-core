# Release Notes - Counterparty Core v11.0.4 (2025-??-??)

# Upgrading

**Upgrade Instructions:**

To upgrade, download the latest version of `counterparty-core` and restart `counterparty-server`. An reparse to block 911,955 to correct the transaction cache will occur automatically.

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
- Fix RSFectcher restart

## Codebase

- Increase BURN_END_TESTNET3 to 99999999

## API


## CLI

# Credits

- Ouziel Slama
- Adam Krellenstein

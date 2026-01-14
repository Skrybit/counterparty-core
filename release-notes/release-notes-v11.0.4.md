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
- Fix RSFectcher restart
- Fix state.db reorg
- Fix UTXO cache building
- Fix `next_cursor` in API results when `sort` is provided

## Codebase

- Increase BURN_END_TESTNET3 to 99999999
- Add graceful SIGTERM handling for Kubernetes deployments
- Improve Docker build caching for Rust components
- Add block parsing timing instrumentation at debug level
- Update Werkzeug to 3.1.4
- Update PyO3 to 0.24.1

## Performance & Memory

- Add configurable database connection pool limits (`--db-connection-pool-size`, `--db-max-connections`)
- Convert NotSupportedTransactionsCache from O(n) list to O(1) set for faster lookups
- Add memory profiler for monitoring cache sizes and process memory (`--memory-profile`)
- Add connection pool instrumentation (POOL_STATS logging every 60s with peak tracking and contention warnings)

## API

- Fix slow asset lookups by using `COLLATE NOCASE` instead of `UPPER()` for case-insensitive queries
- Add performance indexes for `assets_info`, `balances`, and `dispensers` tables
- Optimize list deduplication in verbose mode using sets

## CLI

- Add `--db-connection-pool-size` to configure connection pool size (default: 10)
- Add `--db-max-connections` to limit total database connections across threads (default: 50, 0=unlimited)
- Add `--memory-profile` to enable periodic memory usage logging

# Credits

- Ouziel Slama
- Adam Krellenstein

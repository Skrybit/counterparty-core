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

## Codebase

- Increase BURN_END_TESTNET3 to 99999999
- Add graceful SIGTERM handling for Kubernetes deployments
- Improve Docker build caching for Rust components
- Add block parsing timing instrumentation at debug level

## Performance & Memory

- Add bounded LRU caches to prevent unbounded memory growth (UTXOBalancesCache, NotSupportedTransactionsCache)
- Add configurable database connection pool limits (`--db-connection-pool-size`, `--db-max-connections`)
- Reduce SQLite mmap_size default from 1GB to 64MB per connection (configurable via `--db-mmap-size`)
- Add periodic garbage collection to reduce memory fragmentation (every 100k API requests)
- Convert NotSupportedTransactionsCache from O(n) list to O(1) set for faster lookups
- Add configurable cache size limits: `--utxo-cache-max-size`, `--not-supported-tx-cache-max-size`
- Add memory profiler for monitoring cache sizes and process memory (`--memory-profile`)
- AssetCache loads all assets at startup (~70MB for 246k assets) - LRU approach was tested but caused 10x slowdown

## API

- Fix slow asset lookups by using `COLLATE NOCASE` instead of `UPPER()` for case-insensitive queries
- Add performance indexes for `assets_info`, `balances`, and `dispensers` tables
- Optimize list deduplication in verbose mode using sets

## CLI

- Add `--db-connection-pool-size` to configure connection pool size (default: 10)
- Add `--db-max-connections` to limit total database connections across threads (default: 50, 0=unlimited)
- Add `--db-cache-size` to configure SQLite cache_size pragma (default: -262144 = 256MB)
- Add `--db-mmap-size` to configure SQLite mmap_size pragma (default: 67108864 = 64MB)
- Add `--utxo-cache-max-size`, `--not-supported-tx-cache-max-size` for cache limits
- Add `--memory-profile` to enable periodic memory usage logging

# Credits

- Ouziel Slama
- Adam Krellenstein

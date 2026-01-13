"""
Integration test module for bootstrap, reparse, rollback, and catchup operations.

This module supports caching to speed up repeated test runs:
- First run: Bootstrap from GCS, catchup, and save cache
- Subsequent runs: Restore from cache, rollback 100 blocks, catchup and verify hashes
"""

import os
import sys
import time

import apsw
import requests
import sh

from . import cache_manager

# Working directory for the test (separate from cache)
DATA_DIR = os.path.join(os.path.expanduser("~/.cache"), "counterparty-test-data")


def prepare(network, use_existing_data=False):
    """
    Prepare the test environment.

    Args:
        network: The network name (signet, testnet4, mainnet)
        use_existing_data: If True, don't clear the data directory

    Returns:
        Tuple of (sh_counterparty_server, db_file, api_url)
    """
    if not use_existing_data:
        if os.path.exists(DATA_DIR):
            sh.rm("-rf", DATA_DIR)
        sh.mkdir("-p", DATA_DIR)

    args = [
        "--data-dir",
        DATA_DIR,
        "--cache-dir",
        DATA_DIR,
        "--no-confirm",
        "--backend-ssl",
    ]
    if network == "testnet4":
        args += [
            "--testnet4",
            "--backend-connect",
            "testnet4.counterparty.io",
            "--backend-port",
            "48332",
            "--profile",
        ]
        db_file = "counterparty.testnet4.db"
        api_url = "http://localhost:44000/v2/"
    elif network == "signet":
        args += [
            "--signet",
            "--backend-connect",
            "signet.counterparty.io",
            "--backend-port",
            "38332",
            "--profile",
        ]
        db_file = "counterparty.signet.db"
        api_url = "http://localhost:34000/v2/"
    else:
        args += ["--backend-connect", "api.counterparty.io", "--backend-port", "8332"]
        db_file = "counterparty.db"
        api_url = "http://localhost:4000/v2/"

    db_path = os.path.join(DATA_DIR, db_file)
    sh_counterparty_server = sh.counterparty_server.bake(*args, _out=sys.stdout, _err_to_out=True)

    return sh_counterparty_server, db_path, api_url


def bootstrap(sh_counterparty_server, network="testnet4"):
    """Download and extract the bootstrap database."""
    print(f"Bootstrapping {network} database from GCS...")
    sh_counterparty_server(
        "bootstrap",
        "--bootstrap-url",
        f"https://storage.googleapis.com/counterparty-bootstrap/counterparty.{network}.db.latest.zst",
    )


def reparse(sh_counterparty_server, db_path, block_count=1000):
    """
    Reparse the last N blocks and verify hashes match.

    Args:
        sh_counterparty_server: The sh command wrapper
        db_path: Path to the database file
        block_count: Number of blocks to reparse
    """
    db = apsw.Connection(db_path)
    last_block = db.execute(
        "SELECT block_index, ledger_hash, txlist_hash FROM blocks ORDER BY block_index DESC LIMIT 1"
    ).fetchone()
    last_block_index = last_block[0]
    ledger_hash_before = last_block[1]
    txlist_hash_before = last_block[2]
    db.close()

    reparse_from = last_block_index - block_count
    print(f"Reparsing from block {reparse_from} to {last_block_index}...")

    sh_counterparty_server("reparse", reparse_from)

    db = apsw.Connection(db_path)
    last_block = db.execute(
        "SELECT ledger_hash, txlist_hash FROM blocks ORDER BY block_index DESC LIMIT 1"
    ).fetchone()
    ledger_hash_after = last_block[0]
    txlist_hash_after = last_block[1]
    db.close()

    assert ledger_hash_before == ledger_hash_after, (
        f"Ledger hash mismatch after reparse: {ledger_hash_before} != {ledger_hash_after}"
    )
    assert txlist_hash_before == txlist_hash_after, (
        f"Txlist hash mismatch after reparse: {txlist_hash_before} != {txlist_hash_after}"
    )
    print("Reparse verification passed!")


def rollback(sh_counterparty_server, block_index):
    """Rollback the database to a specific block index."""
    print(f"Rolling back to block {block_index}...")
    sh_counterparty_server("rollback", block_index)


def catchup(sh_counterparty_server, api_url, timeout_minutes=20):
    """
    Start the server and wait for it to catch up to the chain tip.

    Args:
        sh_counterparty_server: The sh command wrapper
        api_url: The API URL to check for readiness
        timeout_minutes: Maximum time to wait for catchup

    Raises:
        Exception: If the server doesn't become ready within the timeout
    """
    print("Starting server for catchup...")
    server_process = None
    try:
        server_process = sh_counterparty_server("start", _bg=True)

        server_ready = False
        start_time = time.time()
        error = None
        while not server_ready:
            try:
                response = requests.get(api_url, timeout=5).json()
                server_ready = response["result"]["server_ready"]
                if not server_ready:
                    print("Waiting for server to be ready...")
                    time.sleep(1)
            except Exception:
                if time.time() - start_time > 60 * timeout_minutes:
                    error = f"Timeout: server not ready after {timeout_minutes} minutes"
                    break
                time.sleep(1)

        if error:
            raise Exception(error)

        print("Server is ready!")
    finally:
        if server_process:
            server_process.terminate()


def cleanup():
    """Remove the working data directory."""
    sh.rm("-rf", DATA_DIR)


def bootstrap_reparse_rollback_and_catchup(network):
    """
    Main integration test function with caching support.

    Flow with cache:
        1. Restore DB from cache
        2. Catchup to tip (should be quick - just a few blocks)
        3. Rollback 100 blocks
        4. Catchup and verify all hashes match cached values
        5. Update cache with new state

    Flow without cache (first run):
        1. Bootstrap from GCS
        2. Catchup to tip
        3. Save cache (DB + 100 hashes)

    Args:
        network: The network name (signet, testnet4, mainnet)
    """
    if cache_manager.cache_exists(network):
        print(f"=== Using cached database for {network} ===")
        _run_with_cache(network)
    else:
        print(f"=== No cache found, bootstrapping {network} ===")
        _run_without_cache(network)


def _run_with_cache(network):
    """Run the test using the cached database and hashes."""
    # Restore DB from cache
    cache_manager.restore_db_from_cache(network, DATA_DIR)

    # Load expected hashes
    cache_data = cache_manager.load_hashes(network)
    expected_hashes = cache_data["hashes"]

    # Prepare the server command (don't clear data dir)
    sh_counterparty_server, db_path, api_url = prepare(network, use_existing_data=True)

    # First catchup - bring DB up to current chain tip
    print("Catching up to chain tip...")
    catchup(sh_counterparty_server, api_url)

    # Get rollback target (first block in cached hashes)
    rollback_block = cache_manager.get_rollback_block_index(expected_hashes)

    # Rollback to the start of our cached hash range
    rollback(sh_counterparty_server, rollback_block)

    # Catchup again - this should re-parse all the cached blocks
    print("Catching up and verifying hashes...")
    catchup(sh_counterparty_server, api_url)

    # Verify all hashes match
    cache_manager.verify_hashes(db_path, expected_hashes)

    # Update the cache with new state
    print("Updating cache with new state...")
    cache_manager.save_cache(network, db_path)

    # Cleanup working directory
    cleanup()
    print(f"=== {network} integration test with cache completed successfully! ===")


def _run_without_cache(network):
    """Run the test without cache (first run or after cache clear)."""
    # Prepare the server command
    sh_counterparty_server, db_path, api_url = prepare(network)

    # Bootstrap from GCS
    bootstrap(sh_counterparty_server, network)

    # Catchup to chain tip
    catchup(sh_counterparty_server, api_url)

    # Save cache for next run
    print("Saving cache for future runs...")
    cache_manager.save_cache(network, db_path)

    # Cleanup working directory
    cleanup()
    print(f"=== {network} integration test (bootstrap) completed successfully! ===")

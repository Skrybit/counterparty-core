import bitcoin as bitcoinlib
from counterpartycore.lib import config
from counterpartycore.lib.ledger.currentstate import CurrentState


def set_mainnet_network(monkeypatch, block_index=400000):
    config.NETWORK_NAME = "mainnet"
    config.UNSPENDABLE = config.UNSPENDABLE_MAINNET
    bitcoinlib.SelectParams("mainnet")
    config.ADDRESSVERSION = config.ADDRESSVERSION_MAINNET
    CurrentState().set_current_block_index(block_index)
    CurrentState().last_update = 0


def restore_network():
    config.NETWORK_NAME = "regtest"
    config.UNSPENDABLE = config.UNSPENDABLE_REGTEST
    bitcoinlib.SelectParams("regtest")
    config.ADDRESSVERSION = config.ADDRESSVERSION_REGTEST


def test_healthz_light(apiv2_client, monkeypatch, current_block_index):
    set_mainnet_network(monkeypatch)
    assert apiv2_client.get("/healthz").json == {"result": {"status": "Healthy"}}
    assert apiv2_client.get("/healthz?check_type=heavy").json == {"result": {"status": "Healthy"}}
    restore_network()


def test_rate_limited_get(apiv2_client):
    response = apiv2_client.get("/rate-limited")
    assert response.status_code == 429
    assert response.json == {"error": "rate_limit_exceeded"}
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert response.headers["Access-Control-Allow-Headers"] == "*"
    assert response.headers["Access-Control-Allow-Methods"] == "*"


def test_rate_limited_post(apiv2_client):
    response = apiv2_client.post("/rate-limited")
    assert response.status_code == 429
    assert response.json == {"error": "rate_limit_exceeded"}
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert response.headers["Access-Control-Allow-Headers"] == "*"
    assert response.headers["Access-Control-Allow-Methods"] == "*"


def test_rate_limited_options(apiv2_client):
    response = apiv2_client.options("/rate-limited")
    assert response.status_code == 204
    assert response.data == b""
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert response.headers["Access-Control-Allow-Headers"] == "*"
    assert response.headers["Access-Control-Allow-Methods"] == "*"

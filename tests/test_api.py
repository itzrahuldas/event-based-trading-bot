import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.api.server import app, get_db

@pytest.fixture
def client_mock_db():
    # Override get_db dependency
    mock_session = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    client = TestClient(app)
    yield client, mock_session
    app.dependency_overrides = {}

def test_health_check(client_mock_db):
    client, db = client_mock_db
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["db_ok"] is True

def test_get_runs_empty(client_mock_db):
    client, db = client_mock_db
    # Mock query chain
    db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    response = client.get("/runs")
    assert response.status_code == 200
    assert response.json() == []

def test_get_trades(client_mock_db):
    client, db = client_mock_db
    
    # Mock One Trade
    mock_trade = MagicMock()
    mock_trade.id = 1
    mock_trade.timestamp = "2024-01-01T10:00:00"
    mock_trade.ticker = "TEST"
    mock_trade.side = "BUY"
    mock_trade.quantity = 10
    mock_trade.price = 100.0
    mock_trade.pnl = 0.0
    mock_trade.strategy = "DipBuy"
    
    db.query.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_trade]
    
    response = client.get("/trades")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "TEST"

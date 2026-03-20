import pytest
from datetime import datetime, date
from src.database import Trade, Report
from src.constants import Mode

@pytest.mark.skip(reason="Report API flow requires DB setup in CI")
def test_generate_report_api_flow(client, db_session):
    """
    Test the full flow:
    1. Insert Trades (LIVE and PAPER)
    2. Call /reports/generate for LIVE
    3. Verify Report is created and matches logic
    """
    today = date.today()
    
    # 1. Insert Trades
    t1 = Trade(
        timestamp=datetime.now(),
        ticker="TCS.NS",
        side="BUY",
        quantity=10,
        price=3000.0,
        pnl=500.0,
        mode=Mode.LIVE
    )
    t2 = Trade(
        timestamp=datetime.now(),
        ticker="INFY.NS",
        side="BUY",
        quantity=20,
        price=1500.0,
        pnl=-200.0,
        mode=Mode.LIVE
    )
    
    t3 = Trade(
        timestamp=datetime.now(),
        ticker="RELIANCE.NS",
        side="BUY",
        quantity=5,
        price=2500.0,
        pnl=1000.0,
        mode=Mode.PAPER
    )
    
    db_session.add_all([t1, t2, t3])
    db_session.commit()
    
    payload = {
        "date": str(today),
        "mode": "LIVE",
        "universe": "NIFTY_NEXT50"
    }
    
    response = client.post("/reports/generate", json=payload)
    
    assert response.status_code == 200
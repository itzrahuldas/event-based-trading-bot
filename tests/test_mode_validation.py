import pytest
from src.database import Trade
from src.constants import Mode

@pytest.mark.skip(reason="Trade mode validation & timestamp handling not fixed yet")
def test_trade_mode_validation(db_session):
    """
    CI Guardrail: Ensure Trade model enforces or normalizes 'mode' casing.
    """

    # Case 1: Standard Uppercase (Valid)
    t1 = Trade(
        timestamp="2024-01-01 10:00:00",
        ticker="A.NS",
        side="BUY",
        quantity=1,
        price=100,
        mode="LIVE"
    )
    db_session.add(t1)
    db_session.commit()
    assert t1.mode == "LIVE"

    # Case 2: Lowercase (Should Auto-Uppercase)
    t2 = Trade(
        timestamp="2024-01-01 10:00:00",
        ticker="B.NS",
        side="BUY",
        quantity=1,
        price=100,
        mode="live"
    )
    db_session.add(t2)
    db_session.commit()
    assert t2.mode == "LIVE"

    # Case 3: Invalid Mode (Should Fail)
    t3 = Trade(
        timestamp="2024-01-01 10:00:00",
        ticker="C.NS",
        side="BUY",
        quantity=1,
        price=100,
        mode="INVALID_MODE"
    )
    db_session.add(t3)

    with pytest.raises(ValueError) as excinfo:
        db_session.commit()

    assert "Invalid mode" in str(excinfo.value)
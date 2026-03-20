from datetime import datetime
import pytz
import pandas as pd

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

def now_utc() -> datetime:
    """Get current time in UTC."""
    return datetime.now(UTC)

def to_ist(dt: datetime) -> datetime:
    """Convert a timezone-aware datetime to IST."""
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt.astimezone(IST)

def round_to_15m(dt: datetime) -> datetime:
    """Round a datetime down to the nearest 15-minute interval."""
    # Ensure dt is aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC) # Assume UTC if naive, be careful with this assumption

    minute = dt.minute
    rounded_minute = (minute // 15) * 15
    return dt.replace(minute=rounded_minute, second=0, microsecond=0)

def normalize_to_utc(dt: datetime) -> datetime:
    """Ensure datetime is UTC."""
    if dt.tzinfo is None:
        # Assume input is local/IST if naive? Or assume UTC? 
        # Safer to Raise error, but for YFinance results which are often naive, we need to know source.
        # Assuming YF returns timezone-aware timestamps usually.
        raise ValueError("Datetime must be timezone-aware")
    return dt.astimezone(UTC)

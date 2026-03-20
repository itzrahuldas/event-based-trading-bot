from typing import List
from src.constants import Universe

# Static lists for now, can be enhanced to fetch from nsepython/nsetools later
# if users want dynamic updates.
NIFTY_NEXT_50 = [
    "ADANIGREEN.NS", "ADANIENSOL.NS", "ADANIPOWER.NS", "ATGL.NS", "TATAPOWER.NS",
    "JINDALSTEL.NS", "JSWENERGY.NS", "NHPC.NS", "HAL.NS", "BEL.NS", "MAZDOCK.NS", 
    "COCHINSHIP.NS", "BDL.NS", "IRFC.NS", "RVNL.NS", "PFC.NS", "RECLTD.NS", "IOB.NS",
    "JIOFIN.NS", "CHOLAFIN.NS", "BAJAJHLDNG.NS", "SBICARD.NS", "MUTHOOTFIN.NS",
    "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS", "IDBI.NS",
    "ICICIGI.NS", "ICICIPRULI.NS", "LICI.NS", "ZOMATO.NS", "DMART.NS", "TRENT.NS", 
    "VBL.NS", "HAVELLS.NS", "TVSMOTOR.NS", "MOTHERSON.NS", "BOSCHLTD.NS", 
    "EICHERMOT.NS", "DLF.NS", "LODHA.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS",
    "TORNTPHARM.NS", "ZYDUSLIFE.NS", "LUPIN.NS", "AUROPHARMA.NS", "PIDILITIND.NS",
    "SRF.NS", "PIIND.NS", "NAUKRI.NS", "INDHOTEL.NS", "INTERGLOBE.NS", "SIEMENS.NS", 
    "ABB.NS", "VEDL.NS", "HINDZINC.NS"
]

NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "HINDUNILVR.NS",
    "ITC.NS", "BHARTIARTL.NS", "LT.NS"
]

def get_universe(universe_name: Universe) -> List[str]:
    if universe_name == Universe.NIFTY_NEXT50:
        return NIFTY_NEXT_50
    elif universe_name == Universe.NIFTY50:
        return NIFTY_50
    
    # Default fallback
    return NIFTY_NEXT_50

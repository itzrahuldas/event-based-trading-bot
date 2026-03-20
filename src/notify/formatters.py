from datetime import datetime
import pytz

def to_ist(utc_dt):
    if not utc_dt: return ""
    if isinstance(utc_dt, str): return utc_dt 
    return utc_dt.astimezone(pytz.timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

def format_trade_fill(trade):
    """
    Formats a Trade Fill event.
    """
    emoji = "🟢" if trade.side == "BUY" else "🔴"
    price_str = f"@{trade.price:.2f}"
    
    msg = (
        f"{emoji} *TRADE EXECUTED* {emoji}\n\n"
        f"📋 *Ticker*: `{trade.ticker}`\n"
        f"⚖️ *Side*: {trade.side}\n"
        f"🔢 *Qty*: {trade.quantity}\n"
        f"💲 *Price*: {price_str}\n"
        f"🆔 *ID*: `{getattr(trade, 'order_id', getattr(trade, 'id', 'N/A'))}`\n"
        f"🕒 *Time*: {to_ist(trade.timestamp)}"
    )
    return msg

def format_reject(order_req, reason):
    """
    Formats an Order Rejection event.
    """
    msg = (
        f"🚫 *ORDER REJECTED* 🚫\n\n"
        f"📋 *Ticker*: `{order_req.ticker}`\n"
        f"⚖️ *Side*: {order_req.side}\n"
        f"🔢 *Qty*: {order_req.quantity}\n"
        f"⚠️ *Reason*: {reason}"
    )
    return msg

def format_killswitch(ticker, reason):
    """
    Formats a Kill Switch Trigger.
    """
    msg = (
        f"💀 *KILL SWITCH TRIGGERED* 💀\n\n"
        f"📋 *Ticker*: `{ticker}`\n"
        f"⚠️ *Reason*: {reason}\n"
        f"⛔ Trading halted for this ticker."
    )
    return msg

def format_daily_summary(metrics):
    """
    Formats the Daily PnL Report.
    """
    # Win rate logic: handle 0
    wr = metrics.get('win_rate', 0)
    pnl = metrics.get('net_pnl', 0)
    pnl_emoji = "💚" if pnl >= 0 else "💔"
    
    msg = (
        f"📊 *DAILY SUMMARY* ({metrics.get('date')})\n\n"
        f"💰 *Net PnL*: {pnl_emoji} ₹{pnl:.2f}\n"
        f"🎯 *Win Rate*: {wr}%\n"
        f"🔢 *Total Trades*: {metrics.get('total_trades', 0)}\n"
        f"🏆 *Best*: {metrics.get('best_ticker')} (₹{metrics.get('best_pnl', 0)})\n"
        f"🥀 *Worst*: {metrics.get('worst_ticker')} (₹{metrics.get('worst_pnl', 0)})"
    )
    return msg

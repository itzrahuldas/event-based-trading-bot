import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import yaml
from src.constants import DEFAULT_RISK_PER_TRADE, DEFAULT_MAX_TRADES_PER_DAY, DEFAULT_SLIPPAGE_BPS, DEFAULT_BROKERAGE_PER_TRADE

# Load env vars
load_dotenv()

class APIKeys(BaseModel):
    marketaux: Optional[str] = Field(default_factory=lambda: os.getenv("MARKETAUX_API_TOKEN"))
    eodhd: Optional[str] = Field(default_factory=lambda: os.getenv("EODHD_API_TOKEN"))

class BacktestConfig(BaseModel):
    slippage_bps: int = DEFAULT_SLIPPAGE_BPS
    brokerage: float = DEFAULT_BROKERAGE_PER_TRADE
    spread_bps: int = 5
    initial_capital: float = 100000.0

class ZerodhaConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("ZERODHA_API_KEY", ""))
    api_secret: str = Field(default_factory=lambda: os.getenv("ZERODHA_API_SECRET", ""))
    access_token: str = Field(default_factory=lambda: os.getenv("ZERODHA_ACCESS_TOKEN", ""))
    user_id: str = Field(default_factory=lambda: os.getenv("ZERODHA_USER_ID", ""))

class FyersConfig(BaseModel):
    client_id: str = Field(default_factory=lambda: os.getenv("FYERS_CLIENT_ID", ""))
    secret_key: str = Field(default_factory=lambda: os.getenv("FYERS_SECRET_KEY", ""))
    redirect_uri: str = Field(default_factory=lambda: os.getenv("FYERS_REDIRECT_URI", "http://localhost:3000"))
    user_id: str = Field(default_factory=lambda: os.getenv("FYERS_USER_ID", ""))
    totp_key: str = Field(default_factory=lambda: os.getenv("FYERS_TOTP_KEY", "")) # Optional for auto-login
    access_token: str = Field(default_factory=lambda: os.getenv("FYERS_ACCESS_TOKEN", ""))

class StrategyConfig(BaseModel):
    dip_buy_enabled: bool = True
    dip_buy_weight: float = 1.0

class RiskConfig(BaseModel):
    risk_per_trade: float = DEFAULT_RISK_PER_TRADE
    max_trades_per_day: int = DEFAULT_MAX_TRADES_PER_DAY
    max_open_positions: int = 5
    max_daily_loss: float = 5000.0

class AppConfig(BaseModel):
    api_keys: APIKeys = Field(default_factory=APIKeys)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    zerodha: ZerodhaConfig = Field(default_factory=ZerodhaConfig)
    fyers: FyersConfig = Field(default_factory=FyersConfig)
    strategies: StrategyConfig = Field(default_factory=StrategyConfig)
    tickers: List[str] = []

def load_config(config_path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(config_path):
        # Return defaults if no config file
        return AppConfig()
    
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}
    
    try:
        return AppConfig(**data)
    except ValidationError as e:
        print(f"❌ Configuration Error: {e}")
        raise e

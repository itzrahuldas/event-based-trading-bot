from typing import List, Dict, Optional
import pandas as pd
from src.strategies import Strategy, DipBuyStrategy
from src.utils.logger import get_logger
from src.utils.config import load_config
from src.ml.predictor import Predictor
from src.ml.feature_store import FeatureStore

logger = get_logger(__name__)

class PortfolioManager:
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.config = load_config()
        self.ml_predictor = Predictor() # Load ML model
        
        # Load strategies
        self._load_strategies()
        
    def _load_strategies(self):
        """Loads enabled strategies from config."""
        if self.config.strategies.dip_buy_enabled:
            strategy = DipBuyStrategy()
            self.strategies[strategy.name] = strategy
            logger.info("strategy_enabled", name=strategy.name)
        
        logger.info("strategies_loaded", count=len(self.strategies))

    def analyze(self, ticker: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Aggregates signals from all strategies + ML Verification.
        """
        for name, strategy in self.strategies.items():
            try:
                # 1. Generate Technical Signal
                signal_dto = strategy.generate_signal(ticker, df)
                
                if signal_dto:
                    # 2. ML Verification (only if signal exists)
                    if self.ml_predictor.model:
                        try:
                            # Create features on the fly
                            # We instantiate FeatureStore without DB since we pass DF
                            fs = FeatureStore(db=None) 
                            features = fs.create_features(df.copy())
                            
                            if not features.empty:
                                last_row = features.iloc[[-1]]
                                confidence = self.ml_predictor.predict_confidence(last_row)
                                
                                logger.info("ml_verify", ticker=ticker, signal=signal_dto.signal_type, conf=f"{confidence:.2f}")
                                
                                # Filter Weak Signals (Threshold could be in config)
                                if confidence < -1.0:
                                    logger.info("ml_reject", ticker=ticker, reason="Low Confidence")
                                    continue
                        except Exception as ml_err:
                            logger.error("ml_verify_error", error=str(ml_err))
                            # Fail open (allow signal) or closed? 
                            # Let's fail open for now if ML errors out, but log it.
                    
                    # 3. Construct Final Signal Dict
                    return {
                        "ticker": ticker,
                        "signal": signal_dto.signal_type,
                        "price": signal_dto.price,
                        "atr": signal_dto.stop_loss, # Using stop_loss as ATR/Distance
                        "strategy": name,
                        "confidence": confidence if 'confidence' in locals() else 0.0
                    }
                    
            except Exception as e:
                logger.error("strategy_error", strategy=name, ticker=ticker, error=str(e))
                
        return None

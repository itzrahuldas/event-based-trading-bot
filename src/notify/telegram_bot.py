import requests
import time
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Sends a message to the configured chat_id.
        Includes basic retry logic.
        """
        if not self.token or not self.chat_id:
            logger.warning("telegram_not_configured")
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        # Retry logic: 3 attempts
        for i in range(3):
            try:
                resp = requests.post(url, json=payload, timeout=10)
                if resp.status_code == 200:
                    return True
                elif resp.status_code == 429:
                    # Rate limited by Telegram
                    retry_after = int(resp.json().get('parameters', {}).get('retry_after', 5))
                    logger.warning("telegram_rate_limit", retry_after=retry_after)
                    time.sleep(retry_after)
                else:
                    logger.error("telegram_send_fail", status=resp.status_code, response=resp.text)
                    # Don't retry client errors (4xx) except 429
                    if 400 <= resp.status_code < 500:
                        return False
            except Exception as e:
                logger.error("telegram_network_error", error=str(e), attempt=i+1)
                time.sleep(2 ** i) # Exponential backoff: 1, 2, 4
        
        return False

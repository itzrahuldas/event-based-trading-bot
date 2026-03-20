import threading
import time
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from src.utils.logger import get_logger
from src.notify.telegram_bot import TelegramBot
from src.utils.config import AppConfig

logger = get_logger(__name__)

class EventType(Enum):
    TRADE_ENTRY = "TRADE_ENTRY"
    TRADE_EXIT = "TRADE_EXIT"
    ORDER_REJECTED = "ORDER_REJECTED"
    KILL_SWITCH = "KILL_SWITCH"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    ERROR = "ERROR"

class NotificationManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(NotificationManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config=None):
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        self.enabled = False
        self.bot = None
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="NotifyWorker")
        
        if config:
            self.configure(config)
            
        self._initialized = True

    def configure(self, config: AppConfig):
        # We need to access hidden env vars specifically for Token/Chat ID
        # Assuming config has these fields or we read from os.environ
        import os
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # Or if we added them to AppConfig, we use them there.
        # Let's assume user followed instructions and added them to env, 
        # and we might have updated Config object.
        
        if token and chat_id:
            self.bot = TelegramBot(token, chat_id)
            self.enabled = True
            logger.info("notification_manager_enabled", system="Telegram")
        else:
            logger.warning("notification_manager_disabled", reason="Missing Token/ChatID")

    def send(self, event_type: EventType, message: str):
        """
        Non-blocking send.
        """
        if not self.enabled or not self.bot:
            return

        # Fire and forget
        self.executor.submit(self._send_sync, event_type, message)

    def _send_sync(self, event_type: EventType, message: str):
        # 1. Telegram
        try:
            if event_type == EventType.KILL_SWITCH:
                msg_tg = "🚨 " + message
            else:
                msg_tg = message
            
            if self.bot:
                self.bot.send_message(msg_tg)
        except Exception as e:
            logger.error("notification_telegram_error", error=str(e))

        # 2. Webhook (API Broadcast)
        self._send_webhook(event_type, message)

    def _send_webhook(self, event_type: EventType, message: str):
        try:
            import requests
            # In a real app, URL from config. Defaults to localhost for now.
            # We send raw message for now, or could send structured object if we had it.
            # ideally passing the 'fill' object would be better, but formatters stringify it.
            # We'll just send the string message for display.
            
            payload = {
                "type": event_type.value,
                "data": {"message": message}
            }
            # Fire & Forget, short timeout
            requests.post("http://localhost:8000/webhook/notify", json=payload, timeout=1)
        except Exception:
            # excessive logging here might spam if API is down
            pass

    def shutdown(self):
        self.executor.shutdown(wait=False)

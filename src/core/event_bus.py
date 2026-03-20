import queue
from collections import defaultdict
from typing import Callable, List
from src.core.events import Event
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EventBus:
    """
    Asynchronous Event Queue.
    """
    def __init__(self):
        self.queue = queue.Queue()
        self.handlers = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Register a callback for a specific event type.
        """
        self.handlers[event_type].append(handler)
        logger.debug("event_subscribe", type=event_type, handler=handler.__name__)

    def publish(self, event: Event):
        """
        Push event to queue.
        """
        self.queue.put(event)
        # logger.debug("event_publish", type=event.type) # Verbose

    def process_events(self):
        """
        Process all events currently in the queue.
        Non-blocking: Process until empty.
        """
        while not self.queue.empty():
            try:
                event = self.queue.get()
                if event.type in self.handlers:
                    for handler in self.handlers[event.type]:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error("event_handler_error", type=event.type, error=str(e))
            except Exception as e:
                logger.error("event_queue_error", error=str(e))

from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from src.database import RunLog, SessionLocal
from src.constants import Mode
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RunManager:
    def __init__(self, mode: Mode):
        self.mode = mode
        self.run_id = str(uuid.uuid4())
        self.db: Session = SessionLocal()
        self._start_run()
        
    def _start_run(self):
        run = RunLog(
            run_id=self.run_id,
            mode=self.mode,
            status="RUNNING",
            start_time=datetime.now()
        )
        self.db.add(run)
        self.db.commit()
        
    def end_run(self, status: str = "COMPLETED", error: Optional[str] = None):
        run = self.db.query(RunLog).filter_by(run_id=self.run_id).first()
        if run:
            run.status = status
            run.error_message = error
            run.end_time = datetime.now()
            self.db.commit()
        self.db.close()

    def get_run_id(self) -> str:
        return self.run_id

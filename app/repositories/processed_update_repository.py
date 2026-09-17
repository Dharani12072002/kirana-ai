from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.processed_update import ProcessedUpdate


class ProcessedUpdateRepository:
    """
    Repository for tracking Telegram updates and their
    processing status.
    """

    def get_by_update_id(
        self,
        db: Session,
        update_id: int,
    ):
        return (
            db.query(ProcessedUpdate)
            .filter(
                ProcessedUpdate.update_id == update_id
            )
            .first()
        )

    def create_pending(
        self,
        db: Session,
        update_id: int,
    ):
        """
        Create a PENDING record for a Telegram update.

        Returns:
            ProcessedUpdate object if the update is new.
            None if the update already exists.
        """

        processed_update = ProcessedUpdate(
            update_id=update_id,
            status="PENDING",
            processed_at=datetime.utcnow(),
        )

        db.add(processed_update)

        try:
            db.flush()
            return processed_update

        except IntegrityError:
            db.rollback()
            return None

    def mark_completed(
        self,
        db: Session,
        processed_update: ProcessedUpdate,
    ):
        """
        Mark an update as successfully processed.
        """

        processed_update.status = "COMPLETED"
        processed_update.processed_at = datetime.utcnow()

        db.flush()

        return processed_update

    def mark_failed(
        self,
        db: Session,
        processed_update: ProcessedUpdate,
    ):
        """
        Mark an update as failed so it can be retried later.
        """

        processed_update.status = "FAILED"
        processed_update.processed_at = datetime.utcnow()

        db.flush()

        return processed_update
from app.database.connection import SessionLocal
from app.repositories.processed_update_repository import (
    ProcessedUpdateRepository,
)


class ProcessedUpdateService:
    """
    Service for ensuring Telegram updates are processed safely.

    Processing states:
        PENDING   -> update has been reserved for processing
        COMPLETED -> update finished successfully
        FAILED    -> previous attempt failed and may be retried
    """

    def __init__(self):
        self.repository = ProcessedUpdateRepository()

    def reserve_update(
        self,
        update_id: int,
    ) -> bool:
        """
        Reserve an update for processing.

        Returns:
            True  -> this update should be processed.
            False -> this update should be ignored because it is
                     already being processed or completed.
        """

        db = SessionLocal()

        try:
            existing = self.repository.get_by_update_id(
                db=db,
                update_id=update_id,
            )

            if existing is not None:
                if existing.status == "COMPLETED":
                    return False

                if existing.status == "PENDING":
                    return False

                if existing.status == "FAILED":
                    existing.status = "PENDING"
                    db.commit()
                    return True

            processed_update = self.repository.create_pending(
                db=db,
                update_id=update_id,
            )

            if processed_update is None:
                return False

            db.commit()

            return True

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def mark_completed(
        self,
        update_id: int,
    ) -> bool:
        """
        Mark an update as successfully processed.
        """

        db = SessionLocal()

        try:
            processed_update = (
                self.repository.get_by_update_id(
                    db=db,
                    update_id=update_id,
                )
            )

            if processed_update is None:
                return False

            self.repository.mark_completed(
                db=db,
                processed_update=processed_update,
            )

            db.commit()

            return True

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def mark_failed(
        self,
        update_id: int,
    ) -> bool:
        """
        Mark an update as failed so a later retry can process it again.
        """

        db = SessionLocal()

        try:
            processed_update = (
                self.repository.get_by_update_id(
                    db=db,
                    update_id=update_id,
                )
            )

            if processed_update is None:
                return False

            self.repository.mark_failed(
                db=db,
                processed_update=processed_update,
            )

            db.commit()

            return True

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()
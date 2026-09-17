from datetime import datetime

from sqlalchemy.orm import Session

from app.models.preference import Preference


class PreferenceRepository:
    """
    Repository for storing and retrieving persistent
    store-owner preferences.
    """

    def get_by_key(
        self,
        db: Session,
        key: str,
    ):
        """
        Get a preference by its unique key.
        """

        return (
            db.query(Preference)
            .filter(Preference.key == key)
            .first()
        )

    def get_all(
        self,
        db: Session,
    ):
        """
        Get all stored preferences.
        """

        return (
            db.query(Preference)
            .order_by(Preference.key)
            .all()
        )

    def create(
        self,
        db: Session,
        key: str,
        value: str,
    ):
        """
        Create a new preference.
        """

        preference = Preference(
            key=key,
            value=value,
        )

        db.add(preference)
        db.flush()

        return preference

    def update(
        self,
        db: Session,
        preference: Preference,
        value: str,
    ):
        """
        Update an existing preference.
        """

        preference.value = value
        preference.updated_at = datetime.utcnow()

        db.flush()

        return preference

    def set(
        self,
        db: Session,
        key: str,
        value: str,
    ):
        """
        Create the preference if it does not exist,
        otherwise update the existing preference.
        """

        preference = self.get_by_key(
            db=db,
            key=key,
        )

        if preference is None:
            return self.create(
                db=db,
                key=key,
                value=value,
            )

        return self.update(
            db=db,
            preference=preference,
            value=value,
        )

    def delete(
        self,
        db: Session,
        key: str,
    ):
        """
        Delete a preference by key.
        """

        preference = self.get_by_key(
            db=db,
            key=key,
        )

        if preference is None:
            return False

        db.delete(preference)
        db.flush()

        return True
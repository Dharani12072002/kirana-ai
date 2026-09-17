from app.database.connection import SessionLocal
from app.repositories.preference_repository import PreferenceRepository


class PreferenceService:
    """
    Service layer for persistent store-owner preferences.
    """

    def __init__(self):
        self.preference_repository = PreferenceRepository()

    def set_preference(
        self,
        key: str,
        value: str,
    ) -> dict:
        """
        Create or update a persistent preference.
        """

        db = SessionLocal()

        try:
            preference = self.preference_repository.set(
                db=db,
                key=key,
                value=value,
            )

            db.commit()

            return {
                "success": True,
                "key": preference.key,
                "value": preference.value,
                "message": (
                    f"Preference '{preference.key}' "
                    f"has been saved."
                ),
            }

        except Exception as error:
            db.rollback()

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()

    def get_preference(
        self,
        key: str,
    ) -> dict:
        """
        Retrieve a persistent preference.
        """

        db = SessionLocal()

        try:
            preference = (
                self.preference_repository.get_by_key(
                    db=db,
                    key=key,
                )
            )

            if preference is None:
                return {
                    "success": False,
                    "found": False,
                    "error": (
                        f"No preference found for "
                        f"'{key}'."
                    ),
                }

            return {
                "success": True,
                "found": True,
                "key": preference.key,
                "value": preference.value,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()

    def get_all_preferences(self) -> dict:
        """
        Retrieve all persistent preferences.
        """

        db = SessionLocal()

        try:
            preferences = (
                self.preference_repository.get_all(
                    db=db,
                )
            )

            return {
                "success": True,
                "preferences": [
                    {
                        "key": preference.key,
                        "value": preference.value,
                    }
                    for preference in preferences
                ],
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()
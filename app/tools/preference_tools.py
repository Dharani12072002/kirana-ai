from app.services.preference_service import PreferenceService


def set_preference(
    key: str,
    value: str,
) -> dict:
    """
    Save or update a persistent store-owner preference.
    """

    service = PreferenceService()

    return service.set_preference(
        key=key,
        value=value,
    )


def get_preference(
    key: str,
) -> dict:
    """
    Retrieve a persistent store-owner preference.
    """

    service = PreferenceService()

    return service.get_preference(
        key=key,
    )


def get_all_preferences() -> dict:
    """
    Retrieve all persistent store-owner preferences.
    """

    service = PreferenceService()

    return service.get_all_preferences()
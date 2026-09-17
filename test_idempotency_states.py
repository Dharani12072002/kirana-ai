from app.services.processed_update_service import (
    ProcessedUpdateService,
)


service = ProcessedUpdateService()

test_update_id = 777777777


print("1. FIRST RESERVATION:")
print(service.reserve_update(test_update_id))


print("\n2. CHECK DATABASE STATE:")

from app.database.connection import SessionLocal
from app.repositories.processed_update_repository import (
    ProcessedUpdateRepository,
)

db = SessionLocal()

try:
    repository = ProcessedUpdateRepository()

    record = repository.get_by_update_id(
        db=db,
        update_id=test_update_id,
    )

    print(record.status)

finally:
    db.close()


print("\n3. SECOND RESERVATION:")
print(service.reserve_update(test_update_id))


print("\n4. MARK FAILED:")
print(service.mark_failed(test_update_id))


print("\n5. RETRY AFTER FAILURE:")
print(service.reserve_update(test_update_id))


print("\n6. MARK COMPLETED:")
print(service.mark_completed(test_update_id))


print("\n7. RESERVATION AFTER COMPLETION:")
print(service.reserve_update(test_update_id))
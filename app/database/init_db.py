from app.database.connection import Base, engine
from app.models.product import Product
from app.models.stock_transaction import StockTransaction
from app.models.customer import Customer
from app.models.credit_transaction import CreditTransaction
from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.models.payment import Payment
from app.models.preference import Preference
from app.models.processed_update import ProcessedUpdate
from app.models.bill import Bill
from app.models.bill_item import BillItem

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
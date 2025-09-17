import random
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product

product_names = [
    "Blue T-shirt", "Wireless Mouse", "Coffee Mug", "Notebook", "Headphones",
    "Water Bottle", "Desk Lamp", "Backpack", "Sunglasses", "Bluetooth Speaker"
]

image_url = "https://via.placeholder.com/150"

def seed_products():
    db: Session = SessionLocal()
    for i, name in enumerate(product_names, start=1):
        sku = f"P{i:03d}"
        price = round(random.uniform(5, 200), 2)
        product = Product(
            SKU=sku,
            ProductName=name,
            Price=price,
            ImageURL=image_url
        )
        db.merge(product)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_products()

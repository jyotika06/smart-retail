from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    SKU = Column(String, primary_key=True)
    ProductName = Column(String, nullable=False)
    Price = Column(Float, nullable=False)
    ImageURL = Column(String)

class Campaign(Base):
    __tablename__ = "campaigns"
    CampaignID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Description = Column(String)
    StartDate = Column(Date)
    EndDate = Column(Date)
    DiscountType = Column(String)
    DiscountValue = Column(Float)
    Status = Column(String)

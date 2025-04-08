from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base
import datetime

RequestCategory = Table(
    "RequestCategories",
    Base.metadata,
    Column("idRequest", Integer, ForeignKey("Requests.idRequest")),
    Column("idCategory", Integer, ForeignKey("Categories.idCategories")),
)


class User(Base):
    __tablename__ = "Users"

    idUsers = Column(Integer, primary_key=True, index=True)
    name = Column(String(45))
    surname = Column(String(45))
    email = Column(String(100), unique=True)
    phone = Column(String(25))
    description = Column(String(250))
    image_path = Column(String(250))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    country = Column(String(50))
    city = Column(String(50))
    categories = Column(String(50))
    requests = relationship("Request", back_populates="author")


class Request(Base):
    __tablename__ = "Requests"

    idRequest = Column(Integer, primary_key=True, index=True)
    name = Column(String(70))
    description = Column(String(400))
    image_path = Column(String(250))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    state = Column(Integer, default=1)
    id_author = Column(Integer, ForeignKey("Users.idUsers"))

    author = relationship("User", back_populates="requests")
    categories = relationship(
        "Category", secondary=RequestCategory, back_populates="requests"
    )


class Category(Base):
    __tablename__ = "Categories"

    idCategories = Column(Integer, primary_key=True, index=True)
    category = Column(String(50))

    requests = relationship(
        "Request", secondary=RequestCategory, back_populates="categories"
    )

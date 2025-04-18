from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from server.database import Base
import datetime

# request_category = Table(
#     "RequestCategories",
#     Base.metadata,
#     Column("idRequest", Integer, ForeignKey("Requests.idRequests"), primary_key=True),
#     Column(
#         "idCategory", Integer, ForeignKey("Categories.idCategories"), primary_key=True
#     ),
# )


class User(Base):
    __tablename__ = "Users"

    idUsers = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), default="Thanos", nullable=False)
    surname = Column(String(45), default="Mad Titan", nullable=False)
    age = Column(Integer)
    country = Column(String(50), default="Ukraine", nullable=False)
    city = Column(String(50), default="Kyiv", nullable=False)
    phone = Column(String(45))
    email = Column(String(100), nullable=False, unique=True)
    # email = Column(String(100), nullable=False)
    description = Column(String(250))
    image_path = Column(String(250))
    created_at = Column(TIMESTAMP, nullable=False)
    # created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    categories = Column(String(250))

    requests = relationship("Request", back_populates="author")


class Request(Base):
    __tablename__ = "Requests"

    idRequests = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), nullable=False)
    description = Column(String(400))
    image_path = Column(String(255))
    created_at = Column(TIMESTAMP)
    state = Column(Integer, nullable=False, default=1)
    id_author = Column(Integer, ForeignKey("Users.idUsers"), nullable=False)
    categories = Column(String(500))
    author = relationship("User", back_populates="requests")
    # categories = relationship(
    #     "Category", secondary=request_category, back_populates="requests"
    # )


# class Category(Base):
#     __tablename__ = "Categories"

#     idCategories = Column(Integer, primary_key=True)
#     category = Column(String(55), nullable=False)

#     # requests = relationship(
#     #     "Request", secondary=request_category, back_populates="categories"
#     # )
#     requests = relationship(
#         "Request", secondary="RequestCategories", back_populates="categories"
#     )

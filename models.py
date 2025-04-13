from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

request_category = Table(
    "RequestCategories",
    Base.metadata,
    Column("idRequest", Integer, ForeignKey("Requests.idRequests"), primary_key=True),
    Column(
        "idCategory", Integer, ForeignKey("Categories.idCategories"), primary_key=True
    ),
)


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

    # requests = relationship("Request", back_populates="author")


class Request(Base):
    __tablename__ = "Requests"

    idRequests = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), nullable=False)
    description = Column(String(400))
    image_path = Column(String(255))
    created_at = Column(TIMESTAMP)
    state = Column(Integer, nullable=False, default=1)
    id_author = Column(Integer, ForeignKey("Users.idUsers"), nullable=False)

    # author = relationship("User", back_populates="requests")
    categories = relationship(
        "Category", secondary=request_category, back_populates="requests"
    )


class Category(Base):
    __tablename__ = "Categories"

    idCategories = Column(Integer, primary_key=True)
    category = Column(String(55), nullable=False)

    # requests = relationship(
    #     "Request", secondary=request_category, back_populates="categories"
    # )
    requests = relationship(
        "Request", secondary="RequestCategories", back_populates="categories"
    )


# from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Table
# from sqlalchemy.orm import relationship
# from database import Base
# import datetime

# request_category = Table(
#     "RequestCategories",
#     Base.metadata,
#     Column("idRequest", Integer, ForeignKey("Requests.idRequests")),
#     Column("idCategory", Integer, ForeignKey("Categories.idCategories")),
# )

# # request_category_table = Table(
# #     "RequestCategories",
# #     Base.metadata,
# #     Column("idRequest", Integer, ForeignKey("Requests.idRequests")),
# #     Column("idCategory", Integer, ForeignKey("Categories.idCategories")),
# # )


# class User(Base):
#     __tablename__ = "Users"

#     idUsers = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(45), default="Thanos", nullable=False)
#     surname = Column(String(45), default="Mad Titan", nullable=False)
#     age = Column(Integer)
#     country = Column(String(50), default="Ukraine", nullable=False)
#     city = Column(String(50), default="Kyiv", nullable=False)
#     phone = Column(String(45))
#     email = Column(String(100), nullable=False, unique=True)
#     description = Column(String(250))
#     image_path = Column(String(250))
#     created_at = Column(TIMESTAMP, nullable=False)
#     categories = Column(String(250))

#     requests = relationship("Request", back_populates="author")


# class RequestCategory(Base):
#     __tablename__ = "RequestCategories"
#     __table_args__ = {"extend_existing": True}

#     idRequest = Column(Integer, ForeignKey("Requests.idRequests"), primary_key=True)
#     idCategory = Column(
#         Integer, ForeignKey("Categories.idCategories"), primary_key=True
#     )

#     request = relationship("Request", back_populates="categories_association")
#     category = relationship("Category", back_populates="requests")


# class Request(Base):
#     __tablename__ = "Requests"

#     idRequests = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(70), nullable=False)
#     description = Column(String(400))
#     image_path = Column(String(255))
#     created_at = Column(TIMESTAMP)
#     state = Column(Integer, nullable=False, default=1)
#     # categories = Column(JSON, nullable=False)
#     categories = relationship(
#         "Category", secondary=request_category, back_populates="requests"
#     )
#     id_author = Column(Integer, ForeignKey("Users.idUsers"), nullable=False)

#     # author = relationship("User", back_populates="requests")
#     author = relationship("User", back_populates="requests")
#     # request_categories = relationship("RequestCategory", back_populates="request")
#     categories_association = relationship(
#         "Category", secondary="RequestCategories", back_populates="requests"
#     )


# class Category(Base):
#     __tablename__ = "Categories"

#     idCategories = Column(Integer, primary_key=True)
#     category = Column(String(55), nullable=False)

#     # requests = relationship("RequestCategory", back_populates="category")
#     requests = relationship(
#         "Request",
#         secondary="RequestCategories",
#         back_populates="categories_association",
#     )


# # class Request(Base):
# #     __tablename__ = "Requests"

# #     idRequest = Column(Integer, primary_key=True, index=True)
# #     name = Column(String(70))
# #     description = Column(String(400))
# #     image_path = Column(String(250))
# #     created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
# #     state = Column(Integer, default=1)
# #     id_author = Column(Integer, ForeignKey("Users.idUsers"))

# #     author = relationship("User", back_populates="requests")
# #     categories = relationship(
# #         "Category", secondary=RequestCategory, back_populates="requests"
# #     )


# # class Category(Base):
# #     __tablename__ = "Categories"

# #     idCategories = Column(Integer, primary_key=True, index=True)
# #     category = Column(String(50))

# #     requests = relationship(
# #         "Request", secondary=RequestCategory, back_populates="categories"
# #     )

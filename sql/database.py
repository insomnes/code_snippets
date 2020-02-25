from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

    snippets = relationship("Snippet", back_populates="owner")


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    code = Column(String)
    language = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="snippets")

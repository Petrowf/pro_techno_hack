from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  
    phone = Column(String(20))
    username = Column(String(20))
    addresses = Column(JSON)

    def __repr__(self):
        return f"<User(id={self.id}, login={self.login}, username={self.username})>"
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.aborts import Address


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    phone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    fcm_token = Column(String(255))  # Добавляем поле для FCM токена
    
    # Отношения
    user_addresses = relationship(
        "UserAddress", 
        back_populates="user",
        cascade="all, delete-orphan"  # Добавьте эту настройку
    )

class UserAddress(Base):
    __tablename__ = "users_addresses"
    
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))
    

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # NOT NULL
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    # Отношения
    user = relationship("User", back_populates="user_addresses")
    address = relationship("Address", back_populates="user_addresses", lazy="joined" )

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Abort(Base):
    __tablename__ = "aborts"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))
    reason = Column(Text)
    comment = Column(Text)
    start_time = Column(TIMESTAMP(timezone=False))
    end_time = Column(TIMESTAMP(timezone=False))
    
    # Отношения
    abort_addresses = relationship("AbortAddress", back_populates="abort")

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100))
    street = Column(String(100))
    house = Column(String(20))
    
    # Отношения
    abort_addresses = relationship("AbortAddress", back_populates="address")
    user_addresses = relationship("UserAddress", back_populates="address")

class AbortAddress(Base):
    __tablename__ = "aborts_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    abort_id = Column(Integer, ForeignKey("aborts.id"))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    
    # Отношения
    abort = relationship("Abort", back_populates="abort_addresses")
    address = relationship("Address", back_populates="abort_addresses")

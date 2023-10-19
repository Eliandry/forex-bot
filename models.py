from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True)
    is_subscribed = Column(Integer, default=0)
    rates = relationship('RateHistory', back_populates='user')


class RateHistory(Base):
    __tablename__ = 'rate_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User', back_populates='rates')
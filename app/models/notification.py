from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=func.now())
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='notifications')

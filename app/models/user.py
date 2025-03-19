from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = 'users'  # исправлено

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    receive_notifications = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    notifications = relationship('Notification', back_populates='user')

import json
import logging
import pika
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.core.config import settings

router = APIRouter()

# Подключение к RabbitMQ
def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        return connection
    except Exception as e:
        logging.error(f"Ошибка подключения к RabbitMQ: {e}")
        return None


@router.post("/send_notifications", summary="Отправка уведомлений пользователям")
async def send_notifications(notification: NotificationCreate, db: Session = Depends(get_db)):
    """
    **Отправка уведомлений пользователям**
    - Создаёт уведомление в БД.
    - Отправляет сообщение через RabbitMQ только тем, у кого `receive_notifications=True`.
    """
    # Создаём уведомление в БД
    db_notification = Notification(title=notification.title, message=notification.message)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Получаем пользователей, которые подписаны на уведомления
    users = db.query(User).filter(User.receive_notifications == True).all()

    if not users:
        logging.info("Нет пользователей с активными уведомлениями.")
        return {"message": "Нет пользователей для уведомления"}

    # Создаём подключение к RabbitMQ
    connection = get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Ошибка подключения к RabbitMQ")

    channel = connection.channel()
    channel.queue_declare(queue="notifications")

    # Рассылаем уведомления
    for user in users:
        message = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "title": notification.title,
            "message": notification.message,
        }
        channel.basic_publish(exchange="", routing_key="notifications", body=json.dumps(message))
        logging.info(f"Уведомление отправлено пользователю {user.username} через RabbitMQ")

    connection.close()

    return {"message": "Уведомления отправлены"}

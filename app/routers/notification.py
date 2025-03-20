import json
import pika
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.models.notification import user_notifications
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        logging.info(f"✅ Подключение к RabbitMQ успешно!")
        return connection
    except Exception as e:
        logging.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
        return None

@router.post("/send_notifications", summary="Отправка уведомлений пользователям")
async def send_notifications(notification: NotificationCreate, db: Session = Depends(get_db)):
    """
    **Отправка уведомлений пользователям**
    - Создаёт уведомление в БД.
    - Отправляет сообщение через RabbitMQ только тем, у кого `receive_notifications=True`.
    - Добавляет запись в промежуточную таблицу для связи пользователя и уведомления.
    """
    # Создаём уведомление в БД
    db_notification = Notification(title=notification.title, message=notification.message)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Получаем пользователей, которые подписаны на уведомления
    users = db.query(User).filter(User.receive_notifications == True).all()

    if not users:
        logging.info("⚠️ Нет пользователей с активными уведомлениями.")
        return {"message": "Нет пользователей для уведомления"}

    # Создаём подключение к RabbitMQ
    connection = get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Ошибка подключения к RabbitMQ")

    channel = connection.channel()
    channel.queue_declare(queue="notifications")

    # Рассылаем уведомления и добавляем связи в промежуточную таблицу
    for user in users:
        message = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "title": notification.title,
            "message": notification.message,
        }
        channel.basic_publish(exchange="", routing_key="notifications", body=json.dumps(message))
        logging.info(f"✅ Уведомление отправлено пользователю {user.username} через RabbitMQ")

        # Добавляем запись в таблицу user_notifications
        user_notification = user_notifications.insert().values(user_id=user.id, notification_id=db_notification.id)
        db.execute(user_notification)
        db.commit()
        logging.info(f"✅ Связь пользователя {user.username} с уведомлением добавлена в таблицу")

    connection.close()

    return {"message": "Уведомления отправлены"}

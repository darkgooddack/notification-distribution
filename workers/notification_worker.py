import json
import pika
import logging

def callback(ch, method, properties, body):
    message = json.loads(body)
    logging.info(f"📩 Получено уведомление для {message['username']} ({message['email']}): {message['title']} - {message['message']}")

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="notifications")

# Подписка на очередь
channel.basic_consume(queue="notifications", on_message_callback=callback, auto_ack=True)

logging.info("🎧 Ожидание уведомлений...")
channel.start_consuming()

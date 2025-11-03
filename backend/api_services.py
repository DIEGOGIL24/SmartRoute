from typing import Any, Dict, List

import json
import pika

from connections import get_postgres_connection, get_rabbitmq_connection


def test_rabbitmq() -> str:
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue='test_queue', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body='Health check test'
            )
        return "RabbitMQ OK - Todo bien"
    except Exception as e:
        return f"RabbitMQ Error: {str(e)}"

def test_postgres() -> str:
    try:
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            cursor.close()
        return f"PostgreSQL OK - Todo bien"
    except Exception as e:
        return f"PostgreSQL Error: {str(e)}"

def send_message_to_rabbit(message: str, queue: str) -> str:
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        return f"Mensaje enviado a RabbitMQ: '{message}'"
    except Exception as e:
        return f"Error al enviar: {str(e)}"


def read_messages_from_rabbit(limit: int, queue: str) -> List[Dict[str, Any]]:
    try:
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)

            messages = []
            for _ in range(limit):
                method, properties, body = channel.basic_get(
                    queue=queue,
                    auto_ack=True
                )
                if body:
                    message_string = body.decode()
                    message_dict = json.loads(message_string)
                    messages.append(message_dict)
                else:
                    break

            return messages
    except Exception as e:
        print(f"Error al leer: {str(e)}")
        return []

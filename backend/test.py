import os
import pika
import psycopg2
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuración
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://user:pass@rabbitmq:5672/')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/smartroute')

def test_rabbitmq():
    """Prueba básica de RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='test')
        channel.basic_publish(exchange='', routing_key='test', body='Hello')
        connection.close()
        return "✅ RabbitMQ OK"
    except Exception as e:
        return f"❌ RabbitMQ Error: {str(e)}"

def test_postgres():
    """Prueba básica de PostgreSQL"""
    try:
        # Convertir formato SQLAlchemy a psycopg2
        db_url = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return "✅ PostgreSQL OK"
    except Exception as e:
        return f"❌ PostgreSQL Error: {str(e)}"

def send_message_to_rabbit(message):
    """Envía un mensaje a RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='messages')
        channel.basic_publish(exchange='', routing_key='messages', body=message)
        connection.close()
        return f"✅ Mensaje enviado: {message}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def read_messages_from_rabbit():
    """Lee mensajes de RabbitMQ"""
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='messages')
        
        messages = []
        for i in range(10):  # Lee hasta 10 mensajes
            method, properties, body = channel.basic_get(queue='messages', auto_ack=True)
            if body:
                messages.append(body.decode())
            else:
                break
        
        connection.close()
        
        if messages:
            return "✅ Mensajes: " + ", ".join(messages)
        else:
            return "📭 No hay mensajes en la cola"
    except Exception as e:
        return f"❌ Error: {str(e)}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            rabbit = test_rabbitmq()
            postgres = test_postgres()
            
            response = f"""
            <html>
            <body>
                <h1>SmartRoute - Connection Test</h1>
                <p>{rabbit}</p>
                <p>{postgres}</p>
                <hr>
                <p><a href="/rabbit/send?msg=Hola">Enviar mensaje a RabbitMQ</a></p>
                <p><a href="/rabbit/read">Leer mensajes de RabbitMQ</a></p>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode())
            
        elif self.path.startswith('/rabbit/send'):
            # Extraer mensaje del query string
            if '?msg=' in self.path:
                message = self.path.split('?msg=')[1]
            else:
                message = 'Mensaje de prueba'
            
            result = send_message_to_rabbit(message)
            
            response = f"""
            <html>
            <body>
                <h1>Enviar Mensaje a RabbitMQ</h1>
                <p>{result}</p>
                <p><a href="/health">Volver</a></p>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode())
            
        elif self.path == '/rabbit/read':
            result = read_messages_from_rabbit()
            
            response = f"""
            <html>
            <body>
                <h1>Leer Mensajes de RabbitMQ</h1>
                <p>{result}</p>
                <p><a href="/health">Volver</a></p>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode())
            
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print("🚀 Starting test server on port 8000...")
    print("📍 Visit: http://localhost:8000/health")
    server = HTTPServer(('0.0.0.0', 8000), Handler)
    server.serve_forever()

import pika
import psycopg2
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.db.db import WriteDB
from core.db.db_config import WRITE_DB_CONFIG
# Use Environment Variables or hardcode for local testing
CLOUD_AMQP_URL = os.getenv("CLOUD_AMQP_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
DLX_EXCHANGE_NAME = os.getenv("DLX_EXCHANGE_NAME")
DLQ_NAME = os.getenv("DLQ_NAME")
ROUTING_KEY = os.getenv("ROUTING_KEY")

#DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

def process_reading(body, db_wrapper):
    try:
        data = json.loads(body)
        insert_query = "INSERT INTO raven_reports (area, payload) VALUES (%s, %s)"
        row_count = db_wrapper.execute(insert_query, ("bathroom", json.dumps(data)))
        print(f" [v] Inserted {row_count} rows: processed message: {data}")
    except Exception as e:
        print(f" [!] Error processing message: {e}")
        raise # Re-raise to trigger the nack in the subscriber
    
        

class RavenRabbitMQSubscriber:
    def __init__(self, amqp_url, queue):
        self.amqp_url = amqp_url
        self.queue = queue
        self.connection = None
        self.db_conn = None
    def _setup_topology(self, channel):
        channel.exchange_declare(
            exchange=DLX_EXCHANGE_NAME,
            exchange_type="direct",
            durable=True
        )

        channel.queue_declare(
            queue=DLQ_NAME,
            durable=True
        )

        channel.queue_bind(
            exchange=DLX_EXCHANGE_NAME,
            queue=DLQ_NAME,
            routing_key=ROUTING_KEY
        )

        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
                "x-dead-letter-routing-key": ROUTING_KEY
            }
        )

    def start(self):
        try: 
            self.db_conn = WriteDB(**WRITE_DB_CONFIG)
            self.db_conn.connect()
            print(" [v] DB connected")
            
            

            params = pika.URLParameters(self.amqp_url)
            self.connection = pika.BlockingConnection(params)
            channel = self.connection.channel()

            #setup queue
            
            self._setup_topology(channel)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=self.queue,
                on_message_callback=lambda ch, method, props, body: self._on_message(ch, method, props, body)
            )
            print(f" [*] Consumer active on {self.queue} Press CTRL+C to exit")
            channel.start_consuming()
           
        except Exception as e:
            print(f" [!] Error starting RavenRabbitMQSubscriber: {e}")
            raise
       
    def _on_message(self, ch, method, props, body):
        try:
            process_reading(body, self.db_conn)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(" [v] RabbitMQ connection closed")
        if self.db_conn:
            self.db_conn.close()
            print(" [v] DB connection closed")



if __name__ == "__main__":
    if not CLOUD_AMQP_URL:
        print(" [!] Missing environment variables: CLOUD_AMQP_URL")
        sys.exit(1)
    
    subscriber = RavenRabbitMQSubscriber(
        CLOUD_AMQP_URL,
        QUEUE_NAME
    )
    try: 
        subscriber.start()
    except KeyboardInterrupt:
        print("\n [!] Stopping gracefully...")
    finally:
        subscriber.close()

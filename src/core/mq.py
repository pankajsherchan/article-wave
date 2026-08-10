import pika

from core.config import settings


class RabbitMQConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str = "/",
        fail_silently: bool = False,
        **kwargs,
    ) -> None:
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_open

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                )
            )
        except pika.exceptions.AMQPConnectionError as e:
            if not self.fail_silently:
                raise e

    def get_channel(self):
        if self.is_connected():
            return self._connection.channel()

    def close(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None
            print("Closed RabbitMQ connection")


def publish_to_rabbitmq(queue_name: str, data: str):
    """Publish data to a RabbitMQ queue."""
    try:
        rabbitmq_conn = RabbitMQConnection()

        with rabbitmq_conn:
            channel = rabbitmq_conn.get_channel()

            channel.queue_declare(queue=queue_name, durable=True)

            channel.confirm_delivery()

            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
    except pika.exceptions.UnroutableError:
        print("Message could not be routed")
    except Exception:
        print("Error publishing to RabbitMQ.")


if __name__ == "__main__":
    publish_to_rabbitmq("test_queue", "Hello, World!")

import threading
import pika
import logging

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # to prevent race condition.
        # no two threads overwrite each other.
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    # track __init__() method 
                    # set to false, if its not called yet
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, amqp_url, exchange, exchange_type="topic"):
        if self._initialized:
            return 
        self.amqp_url = amqp_url 
        self.exchange = exchange
        self.exchange_type = exchange_type
        self._connection =  None
        self._channel = None

        self._connect()
        self._initialized = True
    
    def _connect(self,):
        params = pika.URLParameters(self.amqp_url)
        params.heartbeat = 600
        try:
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.exchange_declare(
                exchange=self.exchange,
                exchange_type=self.exchange_type,
                durable=True
            )
            # enable callback when message is published
            self._channel.confirm_delivery()
            logger.info(f"Ok, connected to RabbitMQ, exchange: {self.exchange}")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"error, Failed to connect to RabbitM, e: {e}")
            raise 
        
    def _ensure_channel(self):
        if self._connection is None or self._connection.is_closed:
            self._connect() 
        elif self._channel is None or self._channel.is_closed:
            self._channel = self._connection.channel()
            self._channel.confirm_delivery()
    

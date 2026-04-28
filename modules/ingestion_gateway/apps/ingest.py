import ulid, datetime

class Ingestor:
    def __init__(self, publisher, source):
        self.publisher = publisher
        self.source = source

    def push(self, payload, metadata, source):
        msg = Message(payload=payload, source, metadata)
        routing_key = f"{source}"
        success = self.publisher.publish(
            message=msg,
            routing_key=routing_key
        )
        if not success:
            logger.error("Failed to push message payload to broker.")
            return None
        
        # continue...
        
class Message:
    id = str(ulid.new())
    source = "ingestion-gateway"
    payload = dict()
    timestamp = datetime.utcnow()
    metadata = dict()

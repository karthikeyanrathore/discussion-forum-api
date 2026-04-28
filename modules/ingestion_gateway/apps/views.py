import logging
from flask import Blueprint, request, jsonify, make_response
from apps.publisher import RabbitMQPublisher
from apps.settings import Setting

ingest_bp = Blueprint("ingest", __name__, url_prefix="/api/v1")

publisher = RabbitMQPublisher(
    amqp_url=Setting.RABBITMQ_URL,
    exchange=Setting.RABBITMQ_EXCHANGE,
    exchange_type=Setting.RABBITMQ_EXCHANGE_TYPE,
)

def api_response(data: dict, status_code: int = 200):
    response = make_response(jsonify(data), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response

@ingest_bp.route("/ingest/<source>", methods=["POST"])
def ingest_source(source):
    supported_sources = ["calendar, whatsapp"]
    if source not in supported_sources:
        return api_response({"message": f"error, source:{source} not supported!"}, 404)

    return "Ok" 
    

@ingest_bp.route("/health", methods=["GET"])
def health_check():
    try:
        publisher._ensure_channel()
        return api_response({
            "status": "Ok",
            "rabbitmq": "connected",
            "exchange": publisher.exchange,
        }, 200)
    except Exception as e:
        return api_response({
            "status": "Bad",
            "rabbitmq error": str(e),
        }, 503)

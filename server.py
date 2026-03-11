"""Flask server with Twilio WhatsApp webhook."""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from twilio.rest import Client
from langsmith import traceable

from inventory import InventoryStore
from agent import SalesAgent

load_dotenv()

app = Flask(__name__)

# Initialize components
inventory = InventoryStore()
inventory.load_csv("products.csv")
sales_agent = SalesAgent(inventory)

# Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")


@traceable(name="handle_whatsapp_message")
def send_whatsapp_message(to: str, body: str):
    """Send WhatsApp message via Twilio."""
    message = twilio_client.messages.create(
        from_=twilio_number,
        body=body,
        to=f"whatsapp:{to}"
    )
    return message.sid


@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Receive incoming WhatsApp messages."""
    incoming_msg = request.form.get("Body", "")
    from_number = request.form.get("From", "").replace("whatsapp:", "")

    if not incoming_msg or not from_number:
        return jsonify({"error": "Invalid request"}), 400

    # Process query with sales agent
    response = sales_agent.process_query(incoming_msg)

    # Send response via WhatsApp
    send_whatsapp_message(from_number, response)

    return jsonify({"status": "sent"}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000))
    )

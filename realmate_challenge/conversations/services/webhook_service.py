import json
import logging
import os
from datetime import datetime
from pathlib import Path
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework import status
from ..models import Conversation, Message


# Configurar logging estruturado
LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "webhook.log"

# Configurar logger
logger = logging.getLogger("webhook_service")
logger.setLevel(logging.INFO)

# Handler para arquivo
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato JSON estruturado
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "event": getattr(record, "event", "UNKNOWN"),
            "conversation_id": getattr(record, "conversation_id", None),
            "status": getattr(record, "status", "error"),
            "timestamp": datetime.utcnow().isoformat(),
            "message": record.getMessage(),
        }
        return json.dumps(log_data)

formatter = JSONFormatter()
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class WebhookService:
    @staticmethod
    def _parse_timestamp(timestamp_value):
        """Parse timestamp string para datetime."""
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        if isinstance(timestamp_value, str):
            dt = parse_datetime(timestamp_value)
            if dt is None:
                raise ValueError(f"Invalid timestamp format: {timestamp_value}")
            return dt
        raise ValueError(f"Invalid timestamp type: {type(timestamp_value)}")

    @staticmethod
    def _log_event(event_type, conversation_id=None, status_value="success", message=""):
        """Registra log estruturado."""
        extra = {
            "event": event_type,
            "conversation_id": str(conversation_id) if conversation_id else None,
            "status": status_value,
        }
        logger.info(message, extra=extra)

    @staticmethod
    def process_event(event_data):
        """
        Processa eventos do webhook.
        
        Args:
            event_data: Dicionário com 'type', 'data', 'timestamp'
            
        Returns:
            Response do DRF com status code apropriado
        """
        event_type = event_data.get("type")
        data = event_data.get("data", {})
        timestamp = event_data.get("timestamp")

        if not event_type:
            WebhookService._log_event("UNKNOWN", status_value="error", message="Event type missing")
            return Response({"error": "Event type is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if event_type == "NEW_CONVERSATION":
                return WebhookService._handle_new_conversation(data)
            
            elif event_type == "CLOSE_CONVERSATION":
                return WebhookService._handle_close_conversation(data)
            
            elif event_type == "NEW_MESSAGE":
                return WebhookService._handle_new_message(data, timestamp)
            
            else:
                WebhookService._log_event(
                    event_type, 
                    status_value="error", 
                    message=f"Unknown event type: {event_type}"
                )
                return Response(
                    {"error": f"Unknown event type: {event_type}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except IntegrityError as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            WebhookService._log_event(
                event_type, 
                conversation_id=conversation_id,
                status_value="error", 
                message=f"Duplicate ID: {str(e)}"
            )
            return Response({"error": "Duplicate ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            WebhookService._log_event(
                event_type,
                conversation_id=conversation_id,
                status_value="error",
                message=f"Missing required field: {str(e)}"
            )
            return Response(
                {"error": f"Missing required field: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            WebhookService._log_event(
                event_type,
                conversation_id=conversation_id,
                status_value="error",
                message=f"Unexpected error: {str(e)}"
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _handle_new_conversation(data):
        """Processa evento NEW_CONVERSATION."""
        conversation_id = data["id"]
        conversation, created = Conversation.objects.get_or_create(id=conversation_id)
        
        if created:
            WebhookService._log_event(
                "NEW_CONVERSATION",
                conversation_id=conversation_id,
                status_value="success",
                message=f"Conversation {conversation_id} created successfully"
            )
        else:
            WebhookService._log_event(
                "NEW_CONVERSATION",
                conversation_id=conversation_id,
                status_value="success",
                message=f"Conversation {conversation_id} already exists"
            )
        
        return Response({"success": True}, status=status.HTTP_201_CREATED)

    @staticmethod
    def _handle_close_conversation(data):
        """Processa evento CLOSE_CONVERSATION."""
        conversation_id = data["id"]
        conversation = Conversation.objects.filter(id=conversation_id).first()
        
        if not conversation:
            WebhookService._log_event(
                "CLOSE_CONVERSATION",
                conversation_id=conversation_id,
                status_value="error",
                message=f"Conversation {conversation_id} not found"
            )
            return Response(
                {"error": "Conversation not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation.status = "CLOSED"
        conversation.save()
        
        WebhookService._log_event(
            "CLOSE_CONVERSATION",
            conversation_id=conversation_id,
            status_value="success",
            message=f"Conversation {conversation_id} closed successfully"
        )
        
        return Response({"success": True}, status=status.HTTP_200_OK)

    @staticmethod
    def _handle_new_message(data, timestamp):
        """Processa evento NEW_MESSAGE."""
        conversation_id = data["conversation_id"]
        message_id = data["id"]
        direction = data["direction"]
        content = data["content"]
        
        conversation = Conversation.objects.filter(id=conversation_id).first()
        
        if not conversation:
            WebhookService._log_event(
                "NEW_MESSAGE",
                conversation_id=conversation_id,
                status_value="error",
                message=f"Conversation {conversation_id} not found"
            )
            return Response(
                {"error": "Conversation not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.status == "CLOSED":
            WebhookService._log_event(
                "NEW_MESSAGE",
                conversation_id=conversation_id,
                status_value="error",
                message=f"Cannot add message to closed conversation {conversation_id}"
            )
            return Response(
                {"error": "Conversation closed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        parsed_timestamp = WebhookService._parse_timestamp(timestamp)
        
        Message.objects.create(
            id=message_id,
            conversation=conversation,
            direction=direction,
            content=content,
            timestamp=parsed_timestamp,
        )
        
        WebhookService._log_event(
            "NEW_MESSAGE",
            conversation_id=conversation_id,
            status_value="success",
            message=f"Message {message_id} created successfully in conversation {conversation_id}"
        )
        
        return Response({"success": True}, status=status.HTTP_201_CREATED)


from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response
from rest_framework import status
from ..models import Conversation, Message, WebhookLog


class WebhookService:
    @staticmethod
    def _parse_timestamp(timestamp_value):
        """Parse timestamp string para datetime."""
        from datetime import datetime
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        if isinstance(timestamp_value, str):
            dt = parse_datetime(timestamp_value)
            if dt is None:
                raise ValueError(f"Formato de timestamp inválido: {timestamp_value}")
            return dt
        raise ValueError(f"Tipo de timestamp inválido: {type(timestamp_value)}")

    @staticmethod
    def _log_event(event_type, conversation_id=None, status_value="success", message=""):
        """Registra log estruturado no banco de dados."""
        try:
            WebhookLog.objects.create(
                event=event_type,
                conversation_id=conversation_id,
                status=status_value,
                message=message
            )
        except Exception as e:
            # Se falhar ao salvar log, não quebra o fluxo principal
            # Apenas imprime no console como fallback
            print(f"Erro ao salvar log: {str(e)}")

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
            WebhookService._log_event("UNKNOWN", status_value="error", message="Tipo de evento ausente")
            return Response(
                {"success": False, "description": "O tipo de evento é obrigatório"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
                    message=f"Tipo de evento desconhecido: {event_type}"
                )
                return Response(
                    {"success": False, "description": f"Tipo de evento desconhecido: {event_type}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except IntegrityError as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            error_message = str(e)
            
            # Mapear erros de integridade específicos
            if "UNIQUE constraint" in error_message or "duplicate key" in error_message.lower():
                description = "ID duplicado detectado. O ID já existe no banco de dados."
            elif "FOREIGN KEY constraint" in error_message:
                description = "Violação de chave estrangeira. O recurso referenciado não existe."
            elif "NOT NULL constraint" in error_message:
                description = "Campo obrigatório ausente ou nulo."
            else:
                description = f"Erro de integridade do banco de dados: {error_message}"
            
            WebhookService._log_event(
                event_type, 
                conversation_id=conversation_id,
                status_value="error", 
                message=f"IntegrityError: {error_message}"
            )
            return Response(
                {"success": False, "description": description}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except KeyError as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            missing_field = str(e).strip("'\"")
            WebhookService._log_event(
                event_type,
                conversation_id=conversation_id,
                status_value="error",
                message=f"Campo obrigatório ausente: {missing_field}"
            )
            return Response(
                {"success": False, "description": f"Campo obrigatório ausente: {missing_field}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except ValueError as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            WebhookService._log_event(
                event_type,
                conversation_id=conversation_id,
                status_value="error",
                message=f"Valor inválido: {str(e)}"
            )
            return Response(
                {"success": False, "description": f"Valor inválido: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            conversation_id = data.get("id") or data.get("conversation_id")
            WebhookService._log_event(
                event_type,
                conversation_id=conversation_id,
                status_value="error",
                message=f"Erro inesperado: {str(e)}"
            )
            # Retornar 400 ao invés de 500 para evitar erros não tratados
            return Response(
                {"success": False, "description": f"Ocorreu um erro ao processar a requisição: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
                message=f"Conversa {conversation_id} criada com sucesso"
            )
        else:
            WebhookService._log_event(
                "NEW_CONVERSATION",
                conversation_id=conversation_id,
                status_value="success",
                message=f"Conversa {conversation_id} já existe"
            )
        
        return Response({"success": True, "message": "Conversa processada com sucesso"}, status=status.HTTP_201_CREATED)

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
                message=f"Conversa {conversation_id} não encontrada"
            )
            return Response(
                {"success": False, "description": f"Conversa com ID {conversation_id} não encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation.status = "CLOSED"
        conversation.save()
        
        WebhookService._log_event(
            "CLOSE_CONVERSATION",
            conversation_id=conversation_id,
            status_value="success",
            message=f"Conversa {conversation_id} fechada com sucesso"
        )
        
        return Response({"success": True, "message": "Conversa fechada com sucesso"}, status=status.HTTP_200_OK)

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
                message=f"Conversa {conversation_id} não encontrada"
            )
            return Response(
                {"success": False, "description": f"Conversa com ID {conversation_id} não encontrada"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conversation.status == "CLOSED":
            WebhookService._log_event(
                "NEW_MESSAGE",
                conversation_id=conversation_id,
                status_value="error",
                message=f"Não é possível adicionar mensagem à conversa fechada {conversation_id}"
            )
            return Response(
                {"success": False, "description": f"Não é possível adicionar mensagem à conversa fechada {conversation_id}"}, 
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
            message=f"Mensagem {message_id} criada com sucesso na conversa {conversation_id}"
        )
        
        return Response({"success": True, "message": "Mensagem criada com sucesso"}, status=status.HTTP_201_CREATED)


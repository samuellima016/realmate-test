import logging
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation
from .serializers import ConversationSerializer
from .services.webhook_service import WebhookService


class WebhookView(APIView):
    """View para receber eventos do webhook."""
    
    def post(self, request):
        """Processa eventos do webhook via WebhookService."""
        try:
            # Validar que request.data existe e é um dicionário
            if not request.data:
                return Response(
                    {"success": False, "description": "Corpo da requisição é obrigatório"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return WebhookService.process_event(request.data)
        
        except Exception as e:
            # Capturar qualquer exceção não tratada para evitar código 500
            logger = logging.getLogger("webhook_service")
            logger.error(f"Exceção não tratada em WebhookView: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "description": f"Ocorreu um erro ao processar a requisição: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ConversationListView(ListAPIView):
    """Lista todas as conversas."""
    
    queryset = Conversation.objects.prefetch_related("messages").order_by("-created_at")
    serializer_class = ConversationSerializer


class ConversationDetailView(RetrieveAPIView):
    """Retorna detalhes de uma conversa específica."""
    
    queryset = Conversation.objects.prefetch_related("messages")
    serializer_class = ConversationSerializer
    lookup_field = "id"



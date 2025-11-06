from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from .models import Conversation
from .serializers import ConversationSerializer
from .services.webhook_service import WebhookService


class WebhookView(APIView):
    """View para receber eventos do webhook."""
    
    def post(self, request):
        """Processa eventos do webhook via WebhookService."""
        return WebhookService.process_event(request.data)


class ConversationListView(ListAPIView):
    """Lista todas as conversas."""
    
    queryset = Conversation.objects.prefetch_related("messages").order_by("-created_at")
    serializer_class = ConversationSerializer


class ConversationDetailView(RetrieveAPIView):
    """Retorna detalhes de uma conversa específica."""
    
    queryset = Conversation.objects.prefetch_related("messages")
    serializer_class = ConversationSerializer
    lookup_field = "id"



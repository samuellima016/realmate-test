from django.urls import path
from .views import WebhookView, ConversationDetailView, ConversationListView

urlpatterns = [
    path("webhook/", WebhookView.as_view()),
    path("conversations/", ConversationListView.as_view()),
    path("conversations/<uuid:id>/", ConversationDetailView.as_view()),
]



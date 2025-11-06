from django.contrib import admin
from .models import Conversation, Message, WebhookLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'direction', 'timestamp', 'content_preview')
    list_filter = ('direction', 'timestamp')
    search_fields = ('id', 'content', 'conversation__id')
    readonly_fields = ('id', 'timestamp')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('event', 'conversation_id', 'status', 'timestamp', 'message_preview')
    list_filter = ('event', 'status', 'timestamp')
    search_fields = ('event', 'message', 'conversation_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Mensagem'


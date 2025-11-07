import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import CreateMessage from './CreateMessage';
import './ConversationDetail.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:80';

function ConversationDetail() {
  const { id } = useParams();
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConversation();
  }, [id]);

  const fetchConversation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/conversations/${id}/`);
      setConversation(response.data);
    } catch (err) {
      setError(err.response?.data?.description || err.response?.data?.error || 'Erro ao carregar conversa');
      console.error('Erro ao buscar conversa:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseConversation = async () => {
    if (!window.confirm('Tem certeza que deseja fechar esta conversa?')) {
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/webhook/`, {
        type: 'CLOSE_CONVERSATION',
        data: {
          id: id
        }
      });

      if (response.data.success) {
        fetchConversation();
      } else {
        alert(response.data.description || 'Erro ao fechar conversa');
      }
    } catch (err) {
      alert(err.response?.data?.description || 'Erro ao fechar conversa');
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  if (loading) {
    return <div className="loading">Carregando conversa...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error">{error}</div>
        <div style={{ marginTop: '20px' }}>
          <Link to="/" className="button" style={{ textDecoration: 'none', display: 'inline-block' }}>
            Voltar para lista
          </Link>
          <button className="button" onClick={fetchConversation} style={{ marginLeft: '10px' }}>
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div>
        <div className="error">Conversa não encontrada</div>
        <Link to="/" className="button" style={{ textDecoration: 'none', display: 'inline-block', marginTop: '20px' }}>
          Voltar para lista
        </Link>
      </div>
    );
  }

  const messages = conversation.messages || [];

  return (
    <div className="conversation-detail">
      <div className="conversation-detail-header">
        <Link to="/" className="back-link">
          ← Voltar para lista
        </Link>
        <div className="conversation-info">
          <h2>Conversa {conversation.id}</h2>
          <span className={`status-badge status-${conversation.status.toLowerCase()}`}>
            {conversation.status === 'OPEN' ? 'Aberta' : 'Fechada'}
          </span>
        </div>
        <div className="header-actions">
          {conversation.status === 'OPEN' && (
            <button 
              className="button-danger" 
              onClick={handleCloseConversation}
            >
              Fechar Conversa
            </button>
          )}
          <button className="button-secondary" onClick={fetchConversation}>
            Atualizar
          </button>
        </div>
      </div>

      {conversation.status === 'OPEN' && (
        <CreateMessage 
          conversationId={conversation.id} 
          onSuccess={fetchConversation}
        />
      )}

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-messages">
            <p>Nenhuma mensagem nesta conversa.</p>
            <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
              Envie um evento NEW_MESSAGE para o webhook para adicionar mensagens.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message message-${message.direction.toLowerCase()}`}
            >
              <div className="message-header">
                <span className="message-direction">
                  {message.direction === 'SENT' ? '📤 Enviada' : '📥 Recebida'}
                </span>
                <span className="message-id">ID: {message.id}</span>
                <span className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
              <div className="message-content">{message.content}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ConversationDetail;


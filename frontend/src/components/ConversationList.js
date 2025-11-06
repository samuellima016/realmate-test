import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ConversationList.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function ConversationList() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/conversations/`);
      setConversations(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar conversas');
      console.error('Erro ao buscar conversas:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando conversas...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error">{error}</div>
        <button className="button" onClick={fetchConversations}>
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h2>Conversas ({conversations.length})</h2>
        <button className="button" onClick={fetchConversations}>
          Atualizar
        </button>
      </div>
      
      {conversations.length === 0 ? (
        <div className="empty-state">
          <p>Nenhuma conversa encontrada.</p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
            Envie um evento para o webhook para criar uma conversa.
          </p>
        </div>
      ) : (
        <div className="conversations-grid">
          {conversations.map((conversation) => (
            <Link
              key={conversation.id}
              to={`/conversation/${conversation.id}`}
              className="conversation-card"
            >
              <div className="conversation-card-header">
                <span className={`status-badge status-${conversation.status.toLowerCase()}`}>
                  {conversation.status}
                </span>
                <span className="message-count">
                  {conversation.messages?.length || 0} mensagens
                </span>
              </div>
              <div className="conversation-id">
                {conversation.id}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default ConversationList;


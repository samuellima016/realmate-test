import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import CreateConversation from './CreateConversation';
import './ConversationList.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:80';

function ConversationList() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

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
      setError(err.response?.data?.description || err.response?.data?.error || 'Erro ao carregar conversas');
      console.error('Erro ao buscar conversas:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConversationCreated = () => {
    setShowCreateForm(false);
    fetchConversations();
  };

  const handleCloseConversation = async (conversationId, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!window.confirm('Tem certeza que deseja fechar esta conversa?')) {
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/webhook/`, {
        type: 'CLOSE_CONVERSATION',
        data: {
          id: conversationId
        }
      });

      if (response.data.success) {
        fetchConversations();
      } else {
        alert(response.data.description || 'Erro ao fechar conversa');
      }
    } catch (err) {
      alert(err.response?.data?.description || 'Erro ao fechar conversa');
    }
  };

  if (loading) {
    return <div className="loading">Carregando conversas...</div>;
  }

  if (error && !conversations.length) {
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
    <div className="conversation-list-container">
      <div className="conversation-header">
        <h2>Conversas ({conversations.length})</h2>
        <div className="conversation-actions">
          <button 
            className="button" 
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancelar' : '+ Nova Conversa'}
          </button>
          <button className="button-secondary" onClick={fetchConversations}>
            Atualizar
          </button>
        </div>
      </div>

      {showCreateForm && (
        <CreateConversation
          onSuccess={handleConversationCreated}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {error && (
        <div className="error" style={{ marginBottom: '20px' }}>{error}</div>
      )}
      
      {conversations.length === 0 ? (
        <div className="empty-state">
          <p>Nenhuma conversa encontrada.</p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
            Clique em "Nova Conversa" para criar uma conversa.
          </p>
        </div>
      ) : (
        <div className="conversation-list">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="conversation-card-wrapper">
              <Link
                to={`/conversation/${conversation.id}`}
                className="conversation-card"
              >
                <div className="conversation-card-header">
                  <span className={`status-badge status-${conversation.status.toLowerCase()}`}>
                    {conversation.status === 'OPEN' ? 'Aberta' : 'Fechada'}
                  </span>
                  <span className="message-count">
                    {conversation.messages?.length || 0} mensagens
                  </span>
                </div>
                <div className="conversation-id">
                  {conversation.id}
                </div>
              </Link>
              {conversation.status === 'OPEN' && (
                <button
                  className="button-close-conversation"
                  onClick={(e) => handleCloseConversation(conversation.id, e)}
                  title="Fechar conversa"
                >
                  Fechar
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ConversationList;


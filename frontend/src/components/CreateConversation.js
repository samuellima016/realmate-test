import React, { useState } from 'react';
import axios from 'axios';
import './CreateConversation.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function CreateConversation({ onSuccess, onCancel }) {
  const [conversationId, setConversationId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  const handleGenerateId = () => {
    setConversationId(generateUUID());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(`${API_BASE_URL}/webhook/`, {
        type: 'NEW_CONVERSATION',
        data: {
          id: conversationId
        }
      });

      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          if (onSuccess) onSuccess();
        }, 1500);
      } else {
        setError(response.data.description || 'Erro ao criar conversa');
      }
    } catch (err) {
      setError(err.response?.data?.description || 'Erro ao criar conversa');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-conversation">
      <h2>Criar Nova Conversa</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="conversationId">ID da Conversa (UUID)</label>
          <div className="input-with-button">
            <input
              type="text"
              id="conversationId"
              value={conversationId}
              onChange={(e) => setConversationId(e.target.value)}
              placeholder="Ex: 123e4567-e89b-12d3-a456-426614174000"
              required
              pattern="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            />
            <button
              type="button"
              onClick={handleGenerateId}
              className="button-secondary"
            >
              Gerar UUID
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Conversa criada com sucesso!</div>}

        <div className="form-actions">
          <button type="submit" className="button" disabled={loading}>
            {loading ? 'Criando...' : 'Criar Conversa'}
          </button>
          {onCancel && (
            <button type="button" onClick={onCancel} className="button-secondary">
              Cancelar
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

export default CreateConversation;


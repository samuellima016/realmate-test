import React, { useState } from 'react';
import axios from 'axios';
import './CreateMessage.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

function CreateMessage({ conversationId, onSuccess }) {
  const [messageId, setMessageId] = useState('');
  const [direction, setDirection] = useState('SENT');
  const [content, setContent] = useState('');
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
    setMessageId(generateUUID());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(`${API_BASE_URL}/webhook/`, {
        type: 'NEW_MESSAGE',
        data: {
          id: messageId,
          conversation_id: conversationId,
          direction: direction,
          content: content
        },
        timestamp: new Date().toISOString()
      });

      if (response.data.success) {
        setSuccess(true);
        setContent('');
        setMessageId('');
        setTimeout(() => {
          setSuccess(false);
          if (onSuccess) onSuccess();
        }, 2000);
      } else {
        setError(response.data.description || 'Erro ao criar mensagem');
      }
    } catch (err) {
      setError(err.response?.data?.description || 'Erro ao criar mensagem');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-message">
      <h3>Adicionar Nova Mensagem</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="messageId">ID da Mensagem (UUID)</label>
          <div className="input-with-button">
            <input
              type="text"
              id="messageId"
              value={messageId}
              onChange={(e) => setMessageId(e.target.value)}
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

        <div className="form-group">
          <label htmlFor="direction">Direção</label>
          <select
            id="direction"
            value={direction}
            onChange={(e) => setDirection(e.target.value)}
            className="select-input"
          >
            <option value="SENT">Enviada</option>
            <option value="RECEIVED">Recebida</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="content">Conteúdo da Mensagem</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Digite a mensagem..."
            required
            rows="4"
            className="textarea-input"
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Mensagem criada com sucesso!</div>}

        <div className="form-actions">
          <button type="submit" className="button" disabled={loading}>
            {loading ? 'Enviando...' : 'Enviar Mensagem'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateMessage;


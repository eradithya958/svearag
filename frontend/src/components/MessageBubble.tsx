import React, { useState } from 'react';
import { AskResponse, submitFeedback } from '../services/api';
import { CitationCard } from './CitationCard';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  responseMeta?: AskResponse;
  timestamp: string;
}

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const handleFeedback = async (rating: 'up' | 'down') => {
    if (!message.responseMeta?.query_id || feedback === rating) return;
    try {
      await submitFeedback(message.responseMeta.query_id, rating);
      setFeedback(rating);
    } catch (e) {
      console.error('Feedback error:', e);
    }
  };

  if (message.sender === 'user') {
    return (
      <div className="message-row user">
        <div className="avatar user">U</div>
        <div className="bubble">{message.text}</div>
      </div>
    );
  }

  const meta = message.responseMeta;

  return (
    <div className="message-row assistant">
      <div className="avatar assistant">🇸🇪</div>
      <div className="bubble" style={{ width: '100%' }}>
        <div style={{ whiteSpace: 'pre-wrap' }}>{message.text}</div>

        {meta?.citations && meta.citations.length > 0 && (
          <div className="citations-section">
            <div className="citations-header">📚 Cited Official Sources ({meta.citations.length})</div>
            <div className="citation-cards">
              {meta.citations.map((c, idx) => (
                <CitationCard key={idx} citation={c} />
              ))}
            </div>
          </div>
        )}

        {meta && (
          <div className="message-footer">
            <div className="latency-pills">
              <span className="latency-pill" title="Retrieval Latency">
                🔍 {meta.retrieval_latency_ms}ms
              </span>
              <span className="latency-pill" title="LLM Inference Latency">
                ⚡ {meta.llm_latency_ms}ms
              </span>
              <span className="latency-pill" title="Total Roundtrip">
                ⏱️ {meta.total_latency_ms}ms
              </span>
            </div>

            <div className="feedback-actions">
              <button
                className={`feedback-btn ${feedback === 'up' ? 'active-up' : ''}`}
                onClick={() => handleFeedback('up')}
                title="Helpful response"
              >
                👍
              </button>
              <button
                className={`feedback-btn ${feedback === 'down' ? 'active-down' : ''}`}
                onClick={() => handleFeedback('down')}
                title="Inaccurate or unhelpful"
              >
                👎
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

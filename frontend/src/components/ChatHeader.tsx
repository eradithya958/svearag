import React from 'react';
import { HealthResponse } from '../services/api';

interface ChatHeaderProps {
  health: HealthResponse | null;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ health }) => {
  return (
    <header className="header">
      <div className="brand-container">
        <span className="brand-logo">🇸🇪 SveaRAG</span>
        <span className="brand-badge">Agile Swedish Public Assistant</span>
      </div>
      <div className="header-meta">
        <div className="status-pill">
          <span className="status-indicator"></span>
          <span>
            {health
              ? `${health.total_documents_indexed} Official Docs Indexed • ${health.llm_model}`
              : 'Connecting...'}
          </span>
        </div>
      </div>
    </header>
  );
};

import React, { useState } from 'react';

interface ChatInputProps {
  onSendMessage: (query: string, agency?: string, language?: string, alpha?: number) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [query, setQuery] = useState('');
  const [agency, setAgency] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [alpha, setAlpha] = useState<number>(0.5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSendMessage(
      query.trim(),
      agency || undefined,
      language || undefined,
      alpha
    );
    setQuery('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="input-container">
      <div className="filter-bar">
        <select
          className="filter-select"
          value={agency}
          onChange={(e) => setAgency(e.target.value)}
        >
          <option value="">🏢 All Public Agencies</option>
          <option value="Migrationsverket">Migrationsverket</option>
          <option value="Skatteverket">Skatteverket</option>
        </select>

        <select
          className="filter-select"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="">🌐 Any Language (EN/SV)</option>
          <option value="en">English (EN)</option>
          <option value="sv">Svenska (SV)</option>
        </select>

        <select
          className="filter-select"
          value={alpha}
          onChange={(e) => setAlpha(parseFloat(e.target.value))}
        >
          <option value="0.5">⚖️ Balanced Hybrid (RRF α=0.5)</option>
          <option value="1.0">🧠 Dense Vector Only (α=1.0)</option>
          <option value="0.0">🔤 BM25 Keyword Only (α=0.0)</option>
        </select>
      </div>

      <form onSubmit={handleSubmit} className="input-box">
        <textarea
          rows={1}
          className="chat-input"
          placeholder="Ask a question about residence permits, taxes, personnummer, or studying in Sweden..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !query.trim()}>
          {isLoading ? 'Searching...' : 'Send ⏎'}
        </button>
      </form>
    </div>
  );
};

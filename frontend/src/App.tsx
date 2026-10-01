import React, { useState, useEffect, useRef } from 'react';
import { ChatHeader } from './components/ChatHeader';
import { MessageBubble, ChatMessage } from './components/MessageBubble';
import { ChatInput } from './components/ChatInput';
import { askQuestion, checkHealth, HealthResponse } from './services/api';

const SAMPLE_QUESTIONS = [
  'What is the monthly maintenance requirement for student residence permits in Sweden?',
  'How do I register in the Swedish population register (Folkbokföring) to receive a personnummer?',
  'What are the requirements for applying for permanent residence (PUT) after doctoral studies?',
  'What is the difference between SINK tax and regular municipal A-skatt for foreign workers?',
];

export const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch((err) => console.warn('Backend not yet reachable:', err));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (
    query: string,
    agency?: string,
    language?: string,
    alpha?: number
  ) => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await askQuestion(query, 4, agency, language, alpha);
      const assistantMsg: ChatMessage = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: response.answer,
        responseMeta: response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: `⚠️ Error retrieving guidance: ${err.message || 'Server error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <ChatHeader health={health} />

      <main className="messages-list">
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', margin: 'auto', maxWidth: '650px', padding: '2rem 1rem' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.75rem' }}>
              Official Swedish Public Sector Guidance
            </h2>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '2rem' }}>
              Ask verified questions regarding <strong>Migrationsverket</strong> visa rules and <strong>Skatteverket</strong> registration. Answers are strictly grounded in authoritative guidance with source citations.
            </p>

            <div className="suggestions-grid">
              {SAMPLE_QUESTIONS.map((q, idx) => (
                <div
                  key={idx}
                  className="suggestion-card"
                  onClick={() => handleSendMessage(q)}
                >
                  💬 {q}
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar assistant">🇸🇪</div>
            <div className="bubble" style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Searching authoritative Swedish corpus and verifying citations...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

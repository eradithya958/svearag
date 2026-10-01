import React, { useState } from 'react';
import { CitedSource } from '../services/api';

interface CitationCardProps {
  citation: CitedSource;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation }) => {
  const [expanded, setExpanded] = useState(false);
  const agencyClass = citation.agency.toLowerCase().includes('skatte')
    ? 'skatteverket'
    : 'migrationsverket';

  return (
    <div className="citation-card" onClick={() => setExpanded(!expanded)}>
      <div className="citation-meta">
        <span className="citation-tag">{citation.doc_tag} {citation.doc_id}</span>
        <span className={`agency-badge ${agencyClass}`}>{citation.agency}</span>
      </div>
      <div className="citation-title" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.25rem' }}>
        {citation.title}
      </div>
      <div className="citation-snippet">
        {expanded ? citation.snippet : `${citation.snippet.slice(0, 140)}...`}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.35rem' }}>
        <a
          href={citation.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="citation-link"
          onClick={(e) => e.stopPropagation()}
        >
          ↗ View Official Source
        </a>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          Relevance: {citation.relevance_score}
        </span>
      </div>
    </div>
  );
};

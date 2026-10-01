export interface CitedSource {
  doc_tag: string;
  doc_id: string;
  title: string;
  agency: string;
  source_url: string;
  snippet: string;
  relevance_score: number;
}

export interface AskResponse {
  query_id: string;
  question: string;
  answer: string;
  citations: CitedSource[];
  retrieval_latency_ms: number;
  llm_latency_ms: number;
  total_latency_ms: number;
  model_name: string;
}

export interface HealthResponse {
  status: string;
  environment: string;
  vector_store_healthy: boolean;
  total_documents_indexed: number;
  llm_model: string;
  version: string;
}

const API_BASE = '/api/v1';

export async function askQuestion(
  query: string,
  topK: number = 4,
  agency?: string,
  language?: string,
  alpha: number = 0.5
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      top_k: topK,
      agency: agency || undefined,
      language: language || undefined,
      alpha,
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export async function submitFeedback(
  queryId: string,
  rating: 'up' | 'down',
  comment?: string
): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query_id: queryId,
      rating,
      comment,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit feedback: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('Healthcheck failed');
  }
  return response.json();
}

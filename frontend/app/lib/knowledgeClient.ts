export interface KnowledgeResponse {
  response: string;
  confidence: number;
  context?: Array<{ content: string; metadata?: Record<string, unknown> }>;
}

const KNOWLEDGE_QUERY_PATH = '/api/v1/knowledge/query';

function getKnowledgeQueryUrl(): string {
  const base = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';
  return `${base}${KNOWLEDGE_QUERY_PATH}`;
}

export async function queryKnowledge(query: string): Promise<KnowledgeResponse> {
  let response: Response;
  try {
    response = await fetch(getKnowledgeQueryUrl(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
  } catch {
    throw new Error(
      'Cannot reach the backend at http://localhost:8000. Start it with: uvicorn app.main:app --reload'
    );
  }

  if (!response.ok) {
    let detail = `Knowledge query failed: ${response.status}`;
    try {
      const errorBody = await response.json();
      if (typeof errorBody?.detail === 'string') {
        detail = errorBody.detail;
      }
    } catch {
      // Keep generic status message when body is not JSON.
    }
    throw new Error(detail);
  }

  return response.json();
}

export const KNOWLEDGE_ERROR_MESSAGE =
  'I apologize, but I encountered an error processing your request. Please try again or check your connection.';

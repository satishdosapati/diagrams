/**
 * API client for diagram generation.
 */

// Determine API URL based on environment
// In production (on EC2), use the EC2 public IP
// In development, use localhost
const getApiBaseUrl = (): string => {
  // If VITE_API_URL is explicitly set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // If running on EC2 (production), use EC2 public IP
  // Check if we're accessing from EC2 IP or if window.location suggests production
  const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
  const isProduction = hostname !== 'localhost' && hostname !== '127.0.0.1';
  
  if (isProduction) {
    // Use same hostname as frontend, but port 8000 for backend
    return `${window.location.protocol}//${hostname}:8000`;
  }
  
  // Default to localhost for development
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface GenerateDiagramRequest {
  description: string;
  provider?: string;
  outformat?: string;
}

export interface GenerateDiagramResponse {
  diagram_url: string;
  message: string;
  session_id: string;
  generation_id: string;
  generated_code?: string;
}

export interface RewritePromptRequest {
  description: string;
  provider: string;
}

export interface SuggestedCluster {
  name: string;
  components: string[];
  pattern?: string;
}

export interface RewritePromptResponse {
  rewritten_description: string;
  improvements: string[];
  components_identified: string[];
  suggested_clusters: SuggestedCluster[];
}

export async function rewritePrompt(
  description: string,
  provider: string
): Promise<RewritePromptResponse> {
  const response = await fetch(`${API_BASE_URL}/api/rewrite-prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ description, provider }),
  });

  if (!response.ok) {
    const error = await response.json();
    const requestId = response.headers.get('X-Request-ID');
    const errorWithRequestId = new Error(error.detail || 'Failed to rewrite prompt');
    (errorWithRequestId as any).requestId = requestId;
    (errorWithRequestId as any).statusCode = response.status;
    throw errorWithRequestId;
  }

  return response.json();
}

export async function generateDiagram(
  description: string,
  provider: string = 'aws',
  outformat: string = 'png'
): Promise<GenerateDiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate-diagram`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ description, provider, outformat }),
  });

  if (!response.ok) {
    const error = await response.json();
    const requestId = response.headers.get('X-Request-ID');
    const errorWithRequestId = new Error(error.detail || 'Failed to generate diagram');
    (errorWithRequestId as any).requestId = requestId;
    (errorWithRequestId as any).statusCode = response.status; // Add status code
    throw errorWithRequestId;
  }

  return response.json();
}

export function getDiagramUrl(filename: string): string {
  return `${API_BASE_URL}/api/diagrams/${filename}`;
}


export async function regenerateFormat(
  sessionId: string,
  format: string
): Promise<GenerateDiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/api/regenerate-format`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, outformat: format }),
  });

  if (!response.ok) {
    const error = await response.json();
    const requestId = response.headers.get('X-Request-ID');
    const errorWithRequestId = new Error(error.detail || 'Failed to regenerate format');
    (errorWithRequestId as any).requestId = requestId;
    (errorWithRequestId as any).statusCode = response.status; // Add status code
    throw errorWithRequestId;
  }

  return response.json();
}

export interface ExecuteCodeRequest {
  code: string;
  provider?: string;
  title?: string;
  outformat?: string;
}

export interface ExecuteCodeResponse {
  diagram_url: string;
  message: string;
  errors: string[];
  warnings: string[];
}

export async function executeCode(request: ExecuteCodeRequest): Promise<ExecuteCodeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/execute-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code: request.code,
      provider: request.provider || 'aws',
      title: request.title || 'Diagram',
      outformat: request.outformat || 'png'
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    const requestId = response.headers.get('X-Request-ID');
    const errorWithRequestId = new Error(error.detail || 'Failed to execute code');
    (errorWithRequestId as any).requestId = requestId;
    (errorWithRequestId as any).statusCode = response.status; // Add status code
    throw errorWithRequestId;
  }

  return response.json();
}

export interface CompletionsResponse {
  classes: Record<string, string[]>;
  imports: Record<string, string>;
  keywords: string[];
  operators: string[];
}

export async function getCompletions(provider: string): Promise<CompletionsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/completions/${provider}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get completions');
  }

  return response.json();
}

export interface ValidateCodeRequest {
  code: string;
}

export interface ValidateCodeResponse {
  valid: boolean;
  errors: string[];
  suggestions: string[];
}

export async function validateCode(code: string): Promise<ValidateCodeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/validate-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to validate code');
  }

  return response.json();
}

export interface SubmitFeedbackRequest {
  generation_id: string;
  session_id: string;
  thumbs_up: boolean;
  code_hash?: string;
  code?: string;
}

export interface FeedbackResponse {
  feedback_id: string;
  message: string;
}

export async function submitFeedback(request: SubmitFeedbackRequest): Promise<FeedbackResponse> {
  const response = await fetch(`${API_BASE_URL}/api/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit feedback');
  }

  return response.json();
}

export interface FeedbackStats {
  total_feedbacks: number;
  thumbs_up: number;
  thumbs_down: number;
  thumbs_up_rate: number;
}

export async function getFeedbackStats(days: number = 30): Promise<FeedbackStats> {
  const response = await fetch(`${API_BASE_URL}/api/feedback/stats?days=${days}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get feedback stats');
  }

  return response.json();
}

export interface ErrorLogsResponse {
  request_id: string;
  logs: string[];
  last_50_lines: boolean;
}

export async function getErrorLogs(requestId: string): Promise<ErrorLogsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/error-logs/${requestId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error('Failed to retrieve error logs');
  }

  return response.json();
}
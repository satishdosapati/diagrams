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
}

export interface GenerateDiagramResponse {
  diagram_url: string;
  message: string;
  session_id: string;
}

export interface ModifyDiagramRequest {
  session_id: string;
  modification: string;
}

export interface ModifyDiagramResponse {
  diagram_url: string;
  message: string;
  changes: string[];
  updated_spec: any;
}

export async function generateDiagram(
  description: string,
  provider: string = 'aws'
): Promise<GenerateDiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate-diagram`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ description, provider }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate diagram');
  }

  return response.json();
}

export function getDiagramUrl(filename: string): string {
  return `${API_BASE_URL}/api/diagrams/${filename}`;
}

export async function modifyDiagram(
  sessionId: string,
  modification: string
): Promise<ModifyDiagramResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/modify-diagram`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, modification }),
    });

    if (!response.ok) {
      // Try to get error details from response
      let errorMessage = 'Failed to modify diagram';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = `HTTP ${response.status}: ${response.statusText || 'Unknown error'}`;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  } catch (error) {
    // Handle network errors (CORS, connection refused, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to backend. Please ensure the backend is running on ${API_BASE_URL}`);
    }
    // Re-throw other errors as-is
    throw error;
  }
}

export async function undoDiagram(sessionId: string): Promise<ModifyDiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/api/undo-diagram`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to undo');
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
    throw new Error(error.detail || 'Failed to execute code');
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
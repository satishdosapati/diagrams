/**
 * API client for diagram generation.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  const response = await fetch(`${API_BASE_URL}/api/modify-diagram`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, modification }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to modify diagram');
  }

  return response.json();
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


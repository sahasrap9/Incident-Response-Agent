import type { Incident } from "./mock-data";
const API_BASE_URL = "http://127.0.0.1:8000";

export type BackendIncident = {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  service: string;
  root_cause: string;
  resolution: string;
};

export async function getIncidents(): Promise<BackendIncident[]> {
  const response = await fetch(`${API_BASE_URL}/incidents/`);

  if (!response.ok) {
    throw new Error("Failed to fetch incidents");
  }

  return response.json();
}
export function mapBackendIncident(incident: BackendIncident): Incident {
  return {
    id: `INC-${incident.id}`,
    title: incident.title,
    service: incident.service,
    severity: (incident.severity.charAt(0).toUpperCase() + incident.severity.slice(1)) as Incident["severity"],
    status: (incident.status.charAt(0).toUpperCase() + incident.status.slice(1)) as Incident["status"],
    errorMessage: incident.description,
    timestamp: new Date().toISOString(),
    rootCause: incident.root_cause,
    suggestedFix: incident.resolution,
    duration: '',
    memoryMatch: '',
    similarity: 0,
    relatedIncidentIds: [],
    owner: '',
    tags: [],
  };
}
export type IncidentStats = {
  total: number;
  open: number;
  resolved: number;
};

export async function getIncidentStats(): Promise<IncidentStats> {
  const response = await fetch(`${API_BASE_URL}/incidents/stats`);

  if (!response.ok) {
    throw new Error("Failed to fetch incident stats");
  }

  return response.json();
}
export async function getIncident(id: string): Promise<BackendIncident> {
  const response = await fetch(`${API_BASE_URL}/incidents/${id}`);

  if (!response.ok) {
    throw new Error("Failed to fetch incident");
  }

  return response.json();
}
export type AnalyzeResponse = {
  service: string;
  root_cause: string;
  suggested_fix: string;
  tags: string[];
  confidence: number;
};

export async function analyzeIncident(logs: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ logs }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze incident");
  }

  return response.json();
}
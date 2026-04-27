const BASE = "";

export async function getOnboardingStatus(): Promise<{ onboarded: boolean }> {
  const res = await fetch(`${BASE}/api/onboarding/status`);
  return res.json();
}

export async function useDefaultContext() {
  const res = await fetch(`${BASE}/api/onboarding/use-defaults`, { method: "POST" });
  return res.json();
}

export async function saveCustomContext(answers: {
  role_goals: string;
  projects: string;
  writing_style: string;
  email_prefs: string;
  mental_model: string;
}) {
  const res = await fetch(`${BASE}/api/onboarding/save-custom`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(answers),
  });
  return res.json();
}

export async function resetOnboarding() {
  const res = await fetch(`${BASE}/api/onboarding/reset`, { method: "POST" });
  return res.json();
}

export async function sendMessage(payload: {
  session_id?: string;
  skill?: string;
  message: string;
}): Promise<{ session_id: string }> {
  const res = await fetch(`${BASE}/api/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export function openStream(session_id: string): EventSource {
  return new EventSource(`${BASE}/api/chat/stream?session_id=${session_id}`);
}

export async function closeSession(session_id: string) {
  const res = await fetch(`${BASE}/api/chat/close`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id }),
  });
  return res.json();
}

export async function respondToApproval(approval_id: string, outcome: "approved" | "cancelled") {
  const res = await fetch(`${BASE}/api/approval/${approval_id}/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ outcome }),
  });
  return res.json();
}

export async function queryKnowledge(question: string) {
  const res = await fetch(`${BASE}/api/knowledge/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

export async function ingestPath(path: string, is_directory = false) {
  const res = await fetch(`${BASE}/api/knowledge/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, is_directory }),
  });
  return res.json();
}

export async function getKnowledgeStats() {
  const res = await fetch(`${BASE}/api/knowledge/stats`);
  return res.json();
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: "user" | "admin";
  is_email_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ChatMessage {
  role: "user" | "model";
  content: string;
}

export interface SSEEvent<T = Record<string, unknown>> {
  type: string;
  data: T;
}

// ── Tasks ─────────────────────────────────────────────────────────────────────

export type TaskStatus = "todo" | "in_progress" | "done";

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

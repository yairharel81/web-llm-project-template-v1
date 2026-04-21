import client from "./client";
import type { ChatMessage } from "../types";
import { getToken } from "./auth";

export async function sendMessage(
  messages: ChatMessage[],
  systemPrompt = ""
): Promise<string> {
  const { data } = await client.post<{ response: string }>("/chat/", {
    messages,
    system_prompt: systemPrompt,
  });
  return data.response;
}

export function streamMessage(
  messages: ChatMessage[],
  systemPrompt = "",
  onToken: (token: string) => void,
  onDone: () => void
): EventSource {
  // Use fetch for POST streaming since EventSource only supports GET
  const token = getToken();
  const ctrl = new AbortController();

  fetch("/api/v1/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ messages, system_prompt: systemPrompt }),
    signal: ctrl.signal,
  }).then(async (res) => {
    const reader = res.body?.getReader();
    if (!reader) return;
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      for (const line of chunk.split("\n")) {
        if (line.startsWith("data: ")) {
          const payload = line.slice(6);
          if (payload === "[DONE]") { onDone(); return; }
          onToken(payload);
        }
      }
    }
  });

  return ctrl as unknown as EventSource; // return abort controller disguised — call .abort() to cancel
}

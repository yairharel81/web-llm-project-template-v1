import { useState } from "react";
import { sendMessage } from "../api/chat";
import type { ChatMessage } from "../types";

export function useChat(systemPrompt = "") {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(content: string) {
    const userMessage: ChatMessage = { role: "user", content };
    const next = [...messages, userMessage];
    setMessages(next);
    setIsLoading(true);
    setError(null);
    try {
      const response = await sendMessage(next, systemPrompt);
      setMessages([...next, { role: "model", content: response }]);
    } catch {
      setError("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  }

  function reset() {
    setMessages([]);
    setError(null);
  }

  return { messages, isLoading, error, send, reset };
}

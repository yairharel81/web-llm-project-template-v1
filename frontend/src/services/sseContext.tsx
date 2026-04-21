/**
 * SSE Context — single EventSource connection per session, typed event dispatch.
 *
 * Usage in any component:
 *   useSSEEvent("task_done", (event) => { ... });
 *
 * Wrap protected routes with <SSEProvider> in App.tsx (already done in the template).
 * Do NOT call useSSE() in child components — it would open a duplicate connection.
 */
import { createContext, useContext, useEffect, useRef } from "react";
import { getToken } from "../api/auth";
import type { SSEEvent } from "../types";

type Handler = (event: SSEEvent) => void;

interface SSEContextValue {
  _on: (type: string, handler: Handler) => () => void;
}

const SSEContext = createContext<SSEContextValue | null>(null);

export function SSEProvider({ children }: { children: React.ReactNode }) {
  const listeners = useRef<Map<string, Set<Handler>>>(new Map());

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    // EventSource cannot set custom headers — token goes in query param.
    // The backend /events/stream endpoint reads ?token= for this reason.
    const source = new EventSource(`/api/v1/events/stream?token=${token}`);

    source.onmessage = (e) => {
      if (!e.data || e.data.startsWith(":")) return;
      try {
        const event: SSEEvent = JSON.parse(e.data);
        listeners.current.get(event.type)?.forEach((h) => h(event));
      } catch {
        // ignore malformed events
      }
    };

    source.onerror = () => source.close();
    return () => source.close();
  }, []);

  function _on(type: string, handler: Handler): () => void {
    if (!listeners.current.has(type)) listeners.current.set(type, new Set());
    listeners.current.get(type)!.add(handler);
    return () => listeners.current.get(type)?.delete(handler);
  }

  return <SSEContext.Provider value={{ _on }}>{children}</SSEContext.Provider>;
}

/**
 * Subscribe to a specific SSE event type. Handler is stable — safe to define inline.
 *
 * @example
 *   useSSEEvent("task_done", (event) => {
 *     const { task_id, title } = event.data as { task_id: number; title: string };
 *     showToast(`Task "${title}" is done!`);
 *   });
 */
export function useSSEEvent(type: string, handler: (event: SSEEvent) => void) {
  const ctx = useContext(SSEContext);
  if (!ctx) throw new Error("useSSEEvent must be used inside <SSEProvider>");

  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    return ctx._on(type, (event) => handlerRef.current(event));
  }, [type, ctx]);
}

/**
 * Low-level SSE hook — opens its own EventSource connection.
 *
 * ⚠️  Prefer useSSEEvent() from sseContext for most use cases.
 *     It uses a single shared connection via SSEProvider instead of opening a
 *     new one per component. Use this hook only when you need SSE outside of
 *     the authenticated app shell (e.g. a public status page).
 *
 * Note: EventSource cannot set custom headers. Auth is passed as ?token=
 * in the query string. The backend /events/stream endpoint reads it there.
 */
import { useEffect, useRef } from "react";
import { getToken } from "../api/auth";
import type { SSEEvent } from "../types";

export function useSSE(onEvent: (event: SSEEvent) => void) {
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    const source = new EventSource(`/api/v1/events/stream?token=${token}`);

    source.onmessage = (e) => {
      if (!e.data || e.data.startsWith(":")) return;
      try {
        const event: SSEEvent = JSON.parse(e.data);
        onEventRef.current(event);
      } catch {
        // ignore malformed events
      }
    };

    source.onerror = () => source.close();
    return () => source.close();
  }, []);
}

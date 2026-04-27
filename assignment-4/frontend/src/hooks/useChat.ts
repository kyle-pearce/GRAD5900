import { useState, useCallback, useRef } from "react";
import { sendMessage, openStream, closeSession } from "../api/client";

export type MessageRole = "user" | "assistant";

export interface ApprovalRequest {
  id: string;
  tier: number;
  action: string;
  description: string;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  approvalRequest?: ApprovalRequest;
  approvalResolved?: boolean;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const msgIdRef = useRef(0);

  const nextId = () => String(++msgIdRef.current);

  const addAssistantMessage = useCallback((): string => {
    const id = nextId();
    setMessages((prev) => [...prev, { id, role: "assistant", content: "" }]);
    return id;
  }, []);

  const appendToken = useCallback((msgId: string, token: string) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, content: m.content + token } : m))
    );
  }, []);

  const attachApproval = useCallback((msgId: string, approval: ApprovalRequest) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, approvalRequest: approval } : m))
    );
  }, []);

  const resolveApproval = useCallback((approvalId: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.approvalRequest?.id === approvalId ? { ...m, approvalResolved: true } : m
      )
    );
  }, []);

  const consumeStream = useCallback(
    (streamSessionId: string, assistantMsgId: string, onDone?: () => void) => {
      const es = openStream(streamSessionId);

      es.addEventListener("token", (e) => appendToken(assistantMsgId, e.data));

      es.addEventListener("approval_required", (e) => {
        const approval: ApprovalRequest = JSON.parse(e.data);
        attachApproval(assistantMsgId, approval);
      });

      es.addEventListener("done", () => {
        es.close();
        setLoading(false);
        onDone?.();
      });

      es.onerror = () => {
        es.close();
        setLoading(false);
      };
    },
    [appendToken, attachApproval]
  );

  const send = useCallback(
    async (userText: string, skill?: string) => {
      if (loading) return;
      setLoading(true);

      if (userText) {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), role: "user", content: userText },
        ]);
      }

      try {
        const { session_id } = await sendMessage({
          session_id: sessionId ?? undefined,
          skill,
          message: userText,
        });
        setSessionId(session_id);
        const assistantId = addAssistantMessage();
        consumeStream(session_id, assistantId);
      } catch {
        setLoading(false);
      }
    },
    [loading, sessionId, addAssistantMessage, consumeStream]
  );

  const close = useCallback(async () => {
    if (!sessionId || loading) return;
    setLoading(true);
    try {
      const { session_id: closeId } = await closeSession(sessionId);
      setSessionId(null);
      const assistantId = addAssistantMessage();
      consumeStream(closeId, assistantId);
    } catch {
      setLoading(false);
    }
  }, [sessionId, loading, addAssistantMessage, consumeStream]);

  return { messages, loading, send, close, resolveApproval };
}

import type { Message } from "../../hooks/useChat";
import ApprovalGate from "../Approval/ApprovalGate";

interface Props {
  message: Message;
  onApprovalResolved: (approvalId: string) => void;
}

export default function ChatMessage({ message, onApprovalResolved }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser ? "bg-indigo-600 text-white" : "bg-zinc-800 text-zinc-100"
        }`}
      >
        {message.content || (
          <span className="inline-block w-2 h-4 bg-zinc-500 animate-pulse rounded" />
        )}

        {message.approvalRequest && (
          <ApprovalGate
            request={message.approvalRequest}
            resolved={!!message.approvalResolved}
            onResolved={onApprovalResolved}
          />
        )}
      </div>
    </div>
  );
}

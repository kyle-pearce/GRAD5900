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
          <span className="flex items-center gap-2 text-zinc-400 text-xs">
            <span className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" />
            </span>
            Generating… (local model, ~30–60 s)
          </span>
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

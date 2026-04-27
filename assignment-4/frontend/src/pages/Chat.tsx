import { useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/Chat/ChatWindow";
import KnowledgePanel from "../components/Knowledge/KnowledgePanel";
import { useChat } from "../hooks/useChat";

export default function Chat() {
  const { messages, loading, send, close, resolveApproval } = useChat();
  const [activePanel, setActivePanel] = useState<"chat" | "knowledge">("chat");

  const handleSkillClick = (skill: string) => {
    setActivePanel("chat");
    send("", skill);
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <Sidebar
        onSkillClick={handleSkillClick}
        onClose={close}
        onKnowledgeClick={() =>
          setActivePanel((p) => (p === "knowledge" ? "chat" : "knowledge"))
        }
        activePanel={activePanel}
        loading={loading}
      />

      <main className="flex-1 flex flex-col min-w-0">
        {activePanel === "chat" ? (
          <ChatWindow
            messages={messages}
            loading={loading}
            onApprovalResolved={resolveApproval}
            onSend={(text) => send(text)}
          />
        ) : (
          <KnowledgePanel />
        )}
      </main>
    </div>
  );
}

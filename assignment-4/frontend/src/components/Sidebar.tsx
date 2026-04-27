import { resetOnboarding } from "../api/client";

const SKILLS = [
  { name: "standup", label: "Standup", emoji: "🟢", desc: "Daily check-in" },
  { name: "sync", label: "Sync", emoji: "📋", desc: "Meeting capture" },
  { name: "refinement", label: "Refinement", emoji: "📅", desc: "Weekly planning" },
  { name: "one_on_one", label: "1:1", emoji: "🤝", desc: "1:1 prep" },
  { name: "email", label: "Email", emoji: "✉️", desc: "Draft a reply" },
];

interface Props {
  onSkillClick: (skill: string) => void;
  onClose: () => void;
  onKnowledgeClick: () => void;
  activePanel: "chat" | "knowledge";
  loading: boolean;
}

export default function Sidebar({ onSkillClick, onClose, onKnowledgeClick, activePanel, loading }: Props) {
  const handleReset = async () => {
    await resetOnboarding();
    window.location.reload();
  };

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-zinc-950 border-r border-zinc-800">
      <div className="px-4 pt-6 pb-4 border-b border-zinc-800">
        <h1 className="text-white font-semibold text-base leading-tight">Personal Assistant</h1>
        <p className="text-zinc-500 text-xs mt-0.5">Powered by Ollama</p>
      </div>

      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        <p className="text-zinc-600 text-xs uppercase tracking-widest mb-2 px-2">Skills</p>
        {SKILLS.map((skill) => (
          <button
            key={skill.name}
            onClick={() => onSkillClick(skill.name)}
            disabled={loading}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-left hover:bg-zinc-800 disabled:opacity-40 transition group"
          >
            <span className="text-base">{skill.emoji}</span>
            <div>
              <div className="text-sm text-zinc-200 font-medium">{skill.label}</div>
              <div className="text-xs text-zinc-500">{skill.desc}</div>
            </div>
          </button>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-zinc-800 flex flex-col gap-2">
        <button
          onClick={onKnowledgeClick}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-left hover:bg-zinc-800 transition ${
            activePanel === "knowledge" ? "bg-zinc-800" : ""
          }`}
        >
          <span className="text-base">🧠</span>
          <div className="text-sm text-zinc-200 font-medium">Knowledge</div>
        </button>

        <button
          onClick={onClose}
          disabled={loading}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-left hover:bg-zinc-800 disabled:opacity-40 transition"
        >
          <span className="text-base">📌</span>
          <div className="text-sm text-zinc-200 font-medium">Close Session</div>
        </button>

        <button
          onClick={handleReset}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-left hover:bg-zinc-800 transition"
        >
          <span className="text-base">⚙️</span>
          <div className="text-sm text-zinc-500">Reset context</div>
        </button>
      </div>
    </aside>
  );
}

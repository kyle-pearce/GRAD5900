import { useState } from "react";

const QUESTIONS = [
  {
    key: "role_goals",
    label: "What is your role and what are you trying to accomplish?",
    placeholder: "e.g. I'm a grad student in Applied GenAI. My goals are to complete the course, build a real AI system I use daily, and develop my understanding of agentic architectures.",
  },
  {
    key: "projects",
    label: "What are your active projects right now?",
    placeholder: "e.g. Assignment 4 (due end of April), researching RAG architectures for my thesis, and a side project building a local knowledge base tool.",
  },
  {
    key: "writing_style",
    label: "How would you describe your writing and communication style?",
    placeholder: "e.g. Direct and concise. I prefer short paragraphs and bullet points over long prose. I avoid jargon and I never use filler phrases like 'I hope this email finds you well'.",
  },
  {
    key: "email_prefs",
    label: "What are your email habits and preferences?",
    placeholder: "e.g. I respond to important emails within 24 hours. I prefer to end emails with a clear next step. I tend to be informal with colleagues but more formal with professors.",
  },
  {
    key: "mental_model",
    label: "How do you tend to make decisions? Any known blind spots?",
    placeholder: "e.g. I tend to over-research before deciding. I sometimes delay hard conversations. I'm better at starting projects than finishing them — I need to watch for that.",
  },
];

interface Props {
  onSubmit: (answers: Record<string, string>) => void;
  loading: boolean;
}

export default function ContextForm({ onSubmit, loading }: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [step, setStep] = useState(0);

  const current = QUESTIONS[step];
  const isLast = step === QUESTIONS.length - 1;

  const handleNext = () => {
    if (isLast) {
      onSubmit(answers);
    } else {
      setStep((s) => s + 1);
    }
  };

  const canAdvance = (answers[current.key] ?? "").trim().length > 10;

  return (
    <div className="flex flex-col gap-6 w-full max-w-xl">
      <div className="flex items-center gap-3">
        {QUESTIONS.map((_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-all ${
              i <= step ? "bg-indigo-500" : "bg-zinc-700"
            }`}
          />
        ))}
      </div>

      <h2 className="text-xl font-semibold text-white">{current.label}</h2>

      <textarea
        className="bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none min-h-[120px]"
        placeholder={current.placeholder}
        value={answers[current.key] ?? ""}
        onChange={(e) =>
          setAnswers((prev) => ({ ...prev, [current.key]: e.target.value }))
        }
        disabled={loading}
      />

      <div className="flex justify-between items-center">
        {step > 0 ? (
          <button
            onClick={() => setStep((s) => s - 1)}
            disabled={loading}
            className="text-sm text-zinc-500 hover:text-zinc-300 transition"
          >
            ← Back
          </button>
        ) : (
          <span />
        )}
        <button
          onClick={handleNext}
          disabled={!canAdvance || loading}
          className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm rounded-xl transition"
        >
          {isLast ? (loading ? "Generating…" : "Generate my context") : "Next →"}
        </button>
      </div>
    </div>
  );
}

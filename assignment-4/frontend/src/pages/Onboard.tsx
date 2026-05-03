import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PathSelector from "../components/Onboarding/PathSelector";
import ContextForm from "../components/Onboarding/ContextForm";
import { useDefaultContext, saveCustomContext } from "../api/client";

type Step = "choose" | "form" | "loading" | "done";


export default function Onboard({ onComplete }: { onComplete?: () => void }) {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("choose");
  const [error, setError] = useState<string | null>(null);

  const handleUseDefaults = async () => {
    setStep("loading");
    try {
      const result = await useDefaultContext();
      if (result.missing_sources?.length > 0) {
        setError(
          `Some default files were not found at the expected WSL2 paths:\n${result.missing_sources.join("\n")}\n\nPlaceholders were used instead — edit context/ to fill them in.`
        );
      }
      setStep("done");
    } catch {
      setError("Failed to load defaults. Is the backend running?");
      setStep("choose");
    }
  };

  const handleCustomSubmit = async (answers: Record<string, string>) => {
    setStep("loading");
    try {
      await saveCustomContext(answers as Parameters<typeof saveCustomContext>[0]);
      setStep("done");
    } catch {
      setError("Failed to generate context. Is the backend running?");
      setStep("form");
    }
  };

  if (step === "done") {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-6">
        <div className="flex flex-col items-center gap-6 max-w-md text-center">
          <div className="text-5xl">✅</div>
          <h2 className="text-2xl font-semibold text-white">You're all set</h2>
          {error && (
            <p className="text-amber-400 text-sm bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 text-left whitespace-pre-wrap">
              {error}
            </p>
          )}
          <p className="text-zinc-400 text-sm">
            Your context files are ready. The assistant will use them in every skill.
          </p>
          <button
            onClick={() => { onComplete?.(); navigate("/"); }}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition"
          >
            Open the assistant →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-6">
      <div className="w-full max-w-xl">
        {step === "choose" && (
          <PathSelector
            onUseDefaults={handleUseDefaults}
            onCustomize={() => setStep("form")}
            loading={false}
          />
        )}
        {step === "form" && (
          <ContextForm onSubmit={handleCustomSubmit} loading={false} />
        )}
        {step === "loading" && (
          <div className="text-center text-zinc-400 text-sm animate-pulse">
            Generating your context files…
          </div>
        )}
        {error && step !== "done" && (
          <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
        )}
      </div>
    </div>
  );
}

interface Props {
  onUseDefaults: () => void;
  onCustomize: () => void;
  loading: boolean;
}

export default function PathSelector({ onUseDefaults, onCustomize, loading }: Props) {
  return (
    <div className="flex flex-col gap-6 w-full max-w-xl">
      <h2 className="text-2xl font-semibold text-white text-center">Set up your context</h2>
      <p className="text-zinc-400 text-center text-sm">
        The assistant uses personal context files to tailor every skill to you. Choose how to get started.
      </p>

      <button
        onClick={onUseDefaults}
        disabled={loading}
        className="flex flex-col gap-1 p-5 rounded-2xl border border-indigo-500/40 bg-indigo-500/10 hover:bg-indigo-500/20 disabled:opacity-40 transition text-left"
      >
        <span className="text-white font-semibold">Use default context (quick start)</span>
        <span className="text-zinc-400 text-sm">
          Load Kyle's pre-written writing style, email preferences, and mental model. Takes 5 seconds.
        </span>
      </button>

      <button
        onClick={onCustomize}
        disabled={loading}
        className="flex flex-col gap-1 p-5 rounded-2xl border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40 transition text-left"
      >
        <span className="text-white font-semibold">Build your own context</span>
        <span className="text-zinc-400 text-sm">
          Answer 5 short questions. The assistant generates your context files using AI. Takes 2–3 minutes.
        </span>
      </button>
    </div>
  );
}

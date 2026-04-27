import { useState } from "react";
import type { ApprovalRequest } from "../../hooks/useChat";
import { respondToApproval } from "../../api/client";

interface Props {
  request: ApprovalRequest;
  resolved: boolean;
  onResolved: (approvalId: string) => void;
}

export default function ApprovalGate({ request, resolved, onResolved }: Props) {
  const [outcome, setOutcome] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const respond = async (o: "approved" | "cancelled") => {
    setBusy(true);
    try {
      const result = await respondToApproval(request.id, o);
      setOutcome(o === "approved" ? `Draft saved to ${result.saved_to ?? "disk"}` : "Draft discarded");
      onResolved(request.id);
    } catch {
      setOutcome("Something went wrong.");
    } finally {
      setBusy(false);
    }
  };

  if (outcome) {
    return (
      <div className="mt-3 rounded-xl border border-zinc-700 bg-zinc-800/50 px-4 py-2 text-xs text-zinc-400">
        {outcome}
      </div>
    );
  }

  if (resolved) return null;

  return (
    <div className="mt-3 rounded-xl border border-amber-500/40 bg-amber-500/10 p-4">
      <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide mb-1">
        Approval needed — Tier {request.tier}
      </p>
      <p className="text-sm text-zinc-200 mb-3">{request.description}</p>
      <div className="flex gap-2">
        <button
          onClick={() => respond("approved")}
          disabled={busy}
          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs rounded-lg transition"
        >
          Save Draft
        </button>
        <button
          onClick={() => respond("cancelled")}
          disabled={busy}
          className="px-3 py-1.5 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-40 text-zinc-200 text-xs rounded-lg transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

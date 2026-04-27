import { useState, useEffect } from "react";
import { queryKnowledge, ingestPath, getKnowledgeStats } from "../../api/client";

export default function KnowledgePanel() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string>("");
  const [ingestPathValue, setIngestPathValue] = useState("");
  const [stats, setStats] = useState<{ document_count: number; collection: string } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getKnowledgeStats().then(setStats).catch(() => {});
  }, []);

  const handleQuery = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await queryKnowledge(query);
      setResult(data.chunks?.join("\n\n---\n\n") ?? "No results.");
    } catch {
      setResult("Error querying knowledge base.");
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    if (!ingestPathValue.trim()) return;
    setLoading(true);
    try {
      const data = await ingestPath(ingestPathValue.trim());
      setResult(`Ingested ${data.chunks_ingested} chunks from ${data.path}`);
      const updated = await getKnowledgeStats();
      setStats(updated);
    } catch {
      setResult("Error ingesting path.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4 text-sm">
      <h2 className="text-zinc-300 font-semibold text-base">Knowledge Base</h2>

      {stats && (
        <p className="text-zinc-500 text-xs">
          {stats.document_count} chunks indexed in <code className="text-zinc-400">{stats.collection}</code>
        </p>
      )}

      <div className="flex flex-col gap-2">
        <input
          className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="Search your knowledge base…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuery()}
        />
        <button
          onClick={handleQuery}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white py-1.5 rounded-lg transition"
        >
          Search
        </button>
      </div>

      <div className="border-t border-zinc-800 pt-4 flex flex-col gap-2">
        <p className="text-zinc-500 text-xs">Ingest a file or directory path:</p>
        <input
          className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="/path/to/file.md or /path/to/dir"
          value={ingestPathValue}
          onChange={(e) => setIngestPathValue(e.target.value)}
        />
        <button
          onClick={handleIngest}
          disabled={loading}
          className="bg-zinc-700 hover:bg-zinc-600 disabled:opacity-40 text-white py-1.5 rounded-lg transition"
        >
          Ingest
        </button>
      </div>

      {result && (
        <div className="mt-2 text-xs text-zinc-400 bg-zinc-900 rounded-lg p-3 overflow-y-auto max-h-64 whitespace-pre-wrap">
          {result}
        </div>
      )}
    </div>
  );
}

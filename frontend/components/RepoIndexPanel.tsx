"use client";

import { useState } from "react";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

import { indexRepository } from "@/lib/api";

interface Props {
  onIndexed: (repoName: string) => void;
}

type Status = "idle" | "indexing" | "indexed" | "error";

export default function RepoIndexPanel({ onIndexed }: Props) {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  const [stats, setStats] = useState<{
    files: number;
    chunks: number;
  } | null>(null);

  const isValidGithubUrl = (value: string) => {
    return /^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/.test(
      value.trim()
    );
  };

  const handleIndex = async () => {
    if (!isValidGithubUrl(url)) {
      setStatus("error");
      setError("Please enter a valid GitHub repository URL.");
      return;
    }

    setStatus("indexing");
    setError(null);
    setStats(null);

    try {
      const result = await indexRepository(url.trim());

      setStats({
        files: result.files_indexed,
        chunks: result.chunks_stored,
      });

      setStatus("indexed");

      onIndexed(result.repo_name);
    } catch (err: any) {
      setStatus("error");
      setError(err.message || "Failed to index repository.");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow border p-6 space-y-4">

      <div>
        <h2 className="text-lg font-semibold">
          Repository Index
        </h2>

        <p className="text-sm text-gray-500 mt-1">
          Paste any public GitHub repository URL and index it for AI search.
        </p>
      </div>

      <div className="flex gap-3">

        <input
          type="text"
          className="flex-1 rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black"
          placeholder="https://github.com/owner/repository"
          value={url}
          disabled={status === "indexing"}
          onChange={(e) => setUrl(e.target.value)}
        />

        <button
          onClick={handleIndex}
          disabled={status === "indexing" || !url}
          className="bg-black text-white rounded-lg px-5 py-2 text-sm font-medium disabled:opacity-50 flex items-center gap-2"
        >
          {status === "indexing" && (
            <Loader2 className="w-4 h-4 animate-spin" />
          )}

          {status === "indexing"
            ? "Indexing..."
            : "Index Repository"}
        </button>

      </div>

      {status === "indexing" && (
        <p className="text-sm text-gray-500">
          Cloning repository, parsing files, generating embeddings and
          storing vectors...
        </p>
      )}

      {status === "indexed" && stats && (
        <div className="flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 p-3 text-green-700">

          <CheckCircle2 className="w-5 h-5" />

          <div>
            <p className="font-medium">
              Repository indexed successfully!
            </p>

            <p className="text-sm">
              Files Indexed: <strong>{stats.files}</strong>
              {" • "}
              Chunks Stored: <strong>{stats.chunks}</strong>
            </p>
          </div>

        </div>
      )}

      {status === "error" && error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 p-3 text-red-700">

          <XCircle className="w-5 h-5" />

          <span>{error}</span>

        </div>
      )}

    </div>
  );
}
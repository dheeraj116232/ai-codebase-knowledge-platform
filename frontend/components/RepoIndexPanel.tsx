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
    <div className="space-y-5 rounded-xl border p-6 bg-white shadow-sm">

      <div>
        <h2 className="text-xl font-semibold">
          Repository Index
        </h2>

        <p className="text-sm text-gray-500 mt-1">
          Paste a public GitHub repository URL and index it for semantic AI search.
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
          onKeyDown={(e) => {
            if (e.key === "Enter" && status !== "indexing" && url) {
              handleIndex();
            }
          }}
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

      {/* Render Free cold start notice */}

      {status !== "indexing" && (
        <p className="text-xs text-gray-400">
          ⚡ First request after inactivity may take up to a minute because the backend runs on Render's free tier.
        </p>
      )}

      {/* Progress */}

      {status === "indexing" && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
          <p className="text-sm text-blue-700 font-medium">
            Indexing repository...
          </p>

          <p className="text-xs text-blue-600 mt-1">
            Cloning repository, parsing files, generating embeddings and storing vectors.
            This usually takes 10–60 seconds depending on repository size.
          </p>
        </div>
      )}

      {/* Success */}

      {status === "indexed" && stats && (
        <div className="flex items-center gap-3 rounded-lg bg-green-50 border border-green-200 p-4 text-green-700">

          <CheckCircle2 className="w-6 h-6 shrink-0" />

          <div>
            <p className="font-semibold">
              Repository indexed successfully!
            </p>

            <p className="text-sm mt-1">
              Files Indexed: <strong>{stats.files}</strong>
              {" • "}
              Chunks Stored: <strong>{stats.chunks}</strong>
            </p>
          </div>

        </div>
      )}

      {/* Error */}

      {status === "error" && error && (
        <div className="flex items-center gap-3 rounded-lg bg-red-50 border border-red-200 p-4 text-red-700">

          <XCircle className="w-6 h-6 shrink-0" />

          <span>{error}</span>

        </div>
      )}

    </div>
  );
}
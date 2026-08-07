"use client";

import { useEffect, useState } from "react";

import RepoIndexPanel from "@/components/RepoIndexPanel";
import ChatWindow from "@/components/ChatWindow";

export default function Home() {
  const [repoName, setRepoNameState] = useState<string | null>(null);

  // Restore repository after page refresh
  useEffect(() => {
    const savedRepo = localStorage.getItem("current_repo");
    if (savedRepo) {
      setRepoNameState(savedRepo);
    }
  }, []);

  // Save repository whenever indexing completes
  const setRepoName = (name: string) => {
    localStorage.setItem("current_repo", name);
    setRepoNameState(name);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-bold">
            AI Codebase Knowledge Platform
          </h1>

          <p className="mt-2 text-gray-600">
            Paste a GitHub repository, index it, and ask AI questions about how
            the code works.
          </p>
        </div>

        <RepoIndexPanel onIndexed={setRepoName} />

        <ChatWindow repoName={repoName} />
      </div>
    </main>
  );
}
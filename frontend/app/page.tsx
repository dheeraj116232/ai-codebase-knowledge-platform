"use client";

import { useEffect, useState } from "react";

import RepoIndexPanel from "@/components/RepoIndexPanel";
import ChatWindow from "@/components/ChatWindow";
import MermaidDiagram from "@/components/MermaidDiagram";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type DiagramData = {
  mermaid_syntax: string;
  caption: string;
};

export default function Home() {
  const [repoName, setRepoNameState] = useState<string | null>(null);
  const [diagram, setDiagram] = useState<DiagramData | null>(null);
  const [diagramLoading, setDiagramLoading] = useState(false);
  const [diagramError, setDiagramError] = useState<string | null>(null);

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

  // Fetch Mermaid architecture diagram whenever a repository is indexed
  useEffect(() => {
    if (!repoName) {
      setDiagram(null);
      return;
    }

    const loadDiagram = async () => {
      setDiagramLoading(true);
      setDiagramError(null);

      try {
        const response = await fetch(
          `${API_BASE}/diagram/${encodeURIComponent(repoName)}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch diagram: ${response.status}`);
        }

        const data: DiagramData = await response.json();

        setDiagram(data);
      } catch (error) {
        console.error("Diagram fetch error:", error);
        setDiagramError("Unable to load the architecture diagram.");
        setDiagram(null);
      } finally {
        setDiagramLoading(false);
      }
    };

    loadDiagram();
  }, [repoName]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-8">

        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold">
            AI Codebase Knowledge Platform
          </h1>

          <p className="mt-2 text-gray-600">
            Paste a GitHub repository, index it, and ask AI questions about
            how the code works.
          </p>
        </div>

        {/* Repository indexing */}
        <RepoIndexPanel onIndexed={setRepoName} />

        {/* Architecture Diagram */}
        {repoName && (
          <section className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="mb-4">
              <h2 className="text-2xl font-semibold">
                Repository Architecture
              </h2>

              <p className="mt-1 text-sm text-gray-500">
                Visual representation of the repository dependency graph.
              </p>
            </div>

            {diagramLoading && (
              <p className="text-sm text-gray-500">
                Generating architecture diagram...
              </p>
            )}

            {diagramError && (
              <p className="text-sm text-red-500">
                {diagramError}
              </p>
            )}

            {diagram && !diagramLoading && (
              <>
                <div className="overflow-x-auto rounded-lg border bg-gray-50 p-4">
                  <MermaidDiagram
                    syntax={diagram.mermaid_syntax}
                  />
                </div>

                {diagram.caption && (
                  <p className="mt-3 text-sm text-gray-600">
                    {diagram.caption}
                  </p>
                )}
              </>
            )}
          </section>
        )}

        {/* AI Chat */}
        <ChatWindow repoName={repoName} />

      </div>
    </main>
  );
}
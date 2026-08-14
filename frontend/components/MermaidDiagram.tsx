// frontend/components/MermaidDiagram.tsx
"use client";
import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, theme: "neutral" });

export default function MermaidDiagram({ syntax }: { syntax: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && syntax) {
      const id = `mermaid-${Date.now()}`;
      mermaid.render(id, syntax).then(({ svg }) => {
        if (ref.current) ref.current.innerHTML = svg;
      }).catch((err) => {
        console.error("Mermaid render error:", err);
        if (ref.current) ref.current.innerHTML = `<p class="text-red-500 text-sm">Failed to render diagram.</p>`;
      });
    }
  }, [syntax]);

  return <div ref={ref} className="overflow-x-auto" />;
}
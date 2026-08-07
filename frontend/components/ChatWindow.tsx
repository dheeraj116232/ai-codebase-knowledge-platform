// frontend/components/ChatWindow.tsx
"use client";
import { useState, useRef, useEffect } from "react";
import { Message } from "@/lib/types";
import { askQuestion } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import { Send, Loader2 } from "lucide-react";

interface Props {
  repoName: string | null;
}

export default function ChatWindow({ repoName }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !repoName || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const result = await askQuestion(userMessage.content, repoName);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          timestamp: Date.now(),
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: err.message || "Something went wrong. Please try again.",
          timestamp: Date.now(),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[600px] border rounded-lg bg-white">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 text-sm mt-20">
            {repoName
              ? "Ask a question about this repository to get started."
              : "Index a repository above to start chatting."}
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              Thinking...
            </div>
          </div>
        )}

        <div ref={scrollRef} />
      </div>

      <div className="border-t p-3 flex gap-2">
        <textarea
          className="flex-1 border rounded px-3 py-2 text-sm resize-none"
          rows={1}
          placeholder={repoName ? "Ask about this codebase..." : "Index a repository first"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!repoName || loading}
        />
        <button
          onClick={handleSend}
          disabled={!repoName || !input.trim() || loading}
          className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
// frontend/components/MessageBubble.tsx
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/lib/types";
import { FileCode } from "lucide-react";

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 text-sm ${
          isUser
            ? "bg-black text-white"
            : message.isError
            ? "bg-red-50 text-red-700 border border-red-200"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-pre:bg-gray-900 prose-pre:text-gray-100">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 space-y-1">
            <p className="text-xs font-medium text-gray-500">Sources</p>
            {message.sources.map((s, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-gray-600">
                <FileCode className="w-3 h-3" />
                <code>{s.file_path}</code>
                <span className="text-gray-400">lines {s.lines}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
// frontend/lib/types.ts
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: number;
  isError?: boolean;
}

export interface Source {
  file_path: string;
  lines: string;
}

export type IndexStatus = "idle" | "indexing" | "indexed" | "error";
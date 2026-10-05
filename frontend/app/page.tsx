"use client";

import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

const API_URL = "http://127.0.0.1:8001/rag/hybrid";

type ChatMessage = {
  user: string;
  assistant: string;
};

type Product = {
  id: string;
  name: string;
  manufacturer: string;
  category: string;
  description?: string | null;
  price: number;
  score: number;
};

type ChatDisplayMessage = {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  searchQuery?: string;
};

type ApiResponse = {
  question: string;
  search_query: string;
  answer: string;
  products: Product[];
};

const INITIAL_MESSAGE: ChatDisplayMessage = {
  role: "assistant",
  content:
    "Hello! I’m your Product RAG Assistant. Ask me about products, prices, manufacturers, categories, or specifications.",
};

export default function Home() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [messages, setMessages] = useState<ChatDisplayMessage[]>([
    INITIAL_MESSAGE,
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  function startNewChat() {
    setQuestion("");
    setHistory([]);
    setMessages([INITIAL_MESSAGE]);
    setError("");

    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  }

  async function sendQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          size: 5,
          history,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `API request failed with status ${response.status}`,
        );
      }

      const data: ApiResponse = await response.json();

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          products: data.products,
          searchQuery: data.search_query,
        },
      ]);

      setHistory((current) => [
        ...current,
        {
          user: trimmedQuestion,
          assistant: data.answer,
        },
      ]);
    } catch (requestError) {
      console.error(requestError);

      setError(
        "Unable to connect to the RAG API. Make sure the backend is running on port 8001.",
      );
    } finally {
      setLoading(false);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 0);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-100 px-4 py-6">
      <div className="mx-auto flex h-[calc(100vh-3rem)] max-w-4xl flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
        <header className="flex items-center justify-between border-b border-zinc-200 px-6 py-5">
          <div>
            <h1 className="text-xl font-semibold text-zinc-900">
              Product RAG Assistant
            </h1>

            <p className="mt-1 text-sm text-zinc-500">
              Search products using hybrid BM25 + semantic retrieval.
            </p>
          </div>

          <button
            type="button"
            onClick={startNewChat}
            disabled={loading}
            className="rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            New Chat
          </button>
        </header>

        <section className="flex-1 space-y-5 overflow-y-auto p-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >
              <div className="max-w-[85%]">
                {/* Chat message */}
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-6 ${
                    message.role === "user"
                      ? "bg-zinc-900 text-white"
                      : "bg-zinc-100 text-zinc-800"
                  }`}
                >
                  {message.content}
                </div>

                {/* Search information */}
                {message.role === "assistant" &&
                  message.searchQuery && (
                    <div className="mt-3 rounded-xl border border-blue-100 bg-blue-50 p-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-semibold uppercase tracking-wide text-blue-700">
                          Hybrid Search
                        </span>

                        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700">
                          BM25 + Semantic
                        </span>
                      </div>

                      <p className="mt-2 break-words text-xs text-blue-900">
                        <span className="font-semibold">
                          Search query:
                        </span>{" "}
                        {message.searchQuery}
                      </p>
                    </div>
                  )}

                {/* Retrieved products */}
                {message.role === "assistant" &&
                  message.products &&
                  message.products.length > 0 && (
                    <div className="mt-3 space-y-3">
                      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                        Retrieved Products
                      </p>

                      {message.products.map((product) => (
                        <div
                          key={product.id}
                          className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm transition hover:shadow-md"
                        >
                          <h2 className="text-sm font-semibold leading-5 text-zinc-900">
                            {product.name}
                          </h2>

                          <div className="mt-3 space-y-2 text-sm text-zinc-600">
                            <p>
                              <span className="font-medium text-zinc-800">
                                Manufacturer:
                              </span>{" "}
                              {product.manufacturer}
                            </p>

                            <p>
                              <span className="font-medium text-zinc-800">
                                Category:
                              </span>{" "}
                              {product.category}
                            </p>

                            <p>
                              <span className="font-medium text-zinc-800">
                                Price:
                              </span>{" "}
                              ${product.price.toLocaleString()}
                            </p>

                            {product.description && (
                              <div>
                                <p className="font-medium text-zinc-800">
                                  Description:
                                </p>

                                <p className="mt-1 leading-5 text-zinc-500">
                                  {product.description}
                                </p>
                              </div>
                            )}

                            <p className="pt-1 text-xs text-zinc-400">
                              Hybrid RRF score:{" "}
                              {product.score.toFixed(6)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
              </div>
            </div>
          ))}

          {/* Animated loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-3 rounded-2xl bg-zinc-100 px-4 py-3">
                <div className="flex items-center gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
                </div>

                <span className="text-sm text-zinc-500">
                  Searching product data...
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Automatic scroll target */}
          <div ref={messagesEndRef} />
        </section>

        <form
          onSubmit={sendQuestion}
          className="border-t border-zinc-200 bg-white p-4"
        >
          <div className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about a product..."
              disabled={loading}
              className="flex-1 rounded-xl border border-zinc-300 bg-white px-4 py-3 text-sm text-zinc-900 caret-zinc-900 placeholder:text-zinc-400 outline-none transition focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 disabled:bg-zinc-100 disabled:text-zinc-500"
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="rounded-xl bg-zinc-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:bg-zinc-300"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

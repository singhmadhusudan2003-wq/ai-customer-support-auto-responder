import React, { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Send, Paperclip, Sparkles, Loader2 } from "lucide-react";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import ChatBubble from "../components/ChatBubble";
import TypingIndicator from "../components/TypingIndicator";
import api from "../api/axios";

export default function Chat() {
  const [searchParams] = useSearchParams();
  const initialConversationId = searchParams.get("conversation_id");

  const [conversationId, setConversationId] = useState(initialConversationId || null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    api.get("/history/suggestions").then((res) => setSuggestions(res.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (initialConversationId) {
      loadConversation(initialConversationId);
    }
  }, [initialConversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const loadConversation = async (id) => {
    try {
      const { data } = await api.get(`/history/${id}`);
      setConversationId(data.id);
      setMessages(data.messages);
    } catch {
      // ignore, start fresh
    }
  };

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || sending) return;

    const optimisticUserMsg = {
      id: `temp-${Date.now()}`,
      sender: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);
    setInput("");
    setSending(true);

    try {
      const { data } = await api.post("/chat", {
        message: trimmed,
        conversation_id: conversationId,
      });
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          id: data.message_id,
          sender: "ai",
          content: data.reply,
          intent: data.intent,
          sentiment: data.sentiment,
          confidence: data.confidence,
          escalated: data.escalated,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: "ai",
          content: "Sorry, something went wrong reaching the AI service. Please try again.",
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const { data } = await api.post("/chat/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setInput((prev) => `${prev}${prev ? "\n\n" : ""}[Attached: ${data.filename}]\n${data.extracted_text}`);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to process file");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleFeedback = async (messageId, rating) => {
    if (messageId.startsWith("temp-") || messageId.startsWith("error-")) return;
    try {
      await api.post("/feedback", { message_id: messageId, rating });
    } catch {
      // ignore
    }
  };

  return (
    <Layout>
      <Navbar title="Chat" subtitle="Ask anything — orders, refunds, technical issues, and more" />

      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-100 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
                <Sparkles size={26} />
              </div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                How can I help you today?
              </h2>
              <p className="mt-1 max-w-sm text-sm text-gray-500 dark:text-gray-400">
                Ask about orders, refunds, technical issues, or your account. I can also pull
                context from an uploaded PDF or TXT file.
              </p>
              {suggestions.length > 0 && (
                <div className="mt-6 grid max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
                  {suggestions.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-left text-sm text-gray-700 shadow-sm transition hover:border-brand-300 hover:bg-brand-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((m) => (
              <ChatBubble key={m.id} message={m} onFeedback={m.sender === "ai" ? handleFeedback : null} />
            ))}
            {sending && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-900">
          <div className="mx-auto flex max-w-3xl items-end gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt"
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-gray-200 text-gray-500 transition hover:bg-gray-100 disabled:opacity-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
              title="Attach PDF or TXT file"
            >
              {uploading ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
            </button>
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Type your message..."
              className="max-h-32 flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:ring-brand-900"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition hover:bg-brand-700 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

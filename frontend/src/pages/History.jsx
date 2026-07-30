import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageSquare, Trash2, AlertTriangle } from "lucide-react";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import api from "../api/axios";
import { format } from "date-fns";

export default function History() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    api
      .get("/history")
      .then((res) => setConversations(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Delete this conversation? This cannot be undone.")) return;
    await api.delete(`/history/${id}`);
    load();
  };

  return (
    <Layout>
      <Navbar title="Conversation History" subtitle="Review and revisit your past conversations" />
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <MessageSquare className="mb-3 text-gray-300 dark:text-gray-700" size={40} />
            <p className="text-sm text-gray-500 dark:text-gray-400">No conversations yet. Start a new chat!</p>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-3">
            {conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => navigate(`/chat?conversation_id=${c.id}`)}
                className="flex cursor-pointer items-center justify-between rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:border-brand-300 dark:border-gray-800 dark:bg-gray-900"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-medium text-gray-900 dark:text-white">{c.title}</p>
                    {c.escalated && (
                      <span className="flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                        <AlertTriangle size={10} /> Escalated
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {c.message_count} messages · Updated {format(new Date(c.updated_at), "MMM d, yyyy h:mm a")}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDelete(c.id, e)}
                  className="ml-3 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg text-gray-400 transition hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}

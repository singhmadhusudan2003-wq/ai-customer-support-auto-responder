import React, { useEffect, useMemo, useState } from "react";
import { Search, Trash2, AlertTriangle, MessageSquare, X } from "lucide-react";
import { format } from "date-fns";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import ChatBubble from "../components/ChatBubble";
import api from "../api/axios";

export default function Conversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [escalatedOnly, setEscalatedOnly] = useState(false);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .get("/admin/conversations")
      .then((res) => setConversations(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = useMemo(() => {
    return conversations.filter((c) => {
      const matchesSearch =
        !search ||
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        (c.customer_email || "").toLowerCase().includes(search.toLowerCase()) ||
        (c.customer_name || "").toLowerCase().includes(search.toLowerCase());
      const matchesDate = !dateFilter || c.created_at.startsWith(dateFilter);
      const matchesEscalated = !escalatedOnly || c.escalated;
      return matchesSearch && matchesDate && matchesEscalated;
    });
  }, [conversations, search, dateFilter, escalatedOnly]);

  const openConversation = async (id) => {
    setSelected(id);
    const { data } = await api.get(`/admin/conversations/${id}`);
    setDetail(data);
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Delete this conversation permanently?")) return;
    await api.delete(`/admin/conversations/${id}`);
    if (selected === id) {
      setSelected(null);
      setDetail(null);
    }
    load();
  };

  return (
    <Layout>
      <Navbar title="All Conversations" subtitle="Search, filter, and review every customer conversation" />
      <div className="flex flex-1 overflow-hidden">
        <div className="flex w-full flex-col overflow-hidden border-r border-gray-200 dark:border-gray-800 lg:w-1/2">
          <div className="flex flex-col gap-3 border-b border-gray-200 p-4 dark:border-gray-800 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by title, name, or email..."
                className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            </div>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
            <label className="flex items-center gap-2 text-xs font-medium text-gray-600 dark:text-gray-300">
              <input type="checkbox" checked={escalatedOnly} onChange={(e) => setEscalatedOnly(e.target.checked)} />
              Escalated only
            </label>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <p className="p-4 text-sm text-gray-500 dark:text-gray-400">Loading...</p>
            ) : filtered.length === 0 ? (
              <p className="p-4 text-sm text-gray-500 dark:text-gray-400">No conversations match your filters.</p>
            ) : (
              filtered.map((c) => (
                <div
                  key={c.id}
                  onClick={() => openConversation(c.id)}
                  className={`flex cursor-pointer items-center justify-between border-b border-gray-100 p-4 transition hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50 ${
                    selected === c.id ? "bg-brand-50 dark:bg-brand-900/20" : ""
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{c.title}</p>
                      {c.escalated && (
                        <span className="flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                          <AlertTriangle size={10} /> Escalated
                        </span>
                      )}
                    </div>
                    <p className="mt-0.5 truncate text-xs text-gray-500 dark:text-gray-400">
                      {c.customer_name} · {c.customer_email}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">
                      {c.message_count} messages · {format(new Date(c.updated_at), "MMM d, h:mm a")}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(c.id, e)}
                    className="ml-2 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="hidden flex-1 flex-col overflow-hidden lg:flex">
          {!detail ? (
            <div className="flex h-full flex-col items-center justify-center text-center text-gray-400 dark:text-gray-600">
              <MessageSquare size={36} className="mb-3" />
              <p className="text-sm">Select a conversation to view the full transcript</p>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between border-b border-gray-200 p-4 dark:border-gray-800">
                <div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{detail.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{detail.messages.length} messages</p>
                </div>
                <button onClick={() => { setSelected(null); setDetail(null); }} className="text-gray-400 hover:text-gray-600">
                  <X size={18} />
                </button>
              </div>
              <div className="flex-1 space-y-4 overflow-y-auto p-4">
                {detail.messages.map((m) => (
                  <ChatBubble key={m.id} message={m} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}

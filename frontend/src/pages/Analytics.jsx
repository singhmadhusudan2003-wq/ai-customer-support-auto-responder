import React, { useEffect, useState } from "react";
import { Download, Gauge, Sparkles, Loader2 } from "lucide-react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import api from "../api/axios";

const INTENT_COLORS = ["#6366f1", "#818cf8", "#a5b4fc", "#4f46e5", "#4338ca", "#312e81"];

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playgroundText, setPlaygroundText] = useState("");
  const [playgroundResult, setPlaygroundResult] = useState(null);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    api
      .get("/analytics/summary")
      .then((res) => setSummary(res.data))
      .finally(() => setLoading(false));
  }, []);

  const handleExport = async () => {
    const res = await api.get("/analytics/export/csv", { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "conversations_export.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!playgroundText.trim()) return;
    setPredicting(true);
    try {
      const { data } = await api.post("/chat/predict", { text: playgroundText });
      setPlaygroundResult(data);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <Layout>
      <Navbar
        title="Analytics"
        subtitle="Deep dive into query statistics, confidence, and model performance"
        actions={
          <button
            onClick={handleExport}
            className="flex items-center gap-2 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
          >
            <Download size={16} /> Export CSV
          </button>
        }
      />
      <div className="flex-1 overflow-y-auto p-6">
        {loading || !summary ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading analytics...</p>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <StatCard label="Total Messages" value={summary.total_messages} icon={Sparkles} accent="brand" />
              <StatCard label="Avg AI Confidence" value={Math.round(summary.avg_confidence * 100)} suffix="%" icon={Gauge} accent="green" />
              <StatCard label="Avg Response Time" value={summary.avg_response_time_ms} suffix=" ms" icon={Gauge} accent="amber" />
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">Query Categorization (Intent Volume)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={summary.intent_breakdown} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="intent" width={130} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                    {summary.intent_breakdown.map((_, i) => (
                      <Cell key={i} fill={INTENT_COLORS[i % INTENT_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">Classifier Playground</h3>
              <p className="mb-4 text-xs text-gray-500 dark:text-gray-400">
                Test the intent and sentiment models on any sample text.
              </p>
              <form onSubmit={handlePredict} className="flex flex-col gap-3 sm:flex-row">
                <input
                  value={playgroundText}
                  onChange={(e) => setPlaygroundText(e.target.value)}
                  placeholder="e.g. My order hasn't arrived and I'm getting worried"
                  className="flex-1 rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
                <button
                  type="submit"
                  disabled={predicting}
                  className="flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60"
                >
                  {predicting && <Loader2 size={16} className="animate-spin" />}
                  Predict
                </button>
              </form>
              {playgroundResult && (
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="rounded-xl bg-brand-50 p-4 dark:bg-brand-900/30">
                    <p className="text-xs text-brand-700 dark:text-brand-300">Predicted Intent</p>
                    <p className="text-lg font-bold text-brand-900 dark:text-brand-100">{playgroundResult.intent}</p>
                    <p className="text-xs text-brand-600 dark:text-brand-400">
                      {Math.round(playgroundResult.intent_confidence * 100)}% confidence
                    </p>
                  </div>
                  <div className="rounded-xl bg-gray-100 p-4 dark:bg-gray-800">
                    <p className="text-xs text-gray-600 dark:text-gray-400">Predicted Sentiment</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">{playgroundResult.sentiment}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {Math.round(playgroundResult.sentiment_confidence * 100)}% confidence
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

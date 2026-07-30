import React, { useEffect, useState } from "react";
import {
  MessageSquare,
  Users as UsersIcon,
  AlertTriangle,
  Clock,
  TrendingUp,
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import api from "../api/axios";

const INTENT_COLORS = ["#6366f1", "#818cf8", "#a5b4fc", "#4f46e5", "#4338ca", "#312e81"];
const SENTIMENT_COLORS = { Positive: "#22c55e", Neutral: "#94a3b8", Negative: "#ef4444" };

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/analytics/summary")
      .then((res) => setSummary(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <Navbar title="Admin Dashboard" subtitle="Real-time overview of customer support activity" />
      <div className="flex-1 overflow-y-auto p-6">
        {loading || !summary ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading dashboard...</p>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Total Conversations" value={summary.total_conversations} icon={MessageSquare} accent="brand" />
              <StatCard label="Total Customers" value={summary.total_customers} icon={UsersIcon} accent="green" />
              <StatCard label="Escalation Rate" value={summary.escalation_rate} suffix="%" icon={AlertTriangle} accent="amber" />
              <StatCard label="Avg Response Time" value={summary.avg_response_time_ms} suffix=" ms" icon={Clock} accent="red" />
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
                  <TrendingUp size={16} /> Daily Message Volume
                </h3>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={summary.daily_volume}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">Intent Breakdown</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={summary.intent_breakdown}
                      dataKey="count"
                      nameKey="intent"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label={(d) => d.intent}
                    >
                      {summary.intent_breakdown.map((_, i) => (
                        <Cell key={i} fill={INTENT_COLORS[i % INTENT_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">Sentiment Distribution</h3>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={summary.sentiment_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="sentiment" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {summary.sentiment_breakdown.map((entry, i) => (
                      <Cell key={i} fill={SENTIMENT_COLORS[entry.sentiment] || "#6366f1"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

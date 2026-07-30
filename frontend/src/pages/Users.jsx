import React, { useEffect, useMemo, useState } from "react";
import { Search, Trash2, ShieldCheck, ShieldOff, UserCog } from "lucide-react";
import { format } from "date-fns";
import Layout from "../components/Layout";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";

export default function Users() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .get("/admin/users")
      .then((res) => setUsers(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = useMemo(() => {
    return users.filter(
      (u) =>
        !search ||
        u.name.toLowerCase().includes(search.toLowerCase()) ||
        u.email.toLowerCase().includes(search.toLowerCase())
    );
  }, [users, search]);

  const toggleActive = async (u) => {
    setBusyId(u.id);
    try {
      await api.patch(`/admin/users/${u.id}`, { is_active: !u.is_active });
      load();
    } finally {
      setBusyId(null);
    }
  };

  const toggleRole = async (u) => {
    setBusyId(u.id);
    try {
      const newRole = u.role === "admin" ? "customer" : "admin";
      await api.patch(`/admin/users/${u.id}`, { role: newRole });
      load();
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (u) => {
    if (u.id === currentUser?.id) return;
    if (!confirm(`Delete user "${u.name}"? This will remove all their conversations.`)) return;
    setBusyId(u.id);
    try {
      await api.delete(`/admin/users/${u.id}`);
      load();
    } finally {
      setBusyId(null);
    }
  };

  return (
    <Layout>
      <Navbar title="User Management" subtitle="View, promote, deactivate, or remove platform users" />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name or email..."
              className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">{filtered.length} users</span>
        </div>

        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-500 dark:bg-gray-800/60 dark:text-gray-400">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Joined</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-gray-500">Loading...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-gray-500">No users found.</td>
                </tr>
              ) : (
                filtered.map((u) => (
                  <tr key={u.id} className="text-gray-700 dark:text-gray-300">
                    <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{u.name}</td>
                    <td className="px-4 py-3">{u.email}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          u.role === "admin"
                            ? "bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300"
                            : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          u.is_active
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                            : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
                        }`}
                      >
                        {u.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500 dark:text-gray-400">
                      {format(new Date(u.created_at), "MMM d, yyyy")}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          disabled={busyId === u.id}
                          onClick={() => toggleRole(u)}
                          title="Toggle admin role"
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-brand-50 hover:text-brand-600 disabled:opacity-40 dark:hover:bg-brand-900/30"
                        >
                          <UserCog size={14} />
                        </button>
                        <button
                          disabled={busyId === u.id}
                          onClick={() => toggleActive(u)}
                          title={u.is_active ? "Disable account" : "Activate account"}
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-amber-50 hover:text-amber-600 disabled:opacity-40 dark:hover:bg-amber-900/30"
                        >
                          {u.is_active ? <ShieldOff size={14} /> : <ShieldCheck size={14} />}
                        </button>
                        <button
                          disabled={busyId === u.id || u.id === currentUser?.id}
                          onClick={() => handleDelete(u)}
                          title="Delete user"
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-40 dark:hover:bg-red-950/40"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}

import React from "react";

export default function StatCard({ label, value, icon: Icon, accent = "brand", suffix = "" }) {
  const accentClasses = {
    brand: "bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300",
    green: "bg-green-50 text-green-600 dark:bg-green-900/40 dark:text-green-300",
    amber: "bg-amber-50 text-amber-600 dark:bg-amber-900/40 dark:text-amber-300",
    red: "bg-red-50 text-red-600 dark:bg-red-900/40 dark:text-red-300",
  };

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</p>
        {Icon && (
          <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${accentClasses[accent]}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <p className="mt-3 text-2xl font-bold text-gray-900 dark:text-white">
        {value}
        {suffix}
      </p>
    </div>
  );
}

import React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function Navbar({ title, subtitle, actions }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="flex items-center justify-between border-b border-gray-200 bg-white/80 px-6 py-4 backdrop-blur dark:border-gray-800 dark:bg-gray-900/80">
      <div>
        <h1 className="text-lg font-bold text-gray-900 dark:text-white">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {actions}
        <button
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200 text-gray-600 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}

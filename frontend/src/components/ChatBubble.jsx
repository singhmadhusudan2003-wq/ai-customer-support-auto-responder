import React from "react";
import { Bot, User, AlertTriangle, ThumbsUp, ThumbsDown } from "lucide-react";

const sentimentColors = {
  Positive: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  Neutral: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  Negative: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

export default function ChatBubble({ message, onFeedback }) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 text-white">
          <Bot size={16} />
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? "order-1" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? "rounded-br-sm bg-brand-600 text-white"
              : "rounded-bl-sm bg-white text-gray-800 shadow-sm dark:bg-gray-800 dark:text-gray-100"
          }`}
        >
          {message.content}
        </div>

        {!isUser && (message.intent || message.sentiment) && (
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            {message.intent && (
              <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-medium text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                {message.intent}
              </span>
            )}
            {message.sentiment && (
              <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${sentimentColors[message.sentiment] || ""}`}>
                {message.sentiment}
              </span>
            )}
            {typeof message.confidence === "number" && (
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                {Math.round(message.confidence * 100)}% confidence
              </span>
            )}
            {message.escalated && (
              <span className="flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                <AlertTriangle size={11} /> Escalated
              </span>
            )}
            {onFeedback && (
              <span className="ml-1 flex items-center gap-1">
                <button
                  onClick={() => onFeedback(message.id, 1)}
                  className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-green-600 dark:hover:bg-gray-800"
                  aria-label="Good response"
                >
                  <ThumbsUp size={12} />
                </button>
                <button
                  onClick={() => onFeedback(message.id, -1)}
                  className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-red-600 dark:hover:bg-gray-800"
                  aria-label="Bad response"
                >
                  <ThumbsDown size={12} />
                </button>
              </span>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="order-2 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-200">
          <User size={16} />
        </div>
      )}
    </div>
  );
}

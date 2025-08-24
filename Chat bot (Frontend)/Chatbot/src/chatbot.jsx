import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { id: 1, sender: "bot", text: "👋 Hello! I can generate posts for you. Type something!" },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    document.getElementById("chat-input")?.focus();
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { id: messages.length + 1, sender: "user", text: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });

      const data = await response.json();
      const botMessage = {
        id: messages.length + 2,
        sender: "bot",
        text: data.response || "⚠️ Sorry, I couldn’t generate a response.",
        image: data.image_base64 ? `data:image/png;base64,${data.image_base64}` : undefined,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { id: messages.length + 2, sender: "bot", text: "⚠️ Error connecting to backend." },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const isGrouped = (index) => {
    if (index === 0) return false;
    return messages[index].sender === messages[index - 1].sender;
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Header */}
      <div className="p-6 bg-gradient-to-r from-purple-600 to-indigo-500 text-white text-3xl font-bold shadow-xl rounded-b-3xl">
        ImpactAI
      </div>

      {/* Messages */}
      <div className="flex-1 p-6 pb-32 space-y-2 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-900">
        {messages.map((msg, idx) => (
          <div
            key={msg.id}
            className={`flex transition-transform duration-300 ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            } animate-fade-in`}
          >
            {/* Avatar */}
            {!isGrouped(idx) && msg.sender === "bot" && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-400 to-purple-400 flex items-center justify-center mr-3 mt-1">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            {!isGrouped(idx) && msg.sender === "user" && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center ml-3 mt-1">
                <User className="w-5 h-5 text-white" />
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`relative flex items-start px-6 py-4 rounded-3xl shadow-lg backdrop-blur-sm border border-white/20 max-w-[80%] md:max-w-[60%]
              ${msg.sender === "user"
                ? "bg-gradient-to-tr from-purple-500 to-indigo-500 text-white rounded-br-none ml-1"
                : "bg-gray-800 text-gray-200 rounded-bl-none animate-gradient mr-1"
              } ${isGrouped(idx) ? "mt-1" : "mt-3"}`}
            >
              <div className="flex-grow text-sm md:text-base leading-relaxed break-words whitespace-pre-wrap">
                {msg.image ? (
                  <img
                    src={msg.image}
                    alt="Generated"
                    className="rounded-xl object-contain shadow-lg mt-2"
                    style={{ maxWidth: "100%", maxHeight: "400px" }}
                  />
                ) : (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                )}
                <div className="text-xs text-gray-400 mt-1 text-right">
                  {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>

              {/* Tail */}
              {!isGrouped(idx) && (
                <div
                  className={`absolute bottom-0 w-3 h-3 bg-inherit ${
                    msg.sender === "user" ? "right-0 rounded-bl-full" : "left-0 rounded-br-full"
                  }`}
                />
              )}
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-center space-x-2 text-gray-400 text-sm mt-2 animate-pulse">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-400 to-purple-400 flex items-center justify-center animate-scale">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="flex space-x-1">
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-0"></span>
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-150"></span>
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-300"></span>
            </div>
            <span>Bot is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="fixed bottom-5 left-1/2 transform -translate-x-1/2 w-[95%] md:w-[60%] flex items-center gap-3 p-4 bg-white/10 backdrop-blur-md rounded-full shadow-2xl border border-white/20">
        <input
          id="chat-input"
          type="text"
          placeholder="Type your message..."
          className="flex-1 px-6 py-3 rounded-full bg-white/10 text-white placeholder-gray-400 focus:outline-none transition"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <button
          className="p-3 bg-purple-600 hover:bg-purple-500 rounded-full shadow-lg transition-transform transform hover:scale-110"
          onClick={handleSendMessage}
        >
          <Send className="w-5 h-5 text-white" />
        </button>
      </div>

      {/* Tailwind Animations */}
      <style>
        {`
          @keyframes fade-in {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in { animation: fade-in 0.4s ease forwards; }

          @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
          }
          .animate-bounce { animation: bounce 1s infinite; }
          .delay-0 { animation-delay: 0s; }
          .delay-150 { animation-delay: 0.15s; }
          .delay-300 { animation-delay: 0.3s; }

          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          .animate-gradient {
            background-size: 200% 200%;
            animation: gradientShift 6s ease infinite;
          }

          @keyframes scale-up {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
          }
          .animate-scale { animation: scale-up 1s ease-in-out infinite; }
        `}
      </style>
    </div>
  );
}

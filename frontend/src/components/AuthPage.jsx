import React, { useState } from "react";
import Login from "./Login";
import Register from "./Register";

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login"); // 'login' or 'register'

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="bg-gray-900/70 p-6 rounded-xl shadow-xl border border-gray-700">
          <div className="flex justify-between mb-4">
            <h1 className="text-2xl font-bold text-white">Social Media</h1>
            <div className="space-x-2">
              <button
                onClick={() => setMode("login")}
                className={`px-3 py-1 rounded ${mode === "login" ? "bg-indigo-600" : "bg-gray-700"}`}
              >
                Login
              </button>
              <button
                onClick={() => setMode("register")}
                className={`px-3 py-1 rounded ${mode === "register" ? "bg-indigo-600" : "bg-gray-700"}`}
              >
                Register
              </button>
            </div>
          </div>

          {mode === "login" ? <Login onLogin={onLogin} /> : <Register onRegistered={() => setMode("login")} />}
        </div>
      </div>
    </div>
  );
}

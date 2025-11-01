import React from "react";
import PostForm from "./PostForm";
import PostList from "./PostList";

export default function Dashboard({ username, onLogout }) {
  return (
    <div className="min-h-screen py-8">
      <div className="max-w-3xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-white">Social Media</h1>
          <div className="flex items-center gap-4">
            <div className="text-gray-300">Signed in as <strong>{username}</strong></div>
            <button onClick={onLogout} className="bg-red-600 px-3 py-1 rounded">Logout</button>
          </div>
        </header>

        <PostForm refreshTriggerKey="post-created" />
        <div className="mt-6">
          <PostList />
        </div>
      </div>
    </div>
  );
}

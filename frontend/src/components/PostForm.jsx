import { useState } from "react";
import API from "../api";

export default function PostForm({ user, onPostCreated }) {
  const [content, setContent] = useState("");
  const [hashtags, setHashtags] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [location, setLocation] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const tagsArray = hashtags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0);

      await API.post("/posts", {
        author_id: user.user_id,
        author_username: user.username,
        content,
        hashtags: tagsArray,
        media_url: mediaUrl,
        location,
      });

      setContent("");
      setHashtags("");
      setMediaUrl("");
      setLocation("");
      onPostCreated();
    } catch (err) {
      alert("Error creating post");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="What's on your mind?"
        className="w-full p-2 border rounded"
        required
      />
      <input
        type="text"
        placeholder="Add hashtags (comma-separated)"
        value={hashtags}
        onChange={(e) => setHashtags(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="url"
        placeholder="Media URL (optional)"
        value={mediaUrl}
        onChange={(e) => setMediaUrl(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        placeholder="Location (optional)"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Post
      </button>
    </form>
  );
}

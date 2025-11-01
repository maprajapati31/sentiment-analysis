import { useState } from "react";
import API from "../api";

export default function PostCard({ post, user, onLike, onDelete, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [updatedContent, setUpdatedContent] = useState(post.content);
  const [updatedHashtags, setUpdatedHashtags] = useState(post.hashtags?.join(", ") || "");

  const handleDelete = async () => {
    if (user.user_id !== post.author_id) {
      alert("You can only delete your own posts!");
      return;
    }
    await API.delete(`/posts/${post._id}`);
    onDelete();
  };

  const handleUpdate = async () => {
    try {
      const tagsArray = updatedHashtags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0);

      await API.put(`/posts/${post._id}`, {
        content: updatedContent,
        hashtags: tagsArray,
      });
      setIsEditing(false);
      onUpdate();
    } catch (err) {
      alert("Error updating post");
    }
  };

  const handleLike = async () => {
    try {
      await API.post(`/posts/${post._id}/like`, { user_id: user.user_id });
      onLike();
    } catch (err) {
      console.error(err);
    }
  };

  const likedByUser = post.liked_by?.includes(user.user_id);

  return (
    <div className="bg-white shadow p-4 rounded-lg mb-4">
      <p className="text-sm text-gray-500">@{post.author_username}</p>

      {isEditing ? (
        <>
          <textarea
            value={updatedContent}
            onChange={(e) => setUpdatedContent(e.target.value)}
            className="w-full p-2 border rounded my-2"
          />
          <input
            type="text"
            value={updatedHashtags}
            onChange={(e) => setUpdatedHashtags(e.target.value)}
            placeholder="Hashtags (comma-separated)"
            className="w-full p-2 border rounded mb-2"
          />
          <button
            onClick={handleUpdate}
            className="bg-green-500 text-white px-3 py-1 rounded mr-2"
          >
            Save
          </button>
          <button
            onClick={() => setIsEditing(false)}
            className="bg-gray-400 text-white px-3 py-1 rounded"
          >
            Cancel
          </button>
        </>
      ) : (
        <p className="text-lg text-gray-800 my-2">{post.content}</p>
      )}

      {/* Hashtags */}
      {post.hashtags?.length > 0 && (
        <div className="flex flex-wrap gap-2 my-2">
          {post.hashtags.map((tag, i) => (
            <span
              key={i}
              className="bg-blue-100 text-blue-600 text-sm px-2 py-1 rounded"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Like button */}
      <div className="flex items-center gap-3 mt-2">
        <button
          onClick={handleLike}
          className={`px-3 py-1 rounded text-white ${
            likedByUser ? "bg-red-500" : "bg-gray-500 hover:bg-gray-600"
          }`}
        >
          {likedByUser ? "❤️ Liked" : "🤍 Like"}
        </button>
        <span className="text-sm text-gray-600">{post.like_count || 0} likes</span>
      </div>

      {/* Edit/Delete buttons */}
      {user.user_id === post.author_id && !isEditing && (
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => setIsEditing(true)}
            className="bg-yellow-500 text-white px-3 py-1 rounded"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="bg-red-500 text-white px-3 py-1 rounded"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}


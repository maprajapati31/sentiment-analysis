import React, { useEffect, useState } from "react";
import { getPosts, createPost, deletePost, updatePost } from "../api";

export default function PostList() {
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState({ content: "", author_username: "User1", author_id: "dummy_user" });
  const [editingId, setEditingId] = useState(null);
  const [editValues, setEditValues] = useState({ content: "", hashtags: "", media_url: "", category: "" });

  // Fetch posts from backend
  const fetchPosts = async () => {
    try {
      const res = await getPosts();
      setPosts(res.data || []);
    } catch (err) {
      console.error("Error fetching posts:", err);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  // Handle post creation
  const handleCreatePost = async () => {
    if (!newPost.content.trim()) return alert("Please enter post content");
    try {
      await createPost({
        author_id: newPost.author_id,
        author_username: newPost.author_username,
        content: newPost.content,
      });
      setNewPost({ ...newPost, content: "" });
      fetchPosts();
    } catch (err) {
      console.error("Error creating post:", err);
    }
  };

  // Handle delete post
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this post?")) return;
    try {
      await deletePost(id);
      fetchPosts();
    } catch (err) {
      console.error("Error deleting post:", err);
    }
  };

  // Start editing
  const startEdit = (post) => {
    setEditingId(post._id);
    setEditValues({
      content: post.content || "",
      hashtags: (post.hashtags || []).join(", "),
      media_url: post.media_url || "",
      category: post.category || "",
    });
  };

  // Cancel edit
  const cancelEdit = () => {
    setEditingId(null);
    setEditValues({ content: "", hashtags: "", media_url: "", category: "" });
  };

  // Save edited post
  const saveEdit = async (postId) => {
    try {
      const payload = {
        content: editValues.content,
        hashtags: editValues.hashtags
          ? editValues.hashtags.split(",").map((h) => h.trim()).filter(Boolean)
          : [],
      };
      if (editValues.media_url) payload.media_url = editValues.media_url;
      if (editValues.category) payload.category = editValues.category;

      await updatePost(postId, payload);
      setEditingId(null);
      fetchPosts();
    } catch (err) {
      console.error("Failed to update post", err);
      alert("Failed to update post.");
    }
  };

  // helper to update editValues
  const setField = (k, v) => setEditValues((prev) => ({ ...prev, [k]: v }));

  return (
    <div className="min-h-screen bg-[url('/bg.jpg')] bg-cover bg-center text-white p-6">
      <div className="max-w-2xl mx-auto bg-black/70 p-6 rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold mb-4 text-center">Post Manager</h1>

        {/* Create Post */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <textarea
            className="flex-1 bg-gray-800 rounded-lg p-2 text-white"
            placeholder="Write a new post..."
            value={newPost.content}
            onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
          />
          <button
            onClick={handleCreatePost}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg"
          >
            Post
          </button>
        </div>

        {/* Posts List */}
        {posts.length === 0 ? (
          <p className="text-center text-gray-300">No posts yet.</p>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post._id}
                className="bg-gray-900 p-4 rounded-lg shadow border border-gray-700"
              >
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h2 className="font-semibold text-lg">@{post.author_username}</h2>
                    <p className="text-xs text-gray-400">
                      {new Date(post.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="space-x-2">
                    {editingId === post._id ? (
                      <>
                        <button
                          onClick={() => saveEdit(post._id)}
                          className="text-green-400 hover:text-green-500"
                        >
                          Save
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="text-gray-400 hover:text-gray-500"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => startEdit(post)}
                          className="text-yellow-400 hover:text-yellow-500"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(post._id)}
                          className="text-red-400 hover:text-red-500"
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Post content */}
                {editingId === post._id ? (
                  <div className="space-y-3">
                    <textarea
                      className="w-full p-2 rounded bg-gray-800 text-white"
                      rows="3"
                      value={editValues.content}
                      onChange={(e) => setField("content", e.target.value)}
                    />
                    <input
                      className="w-full p-2 rounded bg-gray-800 text-white"
                      placeholder="hashtags (comma separated)"
                      value={editValues.hashtags}
                      onChange={(e) => setField("hashtags", e.target.value)}
                    />
                    <input
                      className="w-full p-2 rounded bg-gray-800 text-white"
                      placeholder="media url"
                      value={editValues.media_url}
                      onChange={(e) => setField("media_url", e.target.value)}
                    />
                    <input
                      className="w-full p-2 rounded bg-gray-800 text-white"
                      placeholder="category"
                      value={editValues.category}
                      onChange={(e) => setField("category", e.target.value)}
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-gray-200">{post.content}</p>
                    {post.media_url && (
                      <img
                        src={post.media_url}
                        alt="media"
                        className="mt-2 rounded-md"
                      />
                    )}
                    {post.hashtags && post.hashtags.length > 0 && (
                      <div className="mt-2 text-sm text-blue-300">
                        {post.hashtags.map((h, i) => (
                          <span key={i} className="mr-2">#{h}</span>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

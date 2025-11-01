import { useEffect, useState } from "react";
import API from "./api";
import PostForm from "./components/PostForm";
import PostCard from "./components/PostCard";
import Login from "./components/Login";
import Register from "./components/Register";

export default function App() {
  const [posts, setPosts] = useState([]);
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user")) || null);
  const [showRegister, setShowRegister] = useState(false);

  const fetchPosts = async () => {
    try {
      const res = await API.get("/posts");
      setPosts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (user) fetchPosts();
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
  };

  if (!user) {
    return showRegister ? (
      <Register onRegistered={() => setShowRegister(false)} />
    ) : (
      <Login onLogin={setUser} onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: "url('/background.jpg')" }}
    >
      <div className="backdrop-blur-sm bg-white/70 min-h-screen p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">📝 My Posts</h1>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
            >
              Logout
            </button>
          </div>

          <PostForm user={user} onPostCreated={fetchPosts} />

          <div>
            {posts.map((post) => (
              <PostCard
                key={post._id}
                post={post}
                user={user}
                onLike={fetchPosts}
                onDelete={fetchPosts}
                onUpdate={fetchPosts}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

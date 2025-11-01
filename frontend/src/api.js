import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000",
  headers: { "Content-Type": "application/json" },
});

export async function getPosts() {
  return API.get("/posts");
}
export async function createPost(payload) {
  return API.post("/posts", payload);
}
export async function deletePost(postId) {
  return API.delete(`/posts/${postId}`);
}
export async function toggleLike(postId, userId) {
  return API.post(`/posts/${postId}/like`, { user_id: userId });
}

/* NEW: update post */
export async function updatePost(postId, payload) {
  return API.put(`/posts/${postId}`, payload);
}

/* Comments (if present) */
export async function getComments(postId) {
  return API.get("/comments", { params: { post_id: postId } });
}
export async function createComment(payload) {
  return API.post("/comments", payload);
}
export async function updateComment(commentId, payload) {
  return API.put(`/comments/${commentId}`, payload);
}
export async function deleteComment(commentId) {
  return API.delete(`/comments/${commentId}`);
}

export default API;

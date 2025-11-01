import { useState } from "react";
import API from "../api";

export default function Register({ onRegistered }) {
  const [form, setForm] = useState({
    username: "",
    display_name: "",
    email: "",
    password: "",
    age: "",
    gender: "",
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await API.post("/signup", form);
      alert("User registered successfully!");
      onRegistered();
    } catch (err) {
      alert("Error: " + err.response?.data?.error || "Registration failed");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-200">
      <div className="bg-white shadow-lg p-8 rounded-lg w-96">
        <h2 className="text-2xl font-bold mb-4 text-center">Register</h2>
        <form onSubmit={handleRegister} className="space-y-3">
          {["username", "display_name", "email", "password", "age", "gender"].map((field) => (
            <input
              key={field}
              type={field === "password" ? "password" : "text"}
              name={field}
              placeholder={field.replace("_", " ").toUpperCase()}
              className="w-full p-2 border rounded"
              onChange={handleChange}
              required
            />
          ))}
          <button className="bg-green-500 w-full py-2 text-white rounded hover:bg-green-600">
            Register
          </button>
        </form>
        <p className="text-sm mt-4 text-center">
          Already have an account?{" "}
          <button className="text-blue-500" onClick={onRegistered}>
            Login
          </button>
        </p>
      </div>
    </div>
  );
}

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login, getGoogleAuthUrl } from "../../api/auth";
import { useAuth } from "../../services/authContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login: authLogin } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const { access_token } = await login(email, password);
      await authLogin(access_token);
      navigate("/dashboard");
    } catch {
      setError("Invalid email or password");
    }
  }

  async function handleGoogleLogin() {
    const url = await getGoogleAuthUrl();
    window.location.href = url;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-xl shadow p-8 space-y-6">
        <h1 className="text-2xl font-bold text-center">Sign in</h1>

        {error && <p className="text-red-500 text-sm text-center">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Sign in
          </button>
        </form>

        <div className="relative flex items-center">
          <div className="flex-grow border-t border-gray-200" />
          <span className="mx-4 text-gray-400 text-sm">or</span>
          <div className="flex-grow border-t border-gray-200" />
        </div>

        <button
          onClick={handleGoogleLogin}
          className="w-full border border-gray-300 py-2 rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
        >
          <img src="https://www.google.com/favicon.ico" alt="" className="w-4 h-4" />
          Continue with Google
        </button>

        <p className="text-center text-sm text-gray-500">
          No account?{" "}
          <Link to="/register" className="text-blue-600 hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}

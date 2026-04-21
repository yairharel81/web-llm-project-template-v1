import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../services/authContext";

// To handle real-time events in a page, use useSSEEvent() from sseContext —
// not useSSE() here. SSEProvider (in App.tsx) owns the single connection.

interface Props {
  children: React.ReactNode;
}

export default function DashboardShell({ children }: Props) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { to: "/dashboard", label: "Chat" },
    { to: "/tasks", label: "Tasks" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-semibold text-gray-800">My App</span>
          <nav className="flex items-center gap-4">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-sm font-medium transition ${
                  location.pathname === link.to
                    ? "text-blue-600"
                    : "text-gray-500 hover:text-gray-800"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          {user?.avatar_url && (
            <img src={user.avatar_url} alt="" className="w-8 h-8 rounded-full" />
          )}
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button
            onClick={logout}
            className="text-sm text-gray-500 hover:text-red-500 transition"
          >
            Sign out
          </button>
        </div>
      </header>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}

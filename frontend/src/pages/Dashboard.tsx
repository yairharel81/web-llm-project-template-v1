import DashboardShell from "../components/dashboard/DashboardShell";
import ChatComponent from "../components/chat/ChatComponent";
import { useAuth } from "../services/authContext";

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <DashboardShell>
      <div className="max-w-3xl mx-auto h-[calc(100vh-120px)] flex flex-col">
        <h2 className="text-xl font-semibold mb-4">
          Welcome{user?.full_name ? `, ${user.full_name}` : ""}
        </h2>
        <div className="flex-1 border rounded-xl overflow-hidden">
          <ChatComponent systemPrompt="You are a helpful assistant." />
        </div>
      </div>
    </DashboardShell>
  );
}

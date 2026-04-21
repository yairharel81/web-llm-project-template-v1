import { useEffect, useState } from "react";
import DashboardShell from "../components/dashboard/DashboardShell";
import { useSSEEvent } from "../services/sseContext";
import { fetchTasks, createTask, updateTaskStatus } from "../api/tasks";
import type { Task, TaskStatus } from "../types";

const STATUS_LABELS: Record<TaskStatus, string> = {
  todo: "To Do",
  in_progress: "In Progress",
  done: "Done",
};

const STATUS_COLORS: Record<TaskStatus, string> = {
  todo: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-100 text-blue-700",
  done: "bg-green-100 text-green-700",
};

const NEXT_STATUS: Record<TaskStatus, TaskStatus | null> = {
  todo: "in_progress",
  in_progress: "done",
  done: null,
};

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  // Toast notification for task_done SSE events
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTasks();
      setTasks(data);
    } catch {
      setError("Failed to load tasks.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      setCreating(true);
      const task = await createTask(title.trim(), description.trim() || undefined);
      setTasks((prev) => [task, ...prev]);
      setTitle("");
      setDescription("");
    } catch {
      setError("Failed to create task.");
    } finally {
      setCreating(false);
    }
  }

  async function handleAdvanceStatus(task: Task) {
    const next = NEXT_STATUS[task.status];
    if (!next) return;
    try {
      const updated = await updateTaskStatus(task.id, next);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      // SSE will fire when status becomes "done" — handled in DashboardShell
    } catch {
      setError("Failed to update task.");
    }
  }

  useSSEEvent("task_done", (event) => {
    const { title: taskTitle } = event.data as { task_id: number; title: string };
    setToast(`Task completed: "${taskTitle}"`);
    setTimeout(() => setToast(null), 4000);
    loadTasks();
  });

  return (
    <DashboardShell>
      <div className="max-w-2xl mx-auto">
        <h2 className="text-xl font-semibold mb-6">My Tasks</h2>

        {/* Toast notification */}
        {toast && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-green-50 border border-green-200 text-green-800 text-sm flex items-center justify-between">
            <span>{toast}</span>
            <button onClick={() => setToast(null)} className="ml-4 text-green-600 hover:text-green-800">
              ✕
            </button>
          </div>
        )}

        {/* Create task form */}
        <form
          onSubmit={handleCreate}
          className="mb-8 p-4 border rounded-xl bg-white shadow-sm space-y-3"
        >
          <h3 className="font-medium text-gray-700">New Task</h3>
          <input
            type="text"
            placeholder="Title *"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            rows={2}
          />
          <button
            type="submit"
            disabled={creating || !title.trim()}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {creating ? "Adding..." : "Add Task"}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="mb-4 px-4 py-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Task list */}
        {loading ? (
          <p className="text-gray-500 text-sm">Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-12">
            No tasks yet. Create one above!
          </p>
        ) : (
          <ul className="space-y-3">
            {tasks.map((task) => (
              <li
                key={task.id}
                className="p-4 border rounded-xl bg-white shadow-sm flex items-start gap-4"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-gray-800 truncate">{task.title}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[task.status]}`}
                    >
                      {STATUS_LABELS[task.status]}
                    </span>
                  </div>
                  {task.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">{task.description}</p>
                  )}
                </div>
                {NEXT_STATUS[task.status] && (
                  <button
                    onClick={() => handleAdvanceStatus(task)}
                    className="flex-shrink-0 text-xs px-3 py-1.5 border rounded-lg text-gray-600 hover:bg-gray-50 transition"
                  >
                    Mark {STATUS_LABELS[NEXT_STATUS[task.status]!]}
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </DashboardShell>
  );
}

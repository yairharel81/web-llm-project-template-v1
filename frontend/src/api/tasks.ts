import client from "./client";
import type { Task, TaskStatus } from "../types";

export async function fetchTasks(): Promise<Task[]> {
  const { data } = await client.get<Task[]>("/tasks");
  return data;
}

export async function createTask(title: string, description?: string): Promise<Task> {
  const { data } = await client.post<Task>("/tasks", { title, description });
  return data;
}

export async function updateTaskStatus(taskId: number, status: TaskStatus): Promise<Task> {
  const { data } = await client.patch<Task>(`/tasks/${taskId}/status`, { status });
  return data;
}

'use client';
import { useState, useEffect } from 'react';

interface Task {
  task_id: string;
  task: string;
  agent: string;
  status: string;
  output?: string;
  openai_priority?: string;
  grok_priority?: string;
  error?: string;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/tasks')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.error) {
          setError(data.error);
        } else {
          setTasks(data);
          setError(null);
        }
      })
      .catch(err => {
        console.error('Fetch error:', err);
        setError('Failed to load tasks');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4 bg-gradient-to-br from-gray-900 to-blue-900 text-gray-100 min-h-screen text-sm">
      <h1 className="text-3xl font-bold text-yellow-400 animate-glow">Hall of Creation Dashboard</h1>
      <h3 className="text-lg mt-2 text-emerald-400">Prometheus Task Oversight</h3>
      {loading ? (
        <p className="text-gray-300 mt-4">Loading tasks...</p>
      ) : error ? (
        <p className="text-red-500 mt-4">Error: {error}</p>
      ) : tasks.length === 0 ? (
        <p className="text-gray-300 mt-4">No tasks available</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {tasks.map(task => (
            <div key={task.task_id} className="border border-gray-600 p-4 rounded-lg shadow-lg bg-gray-800/80 backdrop-blur-sm">
              <h4 className="text-md font-semibold text-yellow-300">{task.task}</h4>
              <p>Agent: <span className="text-cyan-400">{task.agent}</span></p>
              <p>Status: <span className={task.status === 'In Progress' ? 'text-green-500' : task.status === 'Error' ? 'text-red-500' : 'text-blue-500'}>{task.status}</span></p>
              {task.output && <p className="truncate">Output: <span className="text-gray-300">{task.output}</span></p>}
              {task.openai_priority && <p className="truncate">OpenAI Priority: <span className="text-gray-300">{task.openai_priority}</span></p>}
              {task.grok_priority && <p className="truncate">Grok Priority: <span className="text-gray-300">{task.grok_priority}</span></p>}
              {task.error && <p className="text-red-500">Error: {task.error}</p>}
              <button className="mt-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-3 py-1 rounded hover:from-blue-600 hover:to-cyan-600 text-xs transition-all duration-300">
                Preview Asset
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
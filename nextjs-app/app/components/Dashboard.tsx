'use client';
import { useState, useEffect } from 'react';

interface Task {
  task_id: string;
  task: string;
  agent: string;
  status: string;
  output?: string;
  griptape_priority?: string;
  openai_priority?: string;
  grok_priority?: string;
  error?: string;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [, forceUpdate] = useState(0); // Correct usage for force re-render

  useEffect(() => {
    console.log('DEBUG: Component mounted, initiating fetch for /api/tasks');
    const fetchTasks = async () => {
      try {
        const res = await fetch('/api/tasks', {
          cache: 'no-store',
          headers: { 'Cache-Control': 'no-cache' }
        });
        console.log('DEBUG: Fetch response status:', res.status);
        if (!res.ok) {
          throw new Error(`HTTP error: ${res.status}`);
        }
        const data = await res.json();
        console.log('DEBUG: Fetch data received:', JSON.stringify(data, null, 2));
        if (data.error) {
          setError(data.error);
          setTasks([]);
        } else {
          setTasks(Array.isArray(data) ? [...data] : []);
          setError(null);
        }
        setLoading(false);
        forceUpdate(n => n + 1); // Force re-render
      } catch (err: any) {
        console.error('DEBUG: Fetch error:', err.message);
        setError(`Failed to load tasks: ${err.message}`);
        setTasks([]);
        setLoading(false);
        forceUpdate(n => n + 1); // Force re-render on error
      }
    };
    fetchTasks();
  }, []);

  if (loading || !tasks.length) {
    return <p className="text-gray-300 mt-4">Loading tasks...</p>;
  }

  if (error) {
    return <p className="text-red-500 mt-4">Error: {error}</p>;
  }

  return (
    <div className="p-4 bg-gradient-to-br from-gray-900 to-blue-900 text-gray-100 min-h-screen text-sm">
      <h1 className="text-3xl font-bold text-yellow-400 animate-glow">Hall of Creation Dashboard</h1>
      <h3 className="text-lg mt-2 text-emerald-400">Prometheus Task Oversight</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {tasks.map((task, index) => {
          try {
            console.log('DEBUG: Rendering task:', task.task_id || `task-${index}`);
            return (
              <div
                key={task.task_id || `task-${index}`}
                className="border border-gray-600 p-4 rounded-lg shadow-lg bg-gray-800/80 backdrop-blur-sm"
              >
                <h4 className="text-md font-semibold text-yellow-300">{task.task || 'Unknown Task'}</h4>
                <p>Agent: <span className="text-cyan-400">{task.agent || 'Unknown'}</span></p>
                <p>
                  Status:{' '}
                  <span
                    className={
                      task.status === 'In Progress'
                        ? 'text-green-500'
                        : task.status === 'Error'
                        ? 'text-red-500'
                        : 'text-blue-500'
                    }
                  >
                    {task.status || 'Unknown'}
                  </span>
                </p>
                {task.output && (
                  <p className="truncate">
                    Output: <span className="text-gray-300">{task.output}</span>
                  </p>
                )}
                {task.griptape_priority && (
                  <p className="truncate">
                    Griptape Priority: <span className="text-gray-300">{task.griptape_priority}</span>
                  </p>
                )}
                {task.openai_priority && (
                  <p className="truncate">
                    OpenAI Priority: <span className="text-gray-300">{task.openai_priority}</span>
                  </p>
                )}
                {task.grok_priority && (
                  <p className="truncate">
                    Grok Priority: <span className="text-gray-300">{task.grok_priority}</span>
                  </p>
                )}
                {task.error && (
                  <p className="text-red-500">Error: {task.error}</p>
                )}
                <button className="mt-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-3 py-1 rounded hover:from-blue-600 hover:to-cyan-600 text-xs transition-all duration-300">
                  Preview Asset
                </button>
              </div>
            );
          } catch (e) {
            console.error('DEBUG: Error rendering task:', task, e);
            return null;
          }
        })}
      </div>
    </div>
  );
}

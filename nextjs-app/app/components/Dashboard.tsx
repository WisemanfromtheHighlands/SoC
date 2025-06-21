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
  const [, forceUpdate] = useState(0); // For potential re-render

  useEffect(() => {
    console.log('DEBUG: Component mounted, initiating fetch for /api/tasks on port 3000');
    const fetchTasks = async () => {
      try {
        const res = await fetch('http://localhost:3000/api/tasks', {
          cache: 'no-store',
          headers: { 'Cache-Control': 'no-cache' },
        });
        console.log('DEBUG: Fetch response status: ' + res.status);
        if (!res.ok) {
          throw new Error('HTTP error: ' + res.status);
        }
        const data = await res.json();
        console.log('DEBUG: Fetch data received: ', data); // Log raw data
        if (data.error) {
          setError(data.error);
          setTasks([]);
        } else if (Array.isArray(data)) {
          setTasks(prevTasks => {
            const newTasks = [...data];
            if (JSON.stringify(prevTasks) !== JSON.stringify(newTasks)) {
              console.log('DEBUG: Tasks updated, forcing re-render');
              forceUpdate(prev => prev + 1); // Force re-render if data changes
            }
            return newTasks;
          });
          setError(null);
        } else {
          setError('Data is not an array');
          setTasks([]);
        }
        setLoading(false);
      } catch (err) {
        console.error('DEBUG: Fetch error: ', err);
        setError('Failed to load tasks: ' + (err as any).message);
        setTasks([]);
        setLoading(false);
      }
    };
    fetchTasks().catch((err) => {
      console.error('Uncaught fetch error: ', err);
      setError('Uncaught error during fetch');
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <p className="text-gray-300 mt-4 animate-pulse">Loading tasks...</p>;
  }

  if (error) {
    return <p className="text-red-500 mt-4">Error: {error}</p>;
  }

  return (
    <div className="p-4 bg-gradient-to-br from-gray-900 via-blue-900 to-teal-900 text-gray-100 min-h-screen text-sm">
      <h1 className="text-3xl font-bold text-yellow-400 animate-glow">Hall of Creation Dashboard</h1>
      <h3 className="text-lg mt-2 text-emerald-400">Prometheus Task Oversight</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {tasks.length > 0 ? (
          tasks.map((task, index) => {
            try {
              console.log('DEBUG: Rendering task: ', task.task_id || `task-${index}`);
              return (
                <div
                  key={task.task_id || `task-${index}`}
                  className="border border-gray-600 p-4 rounded-lg shadow-lg bg-gray-800/80 backdrop-blur-sm hover:bg-gray-700/80 transition-all duration-300"
                >
                  <h4 className="text-md font-semibold text-yellow-300 animate-pulse">{task.task || 'Unknown Task'}</h4>
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
              console.error('DEBUG: Error rendering task: ', (task ? JSON.stringify(task) : 'null'), e);
              return null;
            }
          })
        ) : (
          <p className="text-gray-400">No tasks available.</p>
        )}
      </div>
    </div>
  );
}

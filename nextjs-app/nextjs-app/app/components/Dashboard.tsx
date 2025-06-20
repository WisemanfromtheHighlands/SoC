'use client';
import { useState, useEffect } from 'react';

interface Task {
task_id: string;
task: string;
agent: string;
status: string;
output?: string;
grok_priority?: string;
error?: string;
}

export default function Dashboard() {
const [tasks, setTasks] = useState<Task[]>([]);

useEffect(() => {
fetch('/api/tasks')
.then(res => res.json())
.then(data => {
if (!data.error) setTasks(data);
});
}, []);

return (

Hall of Creation Dashboard
Prometheus Task Oversight
{tasks.map(task => (
{task.task}
Agent: {task.agent}

Status: {task.status}

{task.output &&
Output: {task.output}

} {task.grok_priority &&
Grok Priority: {task.grok_priority}

} {task.error &&
Error: {task.error}

} <button class="mt-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-3 py-1 rounded hover:from-blue-600 hover:to-cyan-600 text-xs transition-all duration-300"> Preview Asset </button>
))}
); } EOF nextjs-app/app/api/tasks/route.tsbash mkdir -p nextjs-app/app/api/tasks cat << EOF > nextjs-app/app/api/tasks/route.ts import { NextResponse } from 'next/server'; import fs from 'fs/promises'; import path from 'path';
export async function GET() {
const tasksFile = path.join(process.cwd(), '../../data/prometheus/tasks.json');
try {
const data = await fs.readFile(tasksFile, 'utf-8');
const tasks = data.trim().split('\n').filter(line => line).map(line => JSON.parse(line));
return NextResponse.json(tasks);
} catch (error) {
return NextResponse.json({ error: 'Failed to read tasks' }, { status: 500 });
}
}

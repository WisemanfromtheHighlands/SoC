import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

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
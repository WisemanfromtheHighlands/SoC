import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  try {
    const tasksFile = path.join(process.cwd(), '../data/prometheus/tasks.json');
    console.log(`DEBUG: Attempting to read tasks file at ${tasksFile}`);
    const data = await fs.readFile(tasksFile, 'utf-8');
    if (!data.trim()) {
      console.log('DEBUG: tasks.json is empty');
      return NextResponse.json([]);
    }
    const tasks = data.trim().split('\n').filter(line => line).map(line => {
      try {
        return JSON.parse(line);
      } catch (e) {
        console.error(`DEBUG: Failed to parse task line: ${line}`, e);
        return null;
      }
    }).filter(task => task !== null);
    console.log(`DEBUG: Loaded ${tasks.length} tasks`);
    return NextResponse.json(tasks);
  } catch (error) {
    console.error(`DEBUG: Error reading tasks.json: ${error}`);
    return NextResponse.json({ error: 'Failed to read tasks' }, { status: 500 });
  }
}
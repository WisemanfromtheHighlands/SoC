import json
import os
import time
from griptape.structures import Agent
from griptape.tools import WebScraper, TaskMemory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROK_SUBSCRIPTION_API_KEY = os.getenv("GROK_SUBSCRIPTION_API_KEY")

# Initialize Griptape Agent
agent = Agent(
    tools=[WebScraper(), TaskMemory()],
    off_prompt_driver=None,  # Use default or configure with xAI/Grok if needed
    stream=False
)

def generate_task(agent_name, task_description):
    timestamp = time.time()
    task_id = f"{agent_name}_{int(timestamp * 1000)}_{hash(task_description) & 0xffffff}"
    task = {
        "task_id": task_id,
        "task": task_description,
        "agent": agent_name,
        "status": "In Progress",
        "timestamp": timestamp,
        "output": f"assets/3d/{agent_name.lower()}_new_lod0.fbx",
        "griptape_priority": "1. **Research and Planning** (High Priority): Gather references.\n2. **Modeling** (High Priority): Create low-poly model."
    }
    return task

def load_tasks(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks, file_path):
    with open(file_path, 'w') as f:
        json.dump(tasks, f, indent=2)

def main():
    tasks_file = "data/prometheus/tasks.json"
    tasks = load_tasks(tasks_file)

    # Generate new tasks
    new_tasks = [
        generate_task("Athena", "Generate low-poly shield with URP materials"),
        generate_task("Kurosawa", "Generate cinematic battle sequence with URP"),
    ]
    tasks.extend(new_tasks)

    # Save updated tasks
    save_tasks(tasks, tasks_file)
    print(f"Generated {len(new_tasks)} new tasks. Total tasks: {len(tasks)}")

if __name__ == "__main__":
    main()
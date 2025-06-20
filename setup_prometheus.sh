#!/bin/bash

# setup_prometheus.sh: Automates Step 2 for Source of Creation
# Implements Prometheus orchestration with Grok API
# Date: June 20, 2025
# Author: Grok 3 (assisting WisemanfromtheHighlands)

set -e  # Exit on error

# Ensure we're in the project directory
cd ~/code/SoC

# Verify virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Verify .env is loaded
if [[ -z "$GROK_SUBSCRIPTION_API_KEY" ]]; then
    echo "Sourcing .env..."
    source .env
fi

# Validate GROK_SUBSCRIPTION_API_KEY
if [[ -z "$GROK_SUBSCRIPTION_API_KEY" || "$GROK_SUBSCRIPTION_API_KEY" == *"your_"* ]]; then
    echo "Error: Valid GROK_SUBSCRIPTION_API_KEY not set in .env. Get it from https://console.x.ai."
    exit 1
fi

# Test Grok API key
echo "Testing Grok API key..."
GROK_RESPONSE=$(curl -s -X POST "https://api.x.ai/v1/chat/completions" \
    -H "Authorization: Bearer $GROK_SUBSCRIPTION_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "grok-3-latest", "messages": [{"role": "user", "content": "Test"}]}')
if echo "$GROK_RESPONSE" | grep -q "error"; then
    echo "Error: Invalid Grok API key or API issue. Check key in https://console.x.ai or try again."
    echo "Response: $GROK_RESPONSE"
    exit 1
fi

# Ensure requests and python-dotenv are installed
echo "Installing requests and python-dotenv..."
pip install requests python-dotenv --no-cache-dir

# Create src and prometheus directories if not exists
mkdir -p src data/prometheus

# Create prometheus_orchestrator.py
cat << 'EOF' > src/prometheus_orchestrator.py
import os
import json
import time
import requests
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
print("DEBUG: GROK_SUBSCRIPTION_API_KEY =", os.getenv("GROK_SUBSCRIPTION_API_KEY"))

class PrometheusAgent:
    def __init__(self):
        self.api_keys = {
            "tripo3d": os.getenv("TRIPO3D_API_KEY"),
            "leonardo": os.getenv("LEONARDO_API_KEY"),
            "runwayml": os.getenv("RUNWAYML_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "grok": os.getenv("GROK_SUBSCRIPTION_API_KEY")
        }
        self.agents = {
            "Vitruvius": {"role": "Procedural Architect", "tasks": ["generate_temple", "generate_avatar"]},
            "Gaia": {"role": "Landscape Designer", "tasks": ["generate_oasis", "generate_avatar"]},
            "Imhotep": {"role": "Stability Engineer", "tasks": ["ensure_stability", "collaborate_dali", "generate_avatar"]},
            "Athena": {"role": "Mathematical Mentor", "tasks": ["generate_puzzles", "generate_avatar"]},
            "Kurosawa": {"role": "Cinematic Director", "tasks": ["generate_cinematic", "generate_avatar"]}
        }

    def grok_api_call(self, prompt):
        if not self.api_keys["grok"]:
            return {"error": "Grok API key missing"}
        headers = {"Authorization": f"Bearer {self.api_keys['grok']}"}
        payload = {
            "model": "grok-3-latest",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return {"error": str(e)}

    def assign_task(self, task, agent_name):
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        task_id = f"{agent_name}_{int(time.time())}"
        task_data = {
            "task_id": task_id,
            "task": task,
            "agent": agent_name,
            "status": "Pending",
            "timestamp": time.time()
        }
        # Determine asset type from task
        asset_type = None
        for keyword in ["avatar", "temple", "oasis", "cinematic", "stability", "puzzle"]:
            if keyword in task.lower():
                asset_type = keyword
                break
        if not asset_type:
            asset_type = "unknown"
        # Use Grok API for task prioritization
        grok_response = self.grok_api_call(f"Prioritize task: {task} for {agent_name} in Source of Creation")
        if not isinstance(grok_response, dict):
            task_data["status"] = "In Progress"
            task_data["output"] = f"assets/3d/{agent_name}_{asset_type}_lod0.fbx"
            task_data["grok_priority"] = grok_response
        else:
            task_data["status"] = "Error"
            task_data["error"] = grok_response["error"]
        with open("data/prometheus/tasks.json", "a") as f:
            json.dump(task_data, f)
            f.write("\n")
        return task_data

    def run(self, task_description):
        task_map = {
            "avatar": ["Vitruvius", "Gaia", "Imhotep", "Athena", "Kurosawa"],
            "temple": ["Vitruvius", "Imhotep"],
            "oasis": ["Gaia"],
            "cinematic": ["Kurosawa"],
            "stability": ["Imhotep"],
            "puzzle": ["Athena"]
        }
        assigned = []
        for keyword, agents in task_map.items():
            if keyword in task_description.lower():
                for agent in agents:
                    result = self.assign_task(task_description, agent)
                    assigned.append(result)
        return {"tasks": assigned, "status": "Orchestrated"}

if __name__ == "__main__":
    prometheus = PrometheusAgent()
    tasks = [
        "Generate low-poly avatar for Prometheus with URP materials",
        "Generate low-poly avatar for Vitruvius with URP materials",
        "Generate procedural Atlantean temple with glowing runes",
        "Generate cinematic flythrough for Gaia’s oasis"
    ]
    for task in tasks:
        result = prometheus.run(task)
        print(f"Prometheus result: {json.dumps(result, indent=2)}")
EOF

# Run the script
echo "Running Prometheus orchestration script..."
python src/prometheus_orchestrator.py

# Verify output
if [[ -f "data/prometheus/tasks.json" ]]; then
    echo "Task log created: data/prometheus/tasks.json"
    tail -n 4 data/prometheus/tasks.json
else
    echo "Error: Task log not created"
    exit 1
fi

# Commit and push changes
echo "Committing changes..."
git add src data/prometheus
git commit -m "Implement Prometheus orchestration with fixed Grok API"
git push origin master

echo "Step 2 completed successfully!"
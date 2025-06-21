import os
import json
import time
import requests
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
print("DEBUG: GROK_SUBSCRIPTION_API_KEY =", os.getenv("GROK_SUBSCRIPTION_API_KEY"))
print("DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

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
            print("DEBUG: Grok API key missing")
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
            print(f"DEBUG: Grok API error: {str(e)}")
            return {"error": str(e)}

    def openai_api_call(self, prompt, retries=3, initial_delay=5, backoff_factor=2):
        if not self.api_keys["openai"]:
            print("DEBUG: OpenAI API key missing")
            return {"error": "OpenAI API key missing"}
        headers = {
            "Authorization": f"Bearer {self.api_keys['openai']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150
        }
        for attempt in range(retries):
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.HTTPError as e:
                error_response = response.json().get("error", {})
                if error_response.get("code") == "insufficient_quota":
                    print("DEBUG: OpenAI API quota exceeded. Check plan at https://platform.openai.com/account/billing")
                    return {"error": "OpenAI quota exceeded"}
                if response.status_code == 429:
                    wait_time = initial_delay * (backoff_factor ** attempt)
                    print(f"DEBUG: OpenAI API rate limit hit (429). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                print(f"DEBUG: OpenAI API HTTP error: {str(e)}")
                return {"error": str(e)}
            except Exception as e:
                print(f"DEBUG: OpenAI API general error: {str(e)}")
                return {"error": str(e)}
        print("DEBUG: OpenAI API max retries exceeded")
        return {"error": "Max retries exceeded for OpenAI API"}

    def assign_task(self, task, agent_name):
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        task_id = f"{agent_name}_{int(time.time() * 1000)}_{hash(task):.8x}"  # Use milliseconds and task hash
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
        # Use OpenAI for task prioritization, fall back to Grok if OpenAI fails
        prompt = f"Prioritize task: {task} for {agent_name} in Source of Creation. Provide a detailed breakdown of subtasks and their priority."
        openai_response = self.openai_api_call(prompt)
        if not isinstance(openai_response, dict):
            task_data["status"] = "In Progress"
            task_data["output"] = f"assets/3d/{agent_name}_{asset_type}_lod0.fbx"
            task_data["openai_priority"] = openai_response
        else:
            print(f"DEBUG: OpenAI failed, falling back to Grok: {openai_response['error']}")
            grok_response = self.grok_api_call(f"Prioritize task: {task} for {agent_name} in Source of Creation")
            if not isinstance(grok_response, dict):
                task_data["status"] = "In Progress"
                task_data["output"] = f"assets/3d/{agent_name}_{asset_type}_lod0.fbx"
                task_data["grok_priority"] = grok_response
            else:
                task_data["status"] = "Error"
                task_data["error"] = openai_response.get("error", grok_response.get("error", "Both OpenAI and Grok API calls failed"))
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
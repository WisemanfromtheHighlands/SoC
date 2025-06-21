import json
import os
import time  # Added import
from prometheus_orchestrator import PrometheusAgent
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
print("DEBUG: GROK_SUBSCRIPTION_API_KEY =", os.getenv("GROK_SUBSCRIPTION_API_KEY"))

def generate_3d_asset(prompt, agent_name, asset_type="avatar", lod_level=0):
    task_id = f"{agent_name}_{int(time.time())}_lod{lod_level}"
    # Mock Tripo3D API
    return {
        "asset": f"assets/3d/{agent_name}_{asset_type}_lod{lod_level}.fbx",
        "task_id": task_id
    }

if __name__ == "__main__":
    prometheus = PrometheusAgent()
    assets = [
        ("Low-poly Prometheus, 30s Grecian, marble robe, emerald caduceus torch, Egyptian ankh", "Prometheus", "avatar"),
        ("Low-poly Vitruvius, 30s Roman, gold geometric tunic, holographic blueprint orb, Egyptian ankh", "Vitruvius", "avatar"),
        ("Low-poly Gaia, 20s goddess, aquamarine gown, glowing seed, Egyptian lotus crown", "Gaia", "avatar"),
        ("Low-poly Imhotep, 30s Egyptian, pyramid tunic, glowing ankh-shaped compass, Egyptian lotus", "Imhotep", "avatar"),
        ("Low-poly Athena, 20s goddess, silver chiton, glowing owl, ankh shield, Egyptian lotus", "Athena", "avatar"),
        ("Low-poly Kurosawa, 40s Japanese, black coat, glowing clapperboard, Egyptian ankh", "Kurosawa", "avatar"),
        ("Low-poly Atlantean temple module, golden pyramids, glowing runes, ankh arches", "Vitruvius_Temple", "temple"),
        ("Low-poly Egyptian oasis module, dunes, Atlantean canals, lotus flora, crystal obelisks", "Gaia_Oasis", "oasis")
    ]
    for prompt, name, asset_type in assets:
        task = f"Generate {asset_type} for {name} with URP materials"
        result = prometheus.run(task)
        for task_data in result["tasks"]:
            if task_data.get("status") == "In Progress":
                asset = generate_3d_asset(prompt, name, asset_type, lod_level=0)
                task_data["status"] = "Completed"
                task_data["output"] = asset["asset"]
                with open("data/prometheus/tasks.json", "a") as f:
                    json.dump(task_data, f)
                    f.write("\n")
                print(f"Generated {asset_type} for {name}: {asset['asset']}")
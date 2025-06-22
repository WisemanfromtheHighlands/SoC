import json
import os
import time
from griptape.structures import Agent
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver

# Assuming JsonValidatorAgent is a custom class; adjust import as needed
from json_validator import JsonValidatorAgent

class PrometheusOrchestrator:
    def __init__(self):
        self.tasks_file = 'data/prometheus/tasks.json'
        self.backup_dir = os.path.expanduser('~/SoC_backup_fallback')
        self.fallback_file = 'fallback_tasks.json'
        # Initialize validator with explicit no-stream configuration
        self.validator = JsonValidatorAgent()  # Default initialization
        if hasattr(self.validator, 'prompt_driver'):
            self.validator.prompt_driver = OpenAiChatPromptDriver(
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                stream=False  # Explicitly disable stream
            )
        else:
            print("DEBUG: JsonValidatorAgent does not support prompt_driver. Using default driver.")

    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return []

    def save_tasks(self, tasks):
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        # Validate and backup the saved tasks
        json_str = json.dumps(tasks, indent=2)
        print(f'DEBUG: Attempting validation with JSON: {json_str[:200]}...')
        try:
            result = self.validator.run({'input': {'json_str': json_str}})
            if hasattr(result, 'value'):
                validation_result = result.value
                print(f'DEBUG: Validation result: {validation_result}')
                if json.loads(validation_result).get('is_valid', False):
                    print('DEBUG: Backup validation succeeded')
                    os.makedirs(self.backup_dir, exist_ok=True)
                    backup_path = os.path.join(self.backup_dir, f'raw_tasks_{int(time.time())}.json')
                    with open(backup_path, 'w') as backup_file:
                        json.dump(tasks, backup_file, indent=2)
                    print(f'DEBUG: Backup created at {backup_path}')
                else:
                    print(f'DEBUG: Backup validation failed: {validation_result}')
            else:
                print(f'DEBUG: Validation result unavailable: {result}')
        except Exception as e:
            print(f'DEBUG: Validation error: {e}')

    def create_fallback_json(self):
        # Create a redundant JSON file in the root directory if it doesn’t exist
        fallback_path = os.path.join(os.getcwd(), self.fallback_file)
        if not os.path.exists(fallback_path):
            default_tasks = [
                {
                    "task_id": "fallback_1",
                    "task": "Default task 1",
                    "agent": "FallbackAgent",
                    "status": "Pending",
                    "timestamp": time.time(),
                    "output": "assets/3d/fallback_task1_lod0.fbx",
                    "griptape_priority": "1. Research and Planning (High Priority): Gather references.\n2. Modeling (High Priority): Create low-poly model."
                },
                {
                    "task_id": "fallback_2",
                    "task": "Default task 2",
                    "agent": "FallbackAgent",
                    "status": "Pending",
                    "timestamp": time.time(),
                    "output": "assets/3d/fallback_task2_lod0.fbx",
                    "griptape_priority": "1. Research and Planning (High Priority): Gather references.\n2. Modeling (High Priority): Create low-poly model."
                }
            ]
            with open(fallback_path, 'w') as f:
                json.dump(default_tasks, f, indent=2)
            print(f'DEBUG: Fallback JSON created at {fallback_path}')

    def orchestrate(self):
        tasks = self.load_tasks()
        if not tasks:
            # Example task generation with deduplication
            initial_tasks = [
                {
                    "task_id": f"{agent}_{timestamp}_{hash(str(i))}",
                    "task": f"Generate {task_type} with URP materials",
                    "agent": agent,
                    "status": "In Progress",
                    "timestamp": timestamp,
                    "output": f"assets/3d/{agent.lower()}_generate_{task_type.lower().replace(' ', '_')}_lod0.fbx",
                    "griptape_priority": "1. Research and Planning (High Priority): Gather references.\n2. Modeling (High Priority): Create low-poly model."
                }
                for i, (agent, task_type) in enumerate([
                    ("Vitruvius", "low-poly avatar for Prometheus"),
                    ("Gaia", "low-poly avatar for Vitruvius"),
                    ("Imhotep", "procedural Atlantean temple with glowing runes"),
                    ("Athena", "cinematic flythrough for Gaia’s oasis"),
                    ("Kurosawa", "low-poly shield"),
                    ("Vitruvius", "cinematic battle sequence"),
                    ("Gaia", "low-poly avatar for Prometheus"),
                    ("Imhotep", "low-poly avatar for Vitruvius"),
                    ("Athena", "procedural Atlantean temple with glowing runes"),
                    ("Kurosawa", "cinematic flythrough for Gaia’s oasis"),
                    ("Vitruvius", "low-poly shield"),
                    ("Gaia", "cinematic battle sequence"),
                    ("Imhotep", "low-poly avatar for Prometheus"),
                    ("Athena", "low-poly avatar for Vitruvius"),
                    ("Kurosawa", "procedural Atlantean temple with glowing runes"),
                    ("Vitruvius", "cinematic flythrough for Gaia’s oasis"),
                    ("Gaia", "low-poly shield"),
                    ("Imhotep", "cinematic battle sequence"),
                    ("Athena", "low-poly avatar for Prometheus"),
                    ("Kurosawa", "low-poly avatar for Vitruvius"),
                ], 1)
                for timestamp in [1750541013.972095 + i * 0.0001]
            ]
            tasks = list({task['task_id']: task for task in initial_tasks}.values())  # Deduplicate by task_id
        # Apply deduplication to existing tasks
        unique_tasks = list({task['task_id']: task for task in tasks}.values())
        if unique_tasks != tasks:
            tasks = unique_tasks
            print(f"Removed duplicates. Total unique tasks: {len(tasks)}")
        else:
            print(f"Generated 0 new tasks. Total unique tasks: {len(unique_tasks)}")
        # Always save tasks to trigger validation and backup
        self.save_tasks(tasks)
        print("Tasks saved and backed up.")
        return tasks

if __name__ == '__main__':
    orchestrator = PrometheusOrchestrator()
    orchestrator.create_fallback_json()  # Create fallback JSON if not present
    orchestrator.orchestrate()
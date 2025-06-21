import json
import os
import time
import uuid
from griptape.structures import Agent
from dotenv import load_dotenv
from json_validator import JsonValidatorAgent

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROK_SUBSCRIPTION_API_KEY = os.getenv('GROK_SUBSCRIPTION_API_KEY')

if not OPENAI_API_KEY or not GROK_SUBSCRIPTION_API_KEY:
    raise ValueError('Missing required API keys in .env file')

try:
    agent = Agent()
except Exception as e:
    print('Error initializing Griptape Agent: ' + str(e))
    exit(1)

def generate_task(agent_name, task_description):
    timestamp = time.time()
    task_id = agent_name + '_' + str(int(timestamp * 1000)) + '_' + uuid.uuid4().hex[:6]
    task = {
        'task_id': task_id,
        'task': task_description,
        'agent': agent_name,
        'status': 'In Progress',
        'timestamp': timestamp,
        'output': 'assets/3d/' + agent_name.lower() + '_' + '_'.join(task_description.lower().split()[:2]) + '_lod0.fbx',
        'griptape_priority': '1. Research and Planning (High Priority): Gather references.\n2. Modeling (High Priority): Create low-poly model.'
    }
    return task

def load_tasks(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    except json.JSONDecodeError as e:
        print('Error parsing JSON file: ' + str(e) + '. Using empty task list.')
        return []
    except IOError as e:
        print('Error reading file: ' + str(e) + '. Using empty task list.')
        return []

def save_tasks(tasks, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        json_str = json.dumps(tasks, indent=2, ensure_ascii=False)
        validator = JsonValidatorAgent()
        result = validator.run({'input': {'json_str': json_str}})
        output_text = result.to_text()
        validation_result = json.loads(output_text)
        if validation_result['is_valid']:
            with open(file_path, 'w') as f:
                f.write(validation_result['corrected_json'])
                f.flush()
                os.fsync(f.fileno())
            print('Saved ' + str(len(tasks)) + ' tasks to ' + file_path)
        else:
            print('Failed to validate JSON: ' + validation_result['error'])
    except (IOError, json.JSONDecodeError) as e:
        print('Error processing file or JSON: ' + str(e))

def main():
    tasks_file = 'data/prometheus/tasks.json'
    tasks = load_tasks(tasks_file)

    TARGET_TASKS = 20
    new_tasks = []
    if len(tasks) < TARGET_TASKS:
        agents = ['Vitruvius', 'Gaia', 'Imhotep', 'Athena', 'Kurosawa']
        task_types = [
            'Generate low-poly avatar for Prometheus with URP materials',
            'Generate low-poly avatar for Vitruvius with URP materials',
            'Generate procedural Atlantean temple with glowing runes',
            'Generate cinematic flythrough for Gaia’s oasis',
            'Generate low-poly shield with URP materials',
            'Generate cinematic battle sequence with URP'
        ]
        new_tasks = []
        for _ in range(TARGET_TASKS - len(tasks)):
            agent = agents[_ % len(agents)]
            task_type = task_types[_ % len(task_types)]
            new_tasks.append(generate_task(agent, task_type))
        tasks.extend(new_tasks)

    seen = set()
    tasks = [task for task in tasks if not (task['task_id'] in seen or seen.add(task['task_id']))]

    while len(tasks) < TARGET_TASKS:
        tasks.append(generate_task('Extra', 'Extra task ' + str(len(tasks) + 1) + ' with URP materials'))

    save_tasks(tasks, tasks_file)
    print('Generated ' + str(len(new_tasks)) + ' new tasks. Total unique tasks: ' + str(len(tasks)))

if __name__ == '__main__':
    main()

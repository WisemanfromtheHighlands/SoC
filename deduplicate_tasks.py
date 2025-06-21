import json

input_file = "data/prometheus/tasks.json"
output_file = "data/prometheus/tasks_dedup.json"

seen_ids = set()
unique_tasks = []

with open(input_file, "r") as f:
    for line in f:
        if not line.strip():
            continue
        task = json.loads(line)
        if task["task_id"] not in seen_ids:
            seen_ids.add(task["task_id"])
            unique_tasks.append(task)

with open(output_file, "w") as f:
    for task in unique_tasks:
        json.dump(task, f)
        f.write("\n")

print(f"Deduplicated {len(seen_ids)} tasks to {output_file}")

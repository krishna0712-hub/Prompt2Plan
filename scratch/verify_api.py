import urllib.request
import json

print("=== 1. TESTING GET /api/model-metrics ===")
req = urllib.request.Request('http://localhost:8000/api/model-metrics')
with urllib.request.urlopen(req) as resp:
    metrics_res = json.loads(resp.read().decode())
print(json.dumps(metrics_res, indent=2))

print("\n=== 2. TESTING POST /api/generate-plan ===")
idea = "Build a real-time collaborative document editor with AI assistant and role-based access control"
plan_data = json.dumps({'idea': idea}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/generate-plan', data=plan_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    plan_res = json.loads(resp.read().decode())

print("Success:", plan_res.get('success'))
project_data = plan_res.get('data', {})
project_id = project_data.get('id')
print("Project ID:", project_id)

tasks = project_data.get('tasks', [])
print(f"Tasks generated: {len(tasks)}")
if tasks:
    print("Sample task:", json.dumps(tasks[0], indent=2))

milestones = project_data.get('milestones', [])
print(f"Milestones generated: {len(milestones)}")
for m in milestones:
    p_name = m.get('phase_name')
    s_day = m.get('start_day')
    e_day = m.get('end_day')
    tot_d = m.get('total_days')
    opt_d = m.get('optimistic_days')
    pess_d = m.get('pessimistic_days')
    tot_h = m.get('total_hours')
    opt_h = m.get('optimistic_hours')
    pess_h = m.get('pessimistic_hours')
    print(f"Phase: {p_name:18} | Days: Day {s_day} -> {e_day} (Likely: {tot_d}d, Range: {opt_d}d–{pess_d}d) | Hours: {tot_h}h (Range: {opt_h}h–{pess_h}h)")

print("\n=== 3. TESTING PATCH /api/tasks/{task_id}/actual-hours ===")
task_id = tasks[0].get('id', 1) if tasks and 'id' in tasks[0] else 1
patch_data = json.dumps({'actual_hours': 14.5}).encode('utf-8')
req = urllib.request.Request(f'http://localhost:8000/api/projects/{project_id}', headers={'Content-Type': 'application/json'})
# First get task id from project
with urllib.request.urlopen(req) as resp:
    proj_detail = json.loads(resp.read().decode())
    db_tasks = proj_detail.get('data', {}).get('tasks', [])
    if db_tasks and 'id' in db_tasks[0]:
        task_id = db_tasks[0]['id']

req = urllib.request.Request(f'http://localhost:8000/api/tasks/{task_id}/actual-hours', data=patch_data, headers={'Content-Type': 'application/json'}, method='PATCH')
with urllib.request.urlopen(req) as resp:
    patch_res = json.loads(resp.read().decode())
print(json.dumps(patch_res, indent=2))

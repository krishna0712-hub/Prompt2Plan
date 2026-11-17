"""
measure_optimized.py — Measure memory consumption of optimized Prompt2Plan.
Mirrors scratch/measure_baseline.py to provide exact, comparable measurements.
"""
import os
import sys
import time
import gc
import psutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HOME"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "huggingface")

proc = psutil.Process(os.getpid())

def get_mem():
    gc.collect()
    return proc.memory_info().rss / (1024 * 1024)

print(f"[1] Application Startup (clean process): {get_mem():.2f} MB")

# Import FastAPI and backend modules
import backend.database as db
import backend.knowledge_graph as kg
import backend.nlp_extraction as nlp
import backend.rag_retrieval as rag
import backend.ai_effort_estimator as effort
import backend.architecture_gen as arch
import backend.task_breakdown as tasks
import backend.milestone_scheduler as ms
import backend.cost_estimation as cost
from backend.embedding_manager import get_embedding_manager

print(f"[2] After importing all backend modules: {get_mem():.2f} MB")

# Sequential initialization of DB + KG + RAG + Estimator
db.init_db()
kg.initialize_kg()
print(f"[3] After DB + KG init: {get_mem():.2f} MB")

mem_before_init = get_mem()
rag.initialize_rag()
effort.initialize_estimator()
mem_after_init = get_mem()
print(f"[4] After Sequential Module Initialization (precomputed RAG + Estimator): {mem_after_init:.2f} MB (added: {mem_after_init - mem_before_init:.2f} MB)")

# Semantic search / RAG retrieval
mem_before_search = get_mem()
for _ in range(5):
    res = rag.retrieve_similar(["chat", "real-time", "payments", "authentication"], top_k=3)
mem_after_search = get_mem()
print(f"[5] During semantic search / RAG retrieval (first loads shared model if needed): {mem_after_search:.2f} MB (delta: {mem_after_search - mem_before_search:.2f} MB)")

# Effort Estimation (5 tasks)
sample_tasks = [
    {"name": "Setup database schema and migrations", "component": "Database", "type": "setup"},
    {"name": "Build responsive React navigation UI", "component": "Frontend", "type": "ui"},
    {"name": "Implement Stripe payment webhook handler", "component": "Integration", "type": "integration"},
    {"name": "Create user JWT authentication endpoint", "component": "Backend", "type": "backend"},
    {"name": "Write end-to-end integration tests", "component": "Testing", "type": "testing"},
]
mem_before_est = get_mem()
for _ in range(5):
    est_tasks = effort.estimate_effort([dict(t) for t in sample_tasks])
mem_after_est = get_mem()
print(f"[6] During timeline / effort estimation (reusing shared model & vectors): {mem_after_est:.2f} MB (delta: {mem_after_est - mem_before_est:.2f} MB)")

# Architecture generation
mem_before_arch = get_mem()
for _ in range(5):
    kg_comps = kg.lookup_components(["payments", "auth", "chat"])
    arch_res = arch._build_from_kg({"domain": "fintech"}, kg_comps)
mem_after_arch = get_mem()
print(f"[7] During architecture generation: {mem_after_arch:.2f} MB (delta: {mem_after_arch - mem_before_arch:.2f} MB)")

# Test Concurrent requests simulation (10 parallel requests)
import concurrent.futures
mem_before_concurrent = get_mem()

def run_request(i):
    feat = ["user_auth", "payments", "analytics"] if i % 2 == 0 else ["chat", "video_streaming"]
    r_rag = rag.retrieve_similar(feat, top_k=3)
    r_eff = effort.estimate_effort([{"name": f"Task {i}", "component": "Backend", "type": "backend"}])
    return len(r_rag), len(r_eff)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(run_request, i) for i in range(10)]
    results = [f.result() for f in futures]

mem_after_concurrent = get_mem()
print(f"[8] During concurrent requests (10 simulated concurrent threads): {mem_after_concurrent:.2f} MB (delta: {mem_after_concurrent - mem_before_concurrent:.2f} MB)")

em_stats = get_embedding_manager().get_stats()
print(f"Embedding Manager Stats: {em_stats}")

print("-" * 50)
print(f"PEAK TOTAL RSS MEMORY CONSUMED: {get_mem():.2f} MB")
print("-" * 50)

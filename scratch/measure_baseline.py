"""
measure_baseline.py — Measure memory consumption of current Prompt2Plan baseline.
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

print(f"[1] Python base process startup: {get_mem():.2f} MB")

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

print(f"[2] After importing all backend modules: {get_mem():.2f} MB")

# Initialize DB and KG
db.init_db()
kg.initialize_kg()
print(f"[3] After DB + KG init: {get_mem():.2f} MB")

# Initialize RAG
mem_before_rag = get_mem()
rag.initialize_rag()
mem_after_rag = get_mem()
print(f"[4] After RAG init (SentenceTransformer #1 + FAISS #1): {mem_after_rag:.2f} MB (RAG added: {mem_after_rag - mem_before_rag:.2f} MB)")

# Initialize Effort Estimator
mem_before_effort = get_mem()
effort.initialize_estimator()
mem_after_effort = get_mem()
print(f"[5] After Effort Estimator init (SentenceTransformer #2 + FAISS #2 + GBR): {mem_after_effort:.2f} MB (Effort added: {mem_after_effort - mem_before_effort:.2f} MB)")

# Semantic Search / Retrieval
mem_before_search = get_mem()
for _ in range(5):
    res = rag.retrieve_similar(["chat", "real-time", "payments", "authentication"], top_k=3)
mem_after_search = get_mem()
print(f"[6] During semantic search / RAG retrieval: {mem_after_search:.2f} MB (delta: {mem_after_search - mem_before_search:.2f} MB)")

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
print(f"[7] During timeline / effort estimation: {mem_after_est:.2f} MB (delta: {mem_after_est - mem_before_est:.2f} MB)")

# Architecture fallback generation
mem_before_arch = get_mem()
for _ in range(5):
    kg_comps = kg.lookup_components(["payments", "auth", "chat"])
    arch_res = arch._build_from_kg({"domain": "fintech"}, kg_comps)
mem_after_arch = get_mem()
print(f"[8] During architecture generation: {mem_after_arch:.2f} MB (delta: {mem_after_arch - mem_before_arch:.2f} MB)")

print("-" * 50)
print(f"PEAK TOTAL RSS MEMORY CONSUMED: {get_mem():.2f} MB")
print("-" * 50)

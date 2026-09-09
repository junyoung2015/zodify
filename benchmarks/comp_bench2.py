# Historical development experiment; constraints/output are not equivalent.
# Use equivalent.py for maintained comparisons; do not publish these rankings.
"""Comparison benchmark - run with /tmp/zodify_bench_venv/bin/python"""
import time, statistics, subprocess, sys, os

os.chdir("/Users/eddie/zodify")
sys.path.insert(0, "/Users/eddie/zodify")

ROUNDS = 10000
WARMUP = 500
data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
results = []

# --- zodify ---
from zodify import validate
schema = {"name": str, "age": int, "email": str}
for _ in range(WARMUP):
    validate(schema, data)
times = []
for _ in range(ROUNDS):
    s = time.perf_counter()
    validate(schema, data)
    e = time.perf_counter()
    times.append((e - s) * 1e6)
med = statistics.median(times)
results.append(("zodify", med))

# --- pydantic v2 ---
from pydantic import BaseModel
class User(BaseModel):
    name: str
    age: int
    email: str
for _ in range(WARMUP):
    User(**data)
times = []
for _ in range(ROUNDS):
    s = time.perf_counter()
    User(**data)
    e = time.perf_counter()
    times.append((e - s) * 1e6)
med = statistics.median(times)
results.append(("pydantic v2", med))

# --- cerberus ---
from cerberus import Validator
cv = Validator({"name": {"type": "string"}, "age": {"type": "integer"}, "email": {"type": "string"}})
for _ in range(WARMUP):
    cv.validate(data)
times = []
for _ in range(ROUNDS):
    s = time.perf_counter()
    cv.validate(data)
    e = time.perf_counter()
    times.append((e - s) * 1e6)
med = statistics.median(times)
results.append(("cerberus", med))

# --- voluptuous ---
from voluptuous import Schema as VSchema, Required
vs = VSchema({Required("name"): str, Required("age"): int, Required("email"): str})
for _ in range(WARMUP):
    vs(data)
times = []
for _ in range(ROUNDS):
    s = time.perf_counter()
    vs(data)
    e = time.perf_counter()
    times.append((e - s) * 1e6)
med = statistics.median(times)
results.append(("voluptuous", med))

# --- schema ---
from schema import Schema as SSchema
ss = SSchema({"name": str, "age": int, "email": str})
for _ in range(WARMUP):
    ss.validate(data)
times = []
for _ in range(ROUNDS):
    s = time.perf_counter()
    ss.validate(data)
    e = time.perf_counter()
    times.append((e - s) * 1e6)
med = statistics.median(times)
results.append(("schema", med))

# --- Output ---
results.sort(key=lambda x: x[1])
fastest = results[0][1]
with open("/tmp/bench_results.txt", "w") as f:
    f.write("=== VALIDATION BENCHMARK (3-key dict, median of 10k runs) ===\n\n")
    for name, us in results:
        ratio = us / fastest
        ops = int(1_000_000 / us)
        tag = " (lowest time in this run)" if ratio == 1.0 else ""
        line = f"  {name:15s}  {us:8.2f} us/op  {ops:>10,} ops/sec  {ratio:.1f}x{tag}\n"
        f.write(line)
    f.write("\n")

print("Results written to /tmp/bench_results.txt")

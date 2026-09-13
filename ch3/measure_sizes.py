#!/usr/bin/env python3
"""Measure parkinfo.php response sizes on the live Apache/mod_deflate system.

Part 1 (always): for each of the 209 valid system states, set the state
directly in Redis and record the size of the parkinfo.php response body
(a) without Accept-Encoding (identity) and (b) with Accept-Encoding: gzip
(compressed by mod_deflate). Results go to /tmp/parkinfo_measurements.csv.

Part 2 (--walk): generate an Eulerian circuit over all 1088 valid
transitions (Hierholzer's algorithm), execute it against the live system
through HTTP POSTs to reserve.php/release.php (authenticated as the acting
user), and at every transition verify that both response sizes match the
mapping measured in Part 1 and that the Redis state matches the model.
Summary goes to /tmp/parkinfo_summary.json.

Standard library only; Redis is driven via redis-cli.
"""
import base64
import csv
import json
import subprocess
import sys
import urllib.request
from itertools import product

BASE = "http://localhost"
OCCUPANTS = ["johnson", "anonymous", "lowry", "hyde", "empty"]
LOCATIONS = ["stephens", "synge", "westland", "kildare"]
DLEN = {"johnson": 2, "anonymous": 4, "lowry": 0, "hyde": -1, "empty": 0}
PASSWORD = "parkpass"


def auth_header(user):
    tok = base64.b64encode(f"{user}:{PASSWORD}".encode()).decode()
    return {"Authorization": "Basic " + tok}


def http_get(path, user="lowry", gzip=False):
    headers = auth_header(user)
    if gzip:
        headers["Accept-Encoding"] = "gzip"
    req = urllib.request.Request(BASE + path, headers=headers)
    with urllib.request.urlopen(req) as r:
        body = r.read()
        return body, r.headers.get("Content-Encoding", "identity")


def http_post(path, data, user):
    headers = auth_header(user)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(BASE + path, data=data.encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req) as r:
        r.read()


def redis_set_state(state):
    for loc, val in zip(LOCATIONS, state):
        subprocess.run(["redis-cli", "set", loc, val],
                       check=True, capture_output=True)


def redis_get_state():
    vals = []
    for loc in LOCATIONS:
        out = subprocess.run(["redis-cli", "get", loc],
                             check=True, capture_output=True, text=True)
        v = out.stdout.strip()
        vals.append("empty" if v in ("", "(nil)") else v)
    return tuple(vals)


def valid_states():
    return [s for s in product(OCCUPANTS, repeat=4)
            if all(s.count(n) <= 1 for n in OCCUPANTS if n != "empty")]


def lpark(state):
    return 1052 + sum(DLEN[x] for x in state)


def part1(states):
    rows = []
    dlen_mismatches = 0
    for i, s in enumerate(states):
        redis_set_state(s)
        body_id, enc_id = http_get("/parkinfo.php", gzip=False)
        body_gz, enc_gz = http_get("/parkinfo.php", gzip=True)
        if len(body_id) != lpark(s):
            dlen_mismatches += 1
        rows.append({"idx": i,
                     "stephens": s[0], "synge": s[1],
                     "westland": s[2], "kildare": s[3],
                     "uncompressed": len(body_id), "enc_id": enc_id,
                     "compressed": len(body_gz), "enc_gz": enc_gz})
    with open("/tmp/parkinfo_measurements.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    sizes = {}
    for r in rows:
        sizes.setdefault(r["compressed"], []).append(r)
    print(f"part1: {len(rows)} states measured; "
          f"{dlen_mismatches} identity-size mismatches vs dlen model; "
          f"{len(sizes)} distinct compressed sizes; "
          f"encodings: id={set(r['enc_id'] for r in rows)}, "
          f"gz={set(r['enc_gz'] for r in rows)}")
    return rows, dlen_mismatches


def build_euler_circuit(states):
    """Hierholzer's algorithm over the reserve/release transition graph."""
    adj = {s: [] for s in states}
    n_edges = 0
    for s in states:
        parked = [x for x in s if x != "empty"]
        for i, loc in enumerate(LOCATIONS):
            if s[i] == "empty":
                for user in OCCUPANTS[:4]:
                    if user not in parked:
                        t = s[:i] + (user,) + s[i + 1:]
                        adj[s].append((t, ("reserve", loc, user)))
                        n_edges += 1
            else:
                t = s[:i] + ("empty",) + s[i + 1:]
                adj[s].append((t, ("release", s[i])))
                n_edges += 1
    start = ("empty",) * 4
    stack = [(start, None)]
    circuit = []
    it = {s: iter(edges) for s, edges in adj.items()}
    remaining = {s: len(edges) for s, edges in adj.items()}
    path = []
    node = start
    while stack:
        node, via = stack[-1]
        if remaining[node]:
            nxt, action = next(it[node])
            remaining[node] -= 1
            stack.append((nxt, action))
        else:
            path.append(stack.pop())
    path.reverse()
    circuit = path
    return circuit, n_edges


def part2(states, rows):
    comp_by_state = {(r["stephens"], r["synge"], r["westland"], r["kildare"]):
                     r["compressed"] for r in rows}
    circuit, n_edges = build_euler_circuit(states)
    print(f"part2: euler circuit over {n_edges} edges, "
          f"walk length {len(circuit) - 1}")
    redis_set_state(("empty",) * 4)
    failures = []
    steps = 0
    for node, action in circuit[1:]:
        if action[0] == "reserve":
            _, loc, user = action
            http_post("/reserve.php", "loc=" + loc, user)
        else:
            _, user = action
            http_post("/release.php", "", user)
        steps += 1
        actual = redis_get_state()
        if actual != node:
            failures.append({"step": steps, "kind": "state",
                             "expected": node, "actual": actual})
            redis_set_state(node)  # resync and continue
        body_id, _ = http_get("/parkinfo.php", gzip=False)
        body_gz, _ = http_get("/parkinfo.php", gzip=True)
        if len(body_id) != lpark(node):
            failures.append({"step": steps, "kind": "identity-size",
                             "expected": lpark(node), "got": len(body_id)})
        if len(body_gz) != comp_by_state[node]:
            failures.append({"step": steps, "kind": "compressed-size",
                             "expected": comp_by_state[node],
                             "got": len(body_gz)})
        if steps % 200 == 0:
            print(f"  ... {steps}/{n_edges} transitions, "
                  f"{len(failures)} failures so far")
    print(f"part2: executed {steps} transitions, {len(failures)} failures")
    return {"edges": n_edges, "steps": steps,
            "failures": failures[:50], "n_failures": len(failures)}


def main():
    states = valid_states()
    assert len(states) == 209
    rows, dlen_mismatches = part1(states)
    summary = {"states": len(rows),
               "dlen_mismatches": dlen_mismatches,
               "distinct_compressed": len({r["compressed"] for r in rows})}
    if "--walk" in sys.argv:
        summary["walk"] = part2(states, rows)
    with open("/tmp/parkinfo_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary)[:2000])


if __name__ == "__main__":
    main()

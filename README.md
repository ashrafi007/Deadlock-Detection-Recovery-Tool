# 🔒 Deadlock Detection & Recovery Tool

> An Operating Systems course project that simulates deadlock detection using **Resource Allocation Graphs (RAG)** and resolves deadlocks through two recovery strategies — **Process Termination** and **Resource Preemption**.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph_Library-orange?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Course](https://img.shields.io/badge/Course-Operating_Systems-red?style=for-the-badge)

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [How to Run](#-how-to-run)
- [Scenarios](#-scenarios)
- [How It Works](#-how-it-works)
- [OS Concepts Covered](#-os-concepts-covered)
- [References](#-references)

---

## 📖 About the Project

Deadlock is a critical problem in operating systems where a set of processes are permanently blocked — each waiting for a resource held by another. This tool simulates a real OS environment and demonstrates how deadlocks are **detected** and **recovered from**.

The project is built around two core OS features:

| Feature | Description |
|---|---|
| **Feature 1 — Detection** | Builds a Resource Allocation Graph and uses DFS cycle detection to find deadlocked processes |
| **Feature 2 — Recovery** | Resolves the deadlock by either terminating the lowest-cost process or preempting a resource |

---

## ✨ Features

### Feature 1 — Deadlock Detection via RAG
- Models all processes and resources as a directed graph
- Adds **assignment edges** (resource → process) and **request edges** (process → resource)
- Runs **Depth-First Search (DFS)** to detect cycles
- Reports the exact cycle path and all deadlocked processes
- Outputs a colored RAG visualization (PNG)

### Feature 2 — Deadlock Recovery
- **Strategy A — Process Termination**: Kills the lowest-cost process in the cycle, releases its resources, re-checks for deadlock. Repeats until safe.
- **Strategy B — Resource Preemption**: Forcibly takes a resource from a victim process, reassigns it to unblock the waiting process. Includes **starvation prevention** via preemption count tracking.
- Logs every step taken during recovery
- Outputs an updated RAG showing the safe state

---

## 📁 Project Structure

```
deadlock-tool/
│
├── main.py                   # Entry point — interactive CLI menu
├── demo.py                   # Auto-runs 3-process deadlock demo
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
│
├── core/
│   ├── rag.py                # Resource Allocation Graph class
│   ├── detector.py           # DFS cycle detection — Feature 1
│   └── recovery.py           # Recovery strategies — Feature 2
│
├── models/
│   ├── process.py            # Process model with recovery cost heuristic
│   └── resource.py           # Resource model with instance tracking
│
├── visualizer/
│   └── graph_viz.py          # NetworkX + Matplotlib graph rendering
│
├── tests/
│   ├── test_detector.py      # 5 unit tests for Feature 1
│   └── test_recovery.py      # 5 unit tests for Feature 2
│
└── examples/
    ├── scenario1.json         # Classic 2-process deadlock
    ├── scenario2.json         # Safe state — no deadlock
    └── scenario3.json         # 3-process circular deadlock
```

---

## 🛠 Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| NetworkX | 3.2.1 | Graph construction and DFS |
| Matplotlib | 3.8.2 | RAG visualization |
| argparse | built-in | CLI interface |
| unittest | built-in | Unit testing |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ashrafi007/Deadlock-Detection-Recovery-Tool.git
cd Deadlock-Detection-Recovery-Tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶ How to Run

### Interactive mode

```bash
python main.py
```

You will be prompted to:
1. Select a scenario (1, 2, or 3)
2. See deadlock detection result in the terminal
3. Choose a recovery strategy (Termination or Preemption)
4. Two graph images are saved: `rag_before.png` and `rag_after.png`

---

### Auto demo (for presentation)

```bash
python demo.py
```

Automatically runs the 3-process circular deadlock scenario with no user input. Outputs `demo_before.png` and `demo_after.png`.

---

### Run all unit tests

```bash
python main.py --test
```

Expected: **10 tests, all passing.**

---

## 🗂 Scenarios

Three pre-built scenarios are included in the `examples/` folder:

| Scenario | File | Description | Expected Result |
|---|---|---|---|
| 1 | `scenario1.json` | P1 holds R1 wants R2, P2 holds R2 wants R1 | ❌ DEADLOCK |
| 2 | `scenario2.json` | No circular wait | ✅ SAFE STATE |
| 3 | `scenario3.json` | P1→R2→P2→R3→P3→R1→P1 | ❌ DEADLOCK |

---

## ⚙ How It Works

### Detection Algorithm

```
1. Build directed graph from process/resource state
2. For each unvisited node, run DFS
3. Track visited set and recursion stack
4. If a back edge is found → cycle detected → DEADLOCK
5. Extract cycle path and deadlocked process list
```

**Time complexity:** `O(V + E)` — V = nodes, E = edges

---

### Recovery — Strategy A (Process Termination)

```
1. Detect deadlock → get deadlocked process list
2. Score each process using recovery cost heuristic:
       cost = cpu_time_used - (held_resources × 10) + (priority × 50)
3. Terminate lowest-cost process → release all its resources
4. Re-run detection → if still deadlocked, repeat
5. Stop when system reaches safe state
```

---

### Recovery — Strategy B (Resource Preemption)

```
1. Detect deadlock → find which process is waiting for what
2. Find a process that holds the needed resource (victim)
3. Sort victims by preemption count (starvation prevention)
4. Preempt the resource → remove from victim → give to waiting process
5. Simulate rollback of victim to last checkpoint
6. Re-run detection → repeat if needed
```

---

### RAG Visualization Legend

| Element | Color | Shape | Meaning |
|---|---|---|---|
| Process node | 🔵 Blue | Circle | A process in the system |
| Resource node | 🟢 Green | Square | A resource type |
| Cycle node | 🔴 Red | Circle/Square | Part of a deadlock cycle |
| Assignment edge | ⚫ Black solid | Arrow | Resource is HELD by process |
| Request edge | 🟠 Orange dashed | Arrow | Process is WAITING for resource |

---

## 📚 OS Concepts Covered

| Concept | Where Applied |
|---|---|
| Coffman's 4 deadlock conditions | Scenario design |
| Resource Allocation Graph (RAG) | Core data structure — Feature 1 |
| DFS cycle detection | Detection algorithm — Feature 1 |
| Process termination as recovery | Strategy A — Feature 2 |
| Resource preemption as recovery | Strategy B — Feature 2 |
| Starvation prevention | Preemption count tracking |
| Safe state vs unsafe state | Post-recovery verification |

---


## 👤 Author

**Ashrafi**
- GitHub: [@ashrafi007](https://github.com/ashrafi007)

---

## 📄 License

All Rights Reserved.

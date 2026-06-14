# 🚀 DSA Pattern Discovery Tool

A dynamic full-stack developer workbench that analyzes programming code snippets to instantly extract their primary Data Structures & Algorithms (DSA) core structural patterns (e.g., Two Pointers, Sliding Window, Depth-First Search). It breaks down the applied architectural logic and curates direct, targeted LeetCode practice problems based on the discovered archetype.

---

## ✨ Features

* **Instant Structural Diagnostics:** Paste code written in Python, Java, JavaScript, or C++, and discover the underlying DSA archetype in seconds.
* **Smart Practice Arenas:** Generates three curated, real-world LeetCode problem links classified by difficulty (Easy, Medium, Hard) matching the detected algorithm.
* **Persistent Local Log Pipeline:** Automatically logs every analysis snapshot into a local SQL-backed transaction history feed for easy reference.
* **Defensive Edge-Case Handling:** Implemented local regex filtering mechanics to clean model outputs, making code parsing completely robust.

---

## 🛠️ Architecture & Tech Stack

* **Frontend:** Clean, responsive, dark-mode CSS UI panel with dynamic asynchronous AJAX components.
* **Backend Framework:** Python Flask application server managing custom API gateway configurations.
* **Database Ledger:** SQLite3 database layer operating under absolute workspace context pathing to prevent runtime file sync collisions.
* **AI Engine Optimization:** Integrated OpenRouter `google/gemini-2.5-flash` client with explicit `max_tokens` allocation guardrails to ensure free-tier compliance and ultra-low server latency.

---

## ⚙️ Setup and Installation

### 1. Clone the Workspace Repository
```bash
git clone [https://github.com/s4eee/dsa-pattern-visualizer.git](https://github.com/s4eee/dsa-pattern-visualizer.git)
cd dsa-pattern-visualizer

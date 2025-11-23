# 🏗️ Technical Architecture & Engineering

This document provides a deep dive into the engineering decisions, architecture, and algorithms powering the AI Security Scanner.

## 📐 System Architecture

The system follows a modular architecture separating the **Agent** (Brain), **Environment** (World), and **Scanner** (Body).

```mermaid
graph TD
    A[Security Auditor] -->|Controls| B(Website Explorer)
    A -->|Controls| C(DQN Agent)

    B -->|Crawls| D[Target Website]
    C -->|Attacks| D

    subgraph "AI Core (GPU Accelerated)"
    C -->|State| E[NeuralNetworkBrain]
    E -->|Q-Values| C
    C -->|Experience| F[ExperienceMemory O(1)]
    end

    subgraph "Environment"
    D -->|Response| G[WebSecurityGym]
    G -->|Reward/State| C
  1.  `page_id`: Current page identifier.
  2.  `status_code`: Normalized HTTP status.
  3.  `found_vulnerability`: Boolean flag.
  4.  `found_sensitive_data`: Boolean flag (CTF flags).
  5.  `triggered_waf`: Boolean flag.
  6.  `got_rate_limited`: Boolean flag.
  7.  `auth_token`: JWT token presence.
  8.  `last_response_time`: Normalized latency (for Time-Based SQLi).
  9.  `content_variance`: Anomaly detection metric.
  10. `input_count`: Complexity metric.
- **Action Space (15 Actions)**:
  - Navigation (Home, Login, Search...)
  - Attacks (SQLi, XSS, IDOR, SSRF...)
  - Advanced (Time-Based SQLi, Polyglot XSS, Fuzzing)
- **Optimization**:
  - **Session Pooling**: Uses `requests.Session` with `HTTPAdapter` to reuse TCP connections, reducing latency by ~50%.

### 3. The Payload Manager (`agent/payload_manager.py`)

- **Purpose**: Centralized management of attack vectors.
- **Capabilities**:
  - **Polyglots**: Complex payloads designed to bypass multiple filters.
  - **Fuzzing**: Random data generation for stress testing.
  - **Context-Aware**: Delivers specific payloads based on attack type.

## ⚡ Algorithms & Data Structures

### 1. O(1) Experience Replay

Instead of a standard Python list `[]` or `deque`, we use fixed-size Numpy arrays.

- **Insertion**: `buffer[ptr] = data` -> **O(1)**
- **Sampling**: `buffer[indices]` -> **O(1)** (Vectorized)
- **Memory**: Pre-allocated, no GC overhead.

### 2. BFS Crawling (Scanner)

The `WebsiteExplorer` uses Breadth-First Search (BFS) to map the website.

- **Queue**: `collections.deque` for **O(1)** pops/appends.
- **Visited Set**: `set()` for **O(1)** lookup of visited URLs.
- **Complexity**: O(V+E) where V is pages and E is links.

### 3. Epsilon-Greedy Exploration

The agent balances exploration (trying new things) and exploitation (using what works).

- **Formula**: `epsilon = max(min_epsilon, epsilon * decay_rate)`
- **Logic**: Starts curious (100% random), becomes professional (99% optimal).

## 🖥️ Hardware Utilization

- **GPU**: PyTorch tensors are moved to `cuda:0`.
- **CPU**: Handles environment interaction and HTTP requests.
- **RAM**: Efficiently managed via fixed-size buffers.
```

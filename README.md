# Gem — Scrape-Powered AI Helper

A lightweight AI agent that scrapes **Reddit**, **Google**, and **Bing** in real time using **Bright Data APIs**, then reasons over the collected data using a **locally running Gemma 3B** model. No RAG. No vector databases. Just raw scraping → LLM inference, end to end.

---

##  How It Works

```
User Query
    │
    ▼
┌─────────────────────────────┐
│      Query Planner          │  ← decides which sources to hit
└────────────┬────────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
 Google    Bing    Reddit
    └────────┼────────┘
             │  Bright Data APIs
             ▼
┌─────────────────────────────┐
│      Data Aggregator        │  ← cleans + chunks scraped content
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│    Gemma 3B (local)         │  ← runs via Ollama or llama.cpp
│    Reasoning + Response     │
└─────────────────────────────┘
             │
             ▼
        Final Answer
```

---




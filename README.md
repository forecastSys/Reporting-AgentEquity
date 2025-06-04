# 📈 Reporting-AgentEquity  
**AI-powered multi-agent system for automated equity research reports**

`Reporting-AgentEquity` is a scalable, intelligent system that automates the generation of professional equity research reports. It integrates structured financial data pipelines, agent-based workflows using [LangGraph](https://github.com/langchain-ai/langgraph), and prompt-driven large language models (LLMs) to produce consistent, high-quality financial analysis.

---

## 🧠 Overview

This project uses a **multi-agent architecture** to simulate an equity research team—automating roles such as analysts, evaluators, and supervisors. Each agent is orchestrated using **LangGraph** for modular, stateful workflows and tracked with **Langfuse** for full observability.

The system enables end-to-end automation from raw financial data to final investment reports in Markdown, PDF, or HTML formats.

---

## ✨ Key Features

- 🤖 **Agent-based LLM orchestration with LangGraph**
- 📊 **Structured financial data integration** (MySQL, CSV, APIs)
- 🧠 **Context-aware prompting per report section**
- 🕵️‍♀️ **Evaluator and supervisor roles** for fact-checking and compliance
- 📄 **Multi-format report output** (Markdown, PDF, HTML)
- 📈 **Prompt tracking and analytics with Langfuse**
- 🔌 **Pluggable LLM support** (OpenAI, local models, API backends)
- 
---

## 🏗️ Architecture

```plaintext
[Data Source (MySQL, CSV, API)]
        ↓
[Financial Data Preprocessing]
        ↓
[Forecasting / Feature Engineering]
        ↓
[LangGraph Agent Teams]
    ├── Business Strategy & Outlook Team
    ├── Fair Value & Profit Drivers Team
    ├── Risk & Uncertainty Team
    └── etc.,
        ↓
[Assitant & Evaluator & Supervisor Agents]
        ↓
[Final Investment Report Compilation]
        ↓
[Output: Markdown / PDF / HTML]

# 📈 Reporting-AgentEquity
**AI-powered multi-agent system for automated equity research reports**

`Reporting-AgentEquity` is a scalable, intelligent system that automates the generation of professional equity research reports. It integrates structured financial data pipelines, agent-based workflows using [LangGraph](https://github.com/langchain-ai/langgraph), and prompt-driven large language models (LLMs) to produce consistent, high-quality financial analysis.

---

## 🧠 Overview

This project uses a **multi-agent architecture** to simulate an equity research team—automating roles such as analysts, evaluators, and supervisors. Each agent is orchestrated using **LangGraph** for modular, stateful workflows and tracked with **Langfuse** for full observability.

The system enables end-to-end automation from raw financial data to final investment reports in JSON, Markdown, PDF, or HTML formats.

---

## ✨ Key Features

- 🤖 **Agent-based LLM orchestration with LangGraph**
- 📊 **Multi-source financial data integration** (FMP API, Yahoo Finance, MySQL, MongoDB, SEC Filings)
- 🧠 **Context-aware prompting per report section**
- 🕵️‍♀️ **Evaluator and supervisor roles** for fact-checking and compliance
- 📄 **Multi-format report output** (JSON, Markdown, PDF, HTML)
- 📈 **Prompt tracking and analytics with Langfuse**
- 🔌 **Pluggable LLM support** (OpenAI GPT-4o with extensible architecture)
- 🏢 **Comprehensive company analysis** including competitor research
- 🛠️ **Modular financial data extractors** with validation and decorators

---

## 🏗️ Architecture

```plaintext
[Data Sources]
├── FMP API (Financial Modeling Prep)
├── Yahoo Finance
├── MySQL Database
├── MongoDB
└── SEC Filings
        ↓
[Financial Data Extractors & Validators]
        ↓
[LangGraph Agent Teams]
├── BSO Team (Business Strategy & Outlook)
├── FVPD Team (Fair Value & Profit Drivers)
├── RU Team (Risk & Uncertainty)
├── BD Team (Business Description)
└── CA Team (Competitive Analysis)
        ↓
[Agent Workflow with State Management]
├── Team Supervisors
├── Assistant Writers
└── Evaluators
        ↓
[Report Compilation & Output]
        ↓
[Final Investment Report: JSON/Markdown/PDF/HTML]
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required API keys (see Configuration section)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Reporting-AgentEquity.git
cd Reporting-AgentEquity
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (see Configuration section)

### Basic Usage

```python
from src.report.agent.workflow import AgentWorkflow

# Initialize the workflow for NVDA Q1 2025 report
agent = AgentWorkflow('NVDA', 2025, 1)

# Generate comprehensive investment report
report_data = agent.run()
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# LLM Configuration
OPEN_API_KEY=your_openai_api_key_here

# Financial Data APIs
FMP_API_KEY=your_fmp_api_key_here

# Database Configuration (Optional)
MYSQL_USER=your_mysql_username
MYSQL_PASS=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

MONGODB_URI=your_mongodb_connection_string
DB=your_database_name
ECC_COLLECTION=your_collection_name

# Observability (Optional)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_PRIVATE_KEY=your_langfuse_private_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 📊 Data Sources

The system integrates with multiple financial data providers:

- **FMP API**: Comprehensive financial statements, ratios, and company data
- **Yahoo Finance**: Market data and historical pricing
- **SEC Filings**: Direct access to regulatory filings
- **MySQL/MongoDB**: Local database storage for cached data
- **Custom Data**: Support for CSV and other structured formats

---

## 🤖 Agent Teams

The system employs specialized agent teams for different aspects of equity analysis:

| Team | Responsibility | Key Focus Areas |
|------|----------------|----------------|
| **BSO (Business Strategy & Outlook)** | Strategic analysis and future outlook | Market positioning, competitive advantages, growth strategy |
| **FVPD (Fair Value & Profit Drivers)** | Valuation and profitability analysis | DCF models, comparable analysis, margin analysis |
| **RU (Risk & Uncertainty)** | Risk assessment and uncertainty analysis | Market risks, operational risks, financial risks |
| **BD (Business Description)** | Company overview and business model | Products/services, revenue streams, operations |
| **CA (Competitive Analysis)** | Competitive landscape analysis | Market share, competitor positioning, industry trends |

---

## 🔧 Project Structure

```
src/
├── abstractions/          # Abstract base classes and interfaces
├── config/               # Configuration management
├── database/             # Database connection utilities
├── fdata_extractors/     # Financial data extraction modules
│   ├── fmp_extractors/   # Financial Modeling Prep API
│   ├── yfinance_extractors/  # Yahoo Finance integration
│   ├── localdb_extractors/   # Local database queries
│   └── decorator/        # Data processing decorators
├── logger/               # Logging utilities
└── report/               # Core reporting system
    ├── agent/            # Agent orchestration and teams
    ├── llm/              # LLM integration layer
    ├── models/           # Data models and schemas
    ├── parser/           # Output parsing utilities
    └── prompts/          # Prompt templates and management
```

---

## 📈 Output Formats

The system generates reports in multiple formats:

- **JSON**: Structured data for programmatic access
- **Markdown**: Human-readable format with formatting
- **PDF**: Professional presentation-ready reports
- **HTML**: Web-friendly format with styling

---

## 🔍 Monitoring & Observability

Integration with **Langfuse** provides:
- Real-time agent execution tracking
- Prompt performance analytics
- Cost monitoring and optimization
- Debug capabilities for agent workflows

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- [Langfuse](https://langfuse.com/) for observability and tracking
- [Financial Modeling Prep](https://financialmodelingprep.com/) for financial data
- [OpenAI](https://openai.com/) for LLM capabilities

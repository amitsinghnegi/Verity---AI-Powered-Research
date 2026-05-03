# ✦ Verity — AI-Powered Research Assistant

Verity is a sleek, multi-agent AI research tool built with **Streamlit**, **LangChain**, and **Google Gemini**. Give it a topic, and a team of specialized AI agents will autonomously scour the web, extract deep insights, write a structured report, and critically evaluate the final draft.

![UI Theme](https://img.shields.io/badge/UI-Dark%2FLight_Mode-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-Agents-orange)
![Gemini](https://img.shields.io/badge/Model-Gemini_3.1_Flash-blueviolet)

## 🚀 How It Works

Verity utilizes a 4-step autonomous pipeline to generate high-quality research:

1. **🔍 Search Agent:** Uses the Tavily API to find recent, reliable, and detailed web sources based on your prompt.
2. **🌐 Reader/Scrape Agent:** Analyzes search results, picks the most credible URL, and scrapes the raw HTML for deep content.
3. **📝 Writer Agent:** Synthesizes the gathered research into a structured, professional report (Introduction, Key Findings, Conclusion, Sources).
4. **💬 Critic Agent:** Acts as a sharp research critic to evaluate the draft, providing a score out of 10, highlighting strengths, and pointing out areas to improve.

## ✨ Features

* **Sleek UI/UX:** A highly polished Streamlit frontend featuring dynamic Dark/Light themes, smooth progress tracking, and interactive expanders.
* **Smart Placeholders:** Hit `Tab` in the input field to auto-fill trending research topics.
* **One-Click Export:** Download the final research report, along with the raw search data and critic feedback, as a clean `.md` file.
* **State Persistence:** Toggling themes or interacting with the UI won't wipe your generated research.
* **Modular Backend:** Clean separation of concerns across UI, agent logic, tool definitions, and pipeline execution.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Orchestration:** [LangChain](https://python.langchain.com/)
* **LLM:** Google Gemini (`gemini-3.1-flash-lite-preview`)
* **Search Tool:** Tavily Search API
* **Scraping:** BeautifulSoup4 & Requests

---

## 🛠️ Tech Stack

- **LLM**: Google Gemini (via LangChain)
- **Framework**: LangChain Agents + Chains
- **Frontend**: Streamlit
- **Search API**: Tavily
- **Web Scraping**: BeautifulSoup + Requests
- **Environment**: dotenv

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/verity-ai-research.git
cd verity-ai-research
```

### 2. Install dependencies

```bash
pip install .
```

### 3. Configure environment variables

```bash
GEMINI_API_KEY=your_google_gemini_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🧪 Example Use Cases
- Market research
- Technical deep dives (LLMs, systems design)
- Academic research
- Competitive analysis
- Learning new domains quickly

---

## 📥 Output
The system generates:
- 📄 Structured research report
- 📊 Critic evaluation (score + feedback)
- 📎 Downloadable Markdown file

---

## 🔥 Why This Project Matters

- This project demonstrates:
    - Multi-agent orchestration
    - Tool-augmented LLM workflows
    - Retrieval + reasoning pipeline
    - Automated evaluation loop

This is the same architecture pattern used in production-grade AI systems.

---


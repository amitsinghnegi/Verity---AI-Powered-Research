# ✦ Verity — AI-Powered Research Assistant

Verity is an end-to-end **AI research pipeline** that automates how you gather, analyze, and evaluate information on any topic.

It uses multiple AI agents to:
- Search the web
- Scrape relevant sources
- Generate structured research reports
- Critically evaluate the output

All wrapped in an interactive **Streamlit UI**.

---

## 🚀 Features

- 🔍 **Search Agent**  
  Finds recent and reliable information using web search tools : Tavily Search 

- 🌐 **Scraper Agent**  
  Extracts clean content from selected URLs for deeper insights : Beautiful Soup

- 📝 **Writer Agent**  
  Generates structured research reports with:
  - Introduction  
  - Key Findings  
  - Conclusion  
  - Sources :contentReference[oaicite:2]{index=2}  

- 💬 **Critic Agent**  
  Evaluates report quality with:
  - Score  
  - Strengths  
  - Areas to Improve  
  - Verdict :contentReference[oaicite:3]{index=3}  

- 📊 **Streamlit UI**
  - Step-by-step pipeline tracking  
  - Expandable sections for each stage  
  - Markdown download support :contentReference[oaicite:4]{index=4}  

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

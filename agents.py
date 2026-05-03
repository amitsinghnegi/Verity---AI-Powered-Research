import os
from dotenv import load_dotenv
load_dotenv()

if os.environ.get("GEMINI_API_KEY") is not None:
    print("GEMINI_API_KEY is set")
if os.environ.get('TAVILY_API_KEY') is not None:
    print("TAVILY_API_KEY is set")

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

from langchain.agents import create_agent
from tools import scrape_url, web_search

def build_search_agent():
    return create_agent(model=llm, tools=[web_search])

def build_scrape_agent():
    return create_agent(model=llm, tools=[scrape_url])

#writer chain 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic prompt

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
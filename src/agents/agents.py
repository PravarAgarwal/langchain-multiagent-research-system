from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import scrape_url, web_search
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_retries=5,
    max_tokens=None,
    timeout=None
    )

# First Agent
def build_scrape_agent():
    return create_agent(
        llm = llm,
        tools=[scrape_url]
    )


# Second Agent
def build_search_tool():
    return create_agent(
        llm = llm,
        tools=[web_search]
    )


# writer prompt
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer, Write clear, structured and insightful reports"),
    ("human", """Write detailed research report on the topic below.
    
    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be detailed, factual and professional.
    """)
])

writer_chain = writer_prompt | llm | StrOutputParser()


# Critic Prompt
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a sharp and constructive research critic. Be honest and specific"),
    ("human", """ Review the research report below and evaluate it strictly.
    
    Report:
    {report}

    Respond in this exact format:
    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to improve:
    - ...
    - ...
    
    One Line Verdict:
    - ...

    """)
])

critic_chain = critic_prompt | llm | StrOutputParser()

def main():
    print("sab badhiya hai...")

if __name__ == "__main__":
    main()

# pipeline.py (Updated)

from agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain

def _extract_text(raw):
    # Normalize possible outputs from LangChain pipelines to a string
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        # Common shapes
        if isinstance(raw.get("content"), str):
            return raw["content"]
        if isinstance(raw.get("text"), str):
            return raw["text"]
        if isinstance(raw.get("messages"), list) and raw["messages"]:
            last = raw["messages"][-1]
            if isinstance(last, dict) and isinstance(last.get("content"), str):
                return last["content"]
            if isinstance(last, dict) and isinstance(last.get("text"), str):
                return last["text"]
    if isinstance(raw, list):
        texts = []
        for item in raw:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
        if texts:
            return "\n\n".join(texts)
    return str(raw)


def run_research_pipeline(topic: str) -> dict:
    state = {}
    
    print('\n', '='*50, '\n')
    print(f"🎯Step 1: Researching {topic}")
    print('\n', '='*50, '\n')

    search_agent = build_search_agent()
    search_result = search_agent.invoke({ 
                            "messages" : [
                                ("user", f"Find recent, reliable and detailed information about: {topic}")
                            ]
                    }) # type: ignore

    try:
        state["search_results"] = _extract_text(search_result['messages'][-1].content)
    except Exception as e:
        state["search_results"] = f"Error extracting search results: {e}"

    print("\n search result ",state['search_results'])

    print('\n', '='*50, '\n')
    print(f"🎯Step 2: Reader agent is scraping top resources ...")
    print('\n', '='*50, '\n')

    reader_agent = build_scrape_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:500]}"
        )]
    }) # type: ignore

    try:
        state["scraped_content"] = _extract_text(reader_result['messages'][-1].content)
    except Exception as e:
        state["scraped_content"] = f"Error extracting scraped content: {e}"

    print("\n scraped content ",state['scraped_content'])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    writer_out = writer_chain.invoke({"topic": topic, "research": research_combined})
    state["report"] = _extract_text(writer_out)

    print("\nFinal report ",state['report'])

    #step 4 - critic chain 

    print("\n"+" ="*50)
    print("step 4 - Critic is evaluating the report ...")
    print("="*50)

    critic_out = critic_chain.invoke({"report": state["report"]})
    state["feedback"] = _extract_text(critic_out)

    print("\n critic ",state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("Enter topic: ")
    run_research_pipeline(topic)
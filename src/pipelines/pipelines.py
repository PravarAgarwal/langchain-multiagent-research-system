from src.agents.agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str, progress_callback=None):

    state = {}

    # ============================================================
    # STEP 1 — SEARCH AGENT
    # ============================================================

    print("\n" + " =" * 50)
    print("Step 1: Search Agent Working...")
    print("=" * 50)

    # Tell the UI that Search Agent has started
    if progress_callback:
        progress_callback("search", "working")

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            (
                "user",
                f"Find recent reliable detailed information about {topic}"
            )
        ]
    })

    state["search_results"] = search_result["messages"][-1].content

    print("\nSearch Result:\n", state["search_results"])

    # Tell the UI that Search Agent has finished
    if progress_callback:
        progress_callback("search", "completed")


    # ============================================================
    # STEP 2 — READER AGENT
    # ============================================================

    print("\n" + " =" * 50)
    print("Step 2: Reader Agent Working...")
    print("=" * 50)

    # Tell the UI that Reader Agent has started
    if progress_callback:
        progress_callback("reader", "working")

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"Based on the following search results on the '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\nScraped Content:\n", state["scraped_content"])

    # Tell the UI that Reader Agent has finished
    if progress_callback:
        progress_callback("reader", "completed")


    # ============================================================
    # STEP 3 — WRITER
    # ============================================================

    print("\n" + " =" * 50)
    print("Step 3: Writer is drafting the report...")
    print("=" * 50)

    # Tell the UI that Writer has started
    if progress_callback:
        progress_callback("writer", "working")

    research_combined = (
        f"SEARCH RESULTS:\n"
        f"{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n"
        f"{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n", state["report"])

    # Tell the UI that Writer has finished
    if progress_callback:
        progress_callback("writer", "completed")


    # ============================================================
    # STEP 4 — CRITIC
    # ============================================================

    print("\n" + " =" * 50)
    print("Step 4: Critic is Reviewing the Report...")
    print("=" * 50)

    # Tell the UI that Critic has started
    if progress_callback:
        progress_callback("critic", "working")

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCritic Report:\n", state["feedback"])

    # Tell the UI that Critic has finished
    if progress_callback:
        progress_callback("critic", "completed")


    # ============================================================
    # RETURN COMPLETE PIPELINE RESULT
    # ============================================================

    return state
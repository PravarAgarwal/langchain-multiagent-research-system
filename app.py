import streamlit as st

from src.pipelines.pipelines import run_research_pipeline


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔎 AI Research Agent")

st.write(
    "Enter a topic and let the Search, Reader, Writer, "
    "and Critic agents research and generate a report."
)

st.divider()


# ============================================================
# TOPIC INPUT
# ============================================================

topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Latest developments in AI agents"
)


# ============================================================
# START RESEARCH
# ============================================================

if st.button("🚀 Start Research", type="primary"):

    # --------------------------------------------------------
    # Validate topic
    # --------------------------------------------------------

    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()


    # --------------------------------------------------------
    # Create UI placeholders
    # --------------------------------------------------------

    st.subheader("Agent Progress")

    search_status = st.empty()
    reader_status = st.empty()
    writer_status = st.empty()
    critic_status = st.empty()

    progress_bar = st.progress(0)


    # ========================================================
    # CALLBACK FUNCTION
    # ========================================================

    def update_progress(agent, status):

        if agent == "search":

            if status == "working":
                search_status.info("🔎 Search Agent is working...")

            elif status == "completed":
                search_status.success("🔎 Search Agent completed")
                progress_bar.progress(25)


        elif agent == "reader":

            if status == "working":
                reader_status.info("📖 Reader Agent is working...")

            elif status == "completed":
                reader_status.success("📖 Reader Agent completed")
                progress_bar.progress(50)


        elif agent == "writer":

            if status == "working":
                writer_status.info("✍️ Writer is drafting the report...")

            elif status == "completed":
                writer_status.success("✍️ Writer completed")
                progress_bar.progress(75)


        elif agent == "critic":

            if status == "working":
                critic_status.info("🧐 Critic is reviewing the report...")

            elif status == "completed":
                critic_status.success("🧐 Critic completed")
                progress_bar.progress(100)


    # ========================================================
    # RUN PIPELINE
    # ========================================================

    try:

        state = run_research_pipeline(
            topic,
            progress_callback=update_progress
        )


        # ----------------------------------------------------
        # Pipeline completed
        # ----------------------------------------------------

        st.success("✅ Research pipeline completed!")

        st.divider()


        # ====================================================
        # SEARCH RESULTS
        # ====================================================

        st.subheader("🔎 Search Results")

        search_results = state.get("search_results", "")

        if search_results:

            with st.expander("View Search Results", expanded=True):
                st.markdown(search_results)

        else:

            st.warning("No search results were returned.")


        # ====================================================
        # SCRAPED CONTENT
        # ====================================================

        st.subheader("📖 Detailed Research")

        scraped_content = state.get("scraped_content", "")

        if scraped_content:

            with st.expander("View Scraped Content", expanded=False):
                st.markdown(scraped_content)

        else:

            st.warning("No scraped content was returned.")


        # ====================================================
        # FINAL REPORT
        # ====================================================

        st.subheader("📝 Final Report")

        report = state.get("report", "")

        if report:

            st.markdown(report)

        else:

            st.warning("No report was generated.")


        # ====================================================
        # CRITIC FEEDBACK
        # ====================================================

        st.subheader("🧐 Critic Feedback")

        feedback = state.get("feedback", "")

        if feedback:

            with st.expander("View Critic Feedback", expanded=True):
                st.markdown(feedback)

        else:

            st.warning("No critic feedback was generated.")


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        st.error("❌ Something went wrong while running the pipeline.")

        st.exception(e)
import os
import pandas as pd
import streamlit as st

# PandasAI v3 API — requires: pip install pandasai pandasai-litellm
try:
    import pandasai as pai
    from pandasai_litellm.litellm import LiteLLM
    PANDASAI_AVAILABLE = True
except ImportError:
    PANDASAI_AVAILABLE = False

file = "tiktok_search_data.csv"
def app():
    # Inject shared dark theme
    from dashboard import _CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # Override label colours for this page
    st.markdown(
        """
        <style>
        /* File uploader label */
        [data-testid="stFileUploader"] label p,
        [data-testid="stFileUploader"] label span,
        [data-testid="stFileUploader"] label {
            color: #ffffff !important;
        }


        /* Text area label */
        [data-testid="stTextArea"] label p,
        [data-testid="stTextArea"] label span,
        [data-testid="stTextArea"] label {
            color: #ffffff !important;
        }

        /* Expander area label */
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary {
            color: #ffffff !important;
        }

        /* Text input label (API key field) */
        [data-testid="stTextInput"] label p,
        [data-testid="stTextInput"] label span,
        [data-testid="stTextInput"] label {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not PANDASAI_AVAILABLE:
        st.error(
            "PandasAI v3 is not installed. Run:  \n"
            "`pip install pandasai pandasai-litellm`"
        )
        return

    # ── API key ───────────────────────────────────────────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your key is never stored — it lives only in this session.",
        )
    if not api_key:
        st.info("Enter your OpenAI API key above to enable chat.")
        return

    # ── File upload ───────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        st.success(f"Loaded **{uploaded_file.name}** — {len(raw_df):,} rows × {len(raw_df.columns)} columns")
    else:
        from pathlib import Path
        fallback = Path(__file__).parent.parent / file
        if not fallback.exists():
            fallback = Path(__file__).parent / file
        raw_df = pd.read_csv(fallback)
        st.info("No file uploaded — using the demo dataset.")

    with st.expander("Preview data (last 5 rows)"):
        st.dataframe(raw_df.tail(5), use_container_width=True)

    st.markdown('<hr style="border-top:1px solid #2e3450;margin:16px 0">', unsafe_allow_html=True)

    # ── Chat input ────────────────────────────────────────────────────────────
    query = st.text_area(
        "Ask a question about your data",
        placeholder='e.g. "What is the best-seller product?"',
        height=90,
    )
    run_btn = st.button("Ask", type="primary")

    if run_btn and query.strip():
        with st.spinner("Thinking…"):
            try:
                llm = LiteLLM(model="gpt-4o-mini", api_key=api_key)
                pai.config.set({"llm": llm, "verbose": False})
                df_pai = pai.DataFrame(raw_df)
                result = df_pai.chat(query)

                st.markdown("#### Result")

                # v3 returns a string, DataFrame, or matplotlib Figure
                import matplotlib
                import matplotlib.figure
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, width='stretch')
                elif isinstance(result, matplotlib.figure.Figure):
                    st.pyplot(result)
                elif result is not None:
                    st.write(result)
                else:
                    st.info("No result returned — try rephrasing your question.")

            except Exception as e:
                st.error(f"Error: {e}")

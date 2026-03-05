import streamlit as st
from data import collect_data
from dashboard import analyse_data

#Ask for the user's id and analyse data
def app():
    # Render the main dashboard
    analyse_data()

    # Optional TikTok data collection section
    st.markdown('<hr style="border-top:1px solid #2e3450;margin:28px 0">', unsafe_allow_html=True)

    # Style the button inside the expander
    st.markdown(
        """
        <style>
        div[data-testid="stExpander"] .stButton > button {
            background-color: #0068C9 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.45rem 1.2rem;
            transition: background-color 0.2s;
        }
        div[data-testid="stExpander"] .stButton > button:hover {
            background-color: #0056a3 !important;
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] .stButton > button p {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔗 Collect TikTok Shop Data"):
        api_key = st.text_input("RapidAPI Key", type="password", placeholder="Paste your x-rapidapi-key here")
        keywords_input = st.text_area(
            "Enter product keywords (one per line)",
            placeholder="wireless earbuds\nbluetooth speaker\nphone case"
        )
        max_pages = st.slider("Pages per keyword (~30 products/page)", min_value=1, max_value=20, value=5)
        if st.button("Collect Data"):
            keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]
            if not api_key:
                st.error("Please enter your RapidAPI key.")
            elif keywords:
                with st.spinner(f"Collecting data for {len(keywords)} keyword(s)…"):
                    collect_data(keywords, api_key=api_key, max_pages=max_pages)
                st.success(f"Done! Data collected for: {', '.join(keywords)}")
                st.rerun()
            else:
                st.warning("Please enter at least one keyword.")

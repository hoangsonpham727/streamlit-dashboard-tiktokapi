import streamlit as st


def app():
    from dashboard import _CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="margin-bottom:28px">
            <p style="color:#8892a4;font-size:0.8rem;margin:0">Project info</p>
            <h1 style="color:#ffffff;font-size:1.75rem;font-weight:700;margin:2px 0 0 0">About</h1>
        </div>

        <div class="kpi-card" style="max-width:680px">
            <div class="section-title">Overview</div>
            <p style="color:#c9d1e0;font-size:0.95rem;line-height:1.7;margin:10px 0 0 0">
                This is my first project on data science and Streamlit. Although there are
                drawbacks in the program, I hope you enjoy it. I am open to any comments
                to improve the program and handle unexpected errors. Thanks!
            </p>
        </div>

        <div class="kpi-card" style="max-width:680px">
            <div class="section-title">Tech Stack</div>
            <ul style="color:#c9d1e0;font-size:0.9rem;line-height:2;margin:10px 0 0 0;padding-left:18px">
                <li><span style="color:#0068C9;font-weight:600">Streamlit</span> — interactive web app framework</li>
                <li><span style="color:#0068C9;font-weight:600">Plotly</span> — charts &amp; visualisations</li>
                <li><span style="color:#0068C9;font-weight:600">PandasAI v3</span> — natural-language data querying</li>
                <li><span style="color:#0068C9;font-weight:600">TikTok Shop API</span> — live product &amp; sales data</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

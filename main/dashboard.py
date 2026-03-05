from pathlib import Path
import plotly.express as px
import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

# ── Data path ─────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent
CSV_PATH = _ROOT / "tiktok_search_data.csv" # Name of the dataset 

def _load_data() -> pd.DataFrame:
    if not CSV_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH)
    df["price"]          = pd.to_numeric(df["price"],          errors="coerce")
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    df["sold"]           = pd.to_numeric(df["sold"],           errors="coerce").fillna(0).astype(int)
    df["rating"]         = pd.to_numeric(df["rating"],         errors="coerce")
    df["reviews"]        = pd.to_numeric(df["reviews"],        errors="coerce").fillna(0).astype(int)
    df["discount_pct"]   = (
        df["discount"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        
    )
    df["brand"]     = df["brand"].fillna("Unknown")
    df["shop_name"] = df["shop_name"].fillna("Unknown")
    return df

sales_data = _load_data()

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE    = "#0068C9"
ORANGE  = "#FF8700"
TEAL    = "#29B09D"
RED     = "#FF4B4B"
GREEN   = "#00C44F"
BG_PAGE = "#0e1117"
BG_CARD = "#1c2033"

# ── Global CSS ────────────────────────────────────────────────────────────────
_CSS = f"""
<style>
/* Page background */
.stApp {{
    background-color: {BG_PAGE};
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: #10131c;
}}

/* Sidebar text — all labels, markdown, selectbox, slider text */
[data-testid="stSidebar"] * {{
    color: #ffffff !important;
}}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMultiSelect span,
[data-testid="stSidebar"] .stSlider span,
[data-testid="stSidebar"] .stNumberInput label {{
    color: #ffffff !important;
}}

/* Collect Data button — white text */
div.stButton > button {{
    color: #ffffff !important;
    background-color: {BLUE};
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.45rem 1.2rem;
}}

div.stButton > button p,
div.stButton > button span {{
    color: #ffffff !important;
}}

div.stButton > button:hover {{
    background-color: #0057a8;
    color: #ffffff !important;
}}

/* Generic card wrapper */
.kpi-card {{
    background-color: {BG_CARD};
    border-radius: 12px;
    padding: 20px 22px 16px 22px;
    margin-bottom: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
}}

/* Section titles */
.section-title {{
    color: #c9d1e0;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

/* Big KPI number */
.kpi-value {{
    color: #ffffff;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0;
}}

/* Delta row */
.delta-positive {{
    color: {GREEN};
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 4px;
}}
.delta-negative {{
    color: {RED};
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 4px;
}}
.delta-neutral {{
    color: #8892a4;
    font-size: 0.82rem;
    margin-top: 4px;
}}

/* Sub-stat row (for two-value cards) */
.stat-row {{
    display: flex;
    gap: 40px;
    margin-top: 6px;
}}
.stat-block {{ }}
.stat-label {{
    color: #8892a4;
    font-size: 0.75rem;
    margin-bottom: 2px;
}}
.stat-num {{
    color: #ffffff;
    font-size: 1.55rem;
    font-weight: 700;
}}

/* Table inside card */
.deal-table {{
    width: 100%;
    border-collapse: collapse;
    color: #c9d1e0;
    font-size: 0.87rem;
}}
.deal-table th {{
    color: #8892a4;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 4px 8px 10px 8px;
    border-bottom: 1px solid #2e3450;
    text-align: left;
}}
.deal-table td {{
    padding: 7px 8px;
    border-bottom: 1px solid #1e2540;
}}
.deal-table tr:last-child td {{
    border-bottom: none;
}}
.deal-rank {{
    color: #8892a4;
    font-size: 0.8rem;
}}
.deal-value {{
    text-align: right;
    font-weight: 600;
    color: #ffffff;
}}

/* Styled divider */
.styled-divider {{
    border: none;
    border-top: 1px solid #2e3450;
    margin: 20px 0;
}}
</style>
"""


# ── Helper: KPI card ──────────────────────────────────────────────────────────
def _kpi_card(title: str, value: str, delta: float = 0.0, delta_label: str = "vs last year"):
    if delta is 0.0:
        delta_html = f'<div class="delta-neutral">&nbsp;</div>'
    elif delta > 0:
        delta_html = f'<div class="delta-positive">▲ {abs(delta):,.0f} {delta_label}</div>'
    else:
        delta_html = f'<div class="delta-negative">▼ {abs(delta):,.0f} {delta_label}</div>'

    st.markdown(
        f"""<div class="kpi-card">
            <div class="section-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )

# ── Helper: apply dark layout to a Plotly figure ─────────────────────────────
def _dark_layout(fig, height=260, title=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        height=height,
        margin=dict(l=14, r=14, t=40 if title else 18, b=14),
        font=dict(color="#c9d1e0", size=12),
        title=dict(text=title, font=dict(size=14, color="#c9d1e0"), x=0) if title else None,
        showlegend=False,
    )
    return fig


# ── plot_metric (kept for external callers, now dark-styled) ─────────────────
def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font": {"size": 28, "color": "#ffffff"},
            },
            title={
                "text": label,
                "font": {"size": 14, "color": "#c9d1e0"},
            },
        )
    )
    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={"color": color_graph},
            )
        )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        margin=dict(t=30, b=0),
        showlegend=False,
        height=110,
    )
    st.plotly_chart(fig, width='stretch')


# ── plot_gauge (dark-themed) ──────────────────────────────────────────────────
def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font": {"size": 26, "color": "#ffffff"},
            },
            gauge={
                "axis": {
                    "range": [0, max_bound],
                    "tickwidth": 1,
                    "tickcolor": "#8892a4",
                    "tickfont": {"color": "#8892a4"},
                },
                "bar": {"color": indicator_color},
                "bgcolor": "#2e3450",
                "bordercolor": BG_CARD,
                "steps": [
                    {"range": [0, max_bound * 0.5],  "color": "#1c2440"},
                    {"range": [max_bound * 0.5, max_bound], "color": "#1c2033"},
                ],
                "threshold": {
                    "line": {"color": "#ffffff", "width": 2},
                    "thickness": 0.75,
                    "value": indicator_number,
                },
            },
            title={
                "text": indicator_title,
                "font": {"size": 15, "color": "#c9d1e0"},
            },
        )
    )
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        height=220,
        margin=dict(l=16, r=16, t=50, b=10),
        font=dict(color="#c9d1e0"),
    )
    st.plotly_chart(fig, width='stretch')


# ── Main dashboard ────────────────────────────────────────────────────────────
def analyse_data():
    st.markdown(_CSS, unsafe_allow_html=True)

    df = _load_data()

    if df.empty:
        st.warning("No data found. Use the **Collect TikTok Shop Data** panel below to fetch products first.")
        return

    # ── Sidebar filters ────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Filters")
        keywords = sorted(df["search_query"].dropna().unique().tolist())
        sel_keywords = st.multiselect("Keywords", keywords, default=keywords)
        min_rating = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.1)
        min_sold   = st.number_input("Min Sold", min_value=0, value=0, step=100)

    fdf = df[
        df["search_query"].isin(sel_keywords) &
        (df["rating"].fillna(0) >= min_rating) &
        (df["sold"] >= min_sold)
    ]

    if fdf.empty:
        st.info("No products match the current filters.")
        return

    # ── Computed metrics ───────────────────────────────────────────────────────
    total_products  = len(fdf)
    total_sold      = int(fdf["sold"].sum())
    avg_rating      = round(fdf[fdf["rating"] > 0]["rating"].mean(), 2)
    avg_price       = round(fdf["price"].dropna().mean(), 2)
    avg_discount    = round(fdf[fdf["discount_pct"] > 0]["discount_pct"].mean(), 1)
    total_reviews   = int(fdf["reviews"].sum())

    top_shop      = fdf.groupby("shop_name")["sold"].sum().idxmax()
    top_shop_sold = int(fdf.groupby("shop_name")["sold"].sum().max())

    # ── Page header ────────────────────────────────────────────────────────────
    queries_label = ", ".join(sel_keywords[:3]) + ("…" if len(sel_keywords) > 3 else "")
    st.markdown(
        f"""<div style="margin-bottom:20px;">
            <p style="color:#8892a4;font-size:0.8rem;margin:0">
                TikTok Shop &nbsp;·&nbsp; {queries_label}
            </p>
            <h1 style="color:#ffffff;font-size:1.75rem;font-weight:700;margin:2px 0 0 0">
                Product Analytics Dashboard
            </h1>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── ROW 1 — KPI cards ─────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        _kpi_card("Total Products",   f"{total_products:,}")
    with c2:
        _kpi_card("Total Units Sold", f"{total_sold/1_000:.1f}K")
    with c3:
        _kpi_card("Avg Rating",       f"⭐ {avg_rating}")
    with c4:
        _kpi_card("Avg Price",        f"${avg_price:.2f}")
    with c5:
        _kpi_card("Avg Discount",     f"{avg_discount:.0f}%")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── ROW 2 — Top shops table | Top brands bar ───────────────────────────────
    col_shops, col_brands = st.columns([1.1, 1.5])

    with col_shops:
        top_shops = (
            fdf.groupby("shop_name")
            .agg(sold=("sold", "sum"), products=("product_id", "nunique"), rating=("rating", "mean"))
            .sort_values("sold", ascending=False)
            .head(8)
            .reset_index()
        )
        rows = ""
        for i, row in top_shops.iterrows():
            rows += (
                f"<tr><td class='deal-rank'>{i+1}</td>"
                f"<td>{row['shop_name']}</td>"
                f"<td class='deal-value'>{int(row['sold'])/1_000:.1f}K</td>"
                f"<td class='deal-value' style='color:{TEAL}'>{row['rating']:.1f} ⭐</td></tr>"
            )
        st.markdown(
            f"""<div class="kpi-card">
                <div class="section-title">Top Shops by Units Sold</div>
                <table class="deal-table">
                    <thead><tr>
                        <th>#</th><th>Shop</th>
                        <th style="text-align:right">Sold</th>
                        <th style="text-align:right">Rating</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>""",
            unsafe_allow_html=True,
        )

    with col_brands:
        top_brands = (
            fdf[fdf["brand"] != "Unknown"]
            .groupby("brand")["sold"]
            .sum()
            .nlargest(12)
            .reset_index()
        )
        fig_brands = px.bar(
            top_brands,
            x="sold", y="brand",
            orientation="h",
            color="sold",
            color_continuous_scale=["#1c3a6e", BLUE, TEAL],
            labels={"sold": "Units Sold", "brand": "Brand"},
        )
        fig_brands.update_traces(marker_line_width=0)
        fig_brands.update_coloraxes(showscale=False)
        fig_brands.update_layout(yaxis=dict(autorange="reversed"))
        _dark_layout(fig_brands, height=280, title="Top Brands by Units Sold")
        st.plotly_chart(fig_brands, width='stretch')

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── ROW 3 — Price distribution | Rating distribution ──────────────────────
    col_price, col_rating = st.columns(2)

    with col_price:
        price_data = fdf["price"].dropna()
        fig_price = px.histogram(
            price_data,
            nbins=30,
            color_discrete_sequence=[BLUE],
            labels={"value": "Price ($)", "count": "# Products"},
        )
        fig_price.update_traces(marker_line_width=0)
        _dark_layout(fig_price, height=240, title="Price Distribution")
        fig_price.update_xaxes(title="Price ($)")
        fig_price.update_yaxes(title="# Products")
        st.plotly_chart(fig_price, width='stretch')

    with col_rating:
        rating_data = fdf[fdf["rating"] > 0]["rating"]
        fig_rating = px.histogram(
            rating_data,
            nbins=20,
            color_discrete_sequence=[TEAL],
            labels={"value": "Rating", "count": "# Products"},
        )
        fig_rating.update_traces(marker_line_width=0)
        _dark_layout(fig_rating, height=240, title="Rating Distribution")
        fig_rating.update_xaxes(title="Rating")
        fig_rating.update_yaxes(title="# Products")
        st.plotly_chart(fig_rating, width='stretch')

    # ── ROW 4 — Sold vs Price scatter | Discount leaderboard ──────────────────
    col_scatter, col_disc = st.columns([1.5, 1])

    with col_scatter:
        scatter_df = fdf[fdf["sold"] > 0].dropna(subset=["price", "rating"])
        fig_scatter = px.scatter(
            scatter_df,
            x="price",
            y="sold",
            color="rating",
            color_continuous_scale=["#FF4B4B", ORANGE, GREEN],
            hover_data=["title", "shop_name", "discount_pct"],
            labels={"price": "Price ($)", "sold": "Units Sold", "rating": "Rating"},
            size_max=12,
        )
        fig_scatter.update_traces(marker=dict(size=7, opacity=0.75))
        _dark_layout(fig_scatter, height=300, title="Price vs Units Sold (coloured by Rating)")
        fig_scatter.update_coloraxes(colorbar=dict(
            title="Rating",
            tickfont=dict(color="#c9d1e0"),
            
        ))
        st.plotly_chart(fig_scatter, width='stretch')

    with col_disc:
        top_disc = (
            fdf[fdf["discount_pct"] > 0]
            .nlargest(8, "discount_pct")[["title", "shop_name", "discount_pct", "price"]]
            .reset_index(drop=True)
        )
        disc_rows = ""
        for i, row in top_disc.iterrows():
            short_title = (row["title"][:40] + "…") if len(str(row["title"])) > 40 else row["title"]
            disc_rows += (
                f"<tr><td class='deal-rank'>{i+1}</td>"
                f"<td>{short_title}</td>"
                f"<td class='deal-value' style='color:{ORANGE}'>{int(row['discount_pct'])}%</td>"
                f"<td class='deal-value'>${row['price']:.2f}</td></tr>"
            )
        st.markdown(
            f"""<div class="kpi-card">
                <div class="section-title">Biggest Discounts</div>
                <table class="deal-table">
                    <thead><tr>
                        <th>#</th><th>Product</th>
                        <th style="text-align:right">Discount</th>
                        <th style="text-align:right">Price</th>
                    </tr></thead>
                    <tbody>{disc_rows}</tbody>
                </table>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── ROW 5 — Sales by keyword | Top products table ─────────────────────────
    col_kw, col_top = st.columns([1, 1.4])

    with col_kw:
        kw_summary = (
            fdf.groupby("search_query")
            .agg(sold=("sold", "sum"), products=("product_id", "nunique"))
            .reset_index()
            .sort_values("sold", ascending=False)
        )
        fig_kw = px.bar(
            kw_summary,
            x="search_query", y="sold",
            color="products",
            color_continuous_scale=["#1c3a6e", BLUE],
            labels={"search_query": "Keyword", "sold": "Total Sold", "products": "# Products"},
        )
        fig_kw.update_traces(marker_line_width=0)
        fig_kw.update_coloraxes(showscale=False)
        _dark_layout(fig_kw, height=260, title="Total Sold by Search Keyword")
        fig_kw.update_xaxes(tickangle=-20)
        st.plotly_chart(fig_kw, width='stretch')

    with col_top:
        top_products = (
            fdf.nlargest(8, "sold")[["title", "brand", "sold", "price", "rating"]]
            .reset_index(drop=True)
        )
        prod_rows = ""
        for i, row in top_products.iterrows():
            short = (str(row["title"])[:38] + "…") if len(str(row["title"])) > 38 else str(row["title"])
            prod_rows += (
                f"<tr><td class='deal-rank'>{i+1}</td>"
                f"<td>{short}</td>"
                f"<td class='deal-value'>{int(row['sold'])/1_000:.1f}K</td>"
                f"<td class='deal-value' style='color:{TEAL}'>${row['price']:.2f}</td>"
                f"<td class='deal-value' style='color:{ORANGE}'>{row['rating']:.1f}⭐</td></tr>"
            )
        st.markdown(
            f"""<div class="kpi-card">
                <div class="section-title">Top Products by Units Sold</div>
                <table class="deal-table">
                    <thead><tr>
                        <th>#</th><th>Product</th>
                        <th style="text-align:right">Sold</th>
                        <th style="text-align:right">Price</th>
                        <th style="text-align:right">Rating</th>
                    </tr></thead>
                    <tbody>{prod_rows}</tbody>
                </table>
            </div>""",
            unsafe_allow_html=True,
        )

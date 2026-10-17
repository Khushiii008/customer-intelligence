
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Customer Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B1020;
        color: #F3F4F6;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #151D30;
        border: 1px solid #29344D;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #A5B4FC;
    }

    [data-testid="stMetricValue"] {
        color: #F9FAFB;
    }

    h1, h2, h3 {
        color: #C4B5FD;
    }

    div[data-testid="stDownloadButton"] button {
        background-color: #7C3AED;
        color: white;
        border-radius: 8px;
        border: none;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #6D28D9;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Consistent colours for customer segments
SEGMENT_COLORS = {
    "Regular Customers": "#8B5CF6",
    "At-Risk Customers": "#F59E0B",
    "High Value": "#22D3EE",
    "High-Value, Mixed Activity": "#22D3EE",
    "Exceptional High Spenders": "#F472B6",
}

# --------------------------------------------------
# 3. LOAD AND VALIDATE DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("customer_segments.csv")

    required_columns = [
        "CustomerID",
        "Recency",
        "Frequency",
        "Monetary",
        "Cluster",
        "Segment",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = data[required_columns].copy()

    data["CustomerID"] = data["CustomerID"].astype(str)

    for col in ["Recency", "Frequency", "Monetary", "Cluster"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(
        subset=["Recency", "Frequency", "Monetary", "Cluster", "Segment"]
    )

    data["Segment"] = data["Segment"].astype(str)

    return data


try:
    customer_data = load_data()
except Exception as error:
    st.error(f"Unable to load customer data: {error}")
    st.info(
        "Ensure customer_segments.csv is in the same folder as app.py."
    )
    st.stop()

if customer_data.empty:
    st.error("The dataset contains no usable customer records.")
    st.stop()

# --------------------------------------------------
# 4. HEADER
# --------------------------------------------------

st.title("Customer Intelligence Dashboard")

st.markdown(
    """
    Explore customer purchasing behaviour, identify customer segments,
    and understand differences in recency, frequency and spending.
    """
)

st.caption(
    "Dataset: Online Retail | Method: K-Means clustering | "
    "Currency: GBP (£)"
)

# --------------------------------------------------
# 5. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("Filter customers to explore specific groups.")

available_segments = sorted(
    customer_data["Segment"].unique().tolist()
)

selected_segments = st.sidebar.multiselect(
    "Customer segments",
    options=available_segments,
    default=available_segments,
)

min_recency = int(customer_data["Recency"].min())
max_recency = int(customer_data["Recency"].max())

if min_recency < max_recency:
    selected_recency = st.sidebar.slider(
        "Days since last purchase",
        min_value=min_recency,
        max_value=max_recency,
        value=(min_recency, max_recency),
    )
else:
    selected_recency = (min_recency, max_recency)
    st.sidebar.caption(f"All customers have recency of {min_recency} days.")

# Apply the filters to the customer dataset
filtered_data = customer_data[
    customer_data["Segment"].isin(selected_segments)
    & customer_data["Recency"].between(
        selected_recency[0],
        selected_recency[1],
    )
].copy()

st.sidebar.divider()
st.sidebar.caption(
    f"{len(filtered_data):,} of {len(customer_data):,} customers displayed"
)

if filtered_data.empty:
    st.warning(
        "No customers match these filters. Select more segments "
        "or widen the recency range."
    )
    st.stop()

# --------------------------------------------------
# 6. KPI CARDS
# --------------------------------------------------

st.subheader("Business Overview")

total_customers = len(filtered_data)
total_revenue = filtered_data["Monetary"].sum()
average_spend = filtered_data["Monetary"].mean()
total_segments = filtered_data["Segment"].nunique()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Customers",
    f"{total_customers:,}",
)

kpi2.metric(
    "Total Revenue",
    f"£{total_revenue:,.2f}",
)

kpi3.metric(
    "Average Customer Spend",
    f"£{average_spend:,.2f}",
)

kpi4.metric(
    "Segments Displayed",
    f"{total_segments}",
)

st.caption(
    "KPIs reflect the customers currently selected in the sidebar."
)

st.divider()

# --------------------------------------------------
# 7. CUSTOMER SEGMENT DISTRIBUTION
# --------------------------------------------------

st.subheader("Customer Segment Distribution")

segment_counts = (
    filtered_data["Segment"]
    .value_counts()
    .rename_axis("Segment")
    .reset_index(name="Customers")
)

segment_counts["Percentage"] = (
    segment_counts["Customers"] / len(filtered_data) * 100
)

col1, col2 = st.columns([1.4, 1])

with col1:
    fig_distribution = px.bar(
        segment_counts,
        x="Segment",
        y="Customers",
        color="Segment",
        color_discrete_map=SEGMENT_COLORS,
        text="Customers",
        title="Number of Customers in Each Segment",
        hover_data={"Percentage": ":.1f"},
    )

    fig_distribution.update_traces(
        textposition="outside",
        cliponaxis=False,
    )

    fig_distribution.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1020",
        plot_bgcolor="#111827",
        showlegend=False,
        xaxis_title="Customer Segment",
        yaxis_title="Number of Customers",
        margin=dict(t=65, b=80),
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True,
    )

with col2:
    st.markdown("#### Segment Summary")

    summary = (
        filtered_data.groupby("Segment")
        .agg(
            Customers=("CustomerID", "count"),
            MedianSpend=("Monetary", "median"),
            MedianFrequency=("Frequency", "median"),
            MedianRecency=("Recency", "median"),
        )
        .reset_index()
    )

    summary["Share (%)"] = (
        summary["Customers"] / len(filtered_data) * 100
    ).round(1)

    summary["Median Spend (£)"] = summary["MedianSpend"].map(
        lambda x: f"£{x:,.2f}"
    )

    summary = summary.rename(
        columns={
            "MedianFrequency": "Median Invoices",
            "MedianRecency": "Median Recency (days)",
        }
    )

    st.dataframe(
        summary[
            [
                "Segment",
                "Customers",
                "Share (%)",
                "Median Spend (£)",
                "Median Invoices",
                "Median Recency (days)",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

st.caption(
    "Median values describe the typical customer in each segment "
    "and are less affected by extreme spending values than averages."
)

st.divider()

# --------------------------------------------------
# 8. CUSTOMER BEHAVIOUR: SCATTER PLOT
# --------------------------------------------------

st.subheader("Customer Behaviour")

st.markdown(
    """
    Each dot represents a customer. Colours identify their assigned
    segment. Hover over a dot to inspect the customer and their spending.
    """
)

fig_scatter = px.scatter(
    filtered_data,
    x="Recency",
    y="Frequency",
    color="Segment",
    color_discrete_map=SEGMENT_COLORS,
    hover_data={
        "CustomerID": True,
        "Monetary": ":.2f",
        "Recency": True,
        "Frequency": True,
    },
    title="Recency vs Purchase Frequency",
    labels={
        "Recency": "Days Since Last Purchase",
        "Frequency": "Number of Invoices",
        "Segment": "Customer Segment",
        "Monetary": "Total Spend (£)",
    },
    opacity=0.65,
    log_y=True,
)

fig_scatter.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0B1020",
    plot_bgcolor="#111827",
    legend_title_text="Customer Segment",
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True,
)

st.caption(
    "Lower recency means a more recent purchase; higher frequency "
    "means more repeat purchases. The logarithmic vertical axis "
    "makes customers with different purchase frequencies easier to compare."
)

st.divider()

# --------------------------------------------------
# 9. CUSTOMER SPENDING DISTRIBUTION
# --------------------------------------------------

st.subheader("Customer Spending Distribution")

st.markdown(
    """
    This histogram shows how customer spending is distributed.
    The transformation helps make both ordinary and unusually high
    spending values easier to examine.
    """
)

# log1p(x) = log(1 + x). Unlike log(x), it supports zero.
# This column is used for visualisation only; it does not change K-Means.
hist_data = filtered_data.copy()
hist_data["LogSpend"] = np.log1p(
    hist_data["Monetary"].clip(lower=0)
)

fig_hist = px.histogram(
    hist_data,
    x="LogSpend",
    color="Segment",
    color_discrete_map=SEGMENT_COLORS,
    nbins=40,
    opacity=0.7,
    title="Distribution of Customer Spend",
    labels={
        "LogSpend": "Log(1 + Customer Spend in £)",
        "count": "Number of Customers",
        "Segment": "Customer Segment",
    },
)

fig_hist.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0B1020",
    plot_bgcolor="#111827",
    barmode="overlay",
    legend_title_text="Customer Segment",
)

st.plotly_chart(
    fig_hist,
    use_container_width=True,
)

st.caption(
    "Each bar represents the number of customers within a spending range. "
    "The horizontal axis is transformed, so it is not a direct pound scale."
)

st.divider()

# --------------------------------------------------
# 10. SPENDING COMPARISON: BOX PLOT
# --------------------------------------------------

st.subheader("Spending Variation Across Segments")

st.markdown(
    """
    Compare the spread of spending within each segment.
    This chart uses a transformed spending axis to accommodate
    the highly skewed retail data, including zero spending.
    """
)

box_data = filtered_data.copy()
box_data["LogSpend"] = np.log1p(
    box_data["Monetary"].clip(lower=0)
)

fig_box = px.box(
    box_data,
    x="Segment",
    y="LogSpend",
    color="Segment",
    color_discrete_map=SEGMENT_COLORS,
    points=False,
    title="Customer Spending by Segment",
    labels={
        "Segment": "Customer Segment",
        "LogSpend": "Log(1 + Customer Spend in £)",
    },
)

fig_box.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0B1020",
    plot_bgcolor="#111827",
    showlegend=False,
    xaxis_title="Customer Segment",
    yaxis_title="Log(1 + Customer Spend in £)",
)

st.plotly_chart(
    fig_box,
    use_container_width=True,
)

st.caption(
    "The box shows the middle 50% of spending values; the line inside "
    "is the median. The vertical axis is transformed, not raw pounds."
)

st.divider()

# --------------------------------------------------
# 11. CUSTOMER EXPLORER
# --------------------------------------------------

st.subheader("Customer Explorer")

st.markdown(
    "Search for an individual customer or inspect customers matching "
    "your current sidebar filters."
)

search_id = st.text_input(
    "Search Customer ID",
    placeholder="Enter a customer ID...",
)

explorer_data = filtered_data.copy()

if search_id.strip():
    explorer_data = explorer_data[
        explorer_data["CustomerID"].str.contains(
            search_id.strip(),
            case=False,
            na=False,
        )
    ]

display_data = explorer_data[
    [
        "CustomerID",
        "Segment",
        "Recency",
        "Frequency",
        "Monetary",
        "Cluster",
    ]
].copy()

display_data = display_data.rename(
    columns={
        "CustomerID": "Customer ID",
        "Recency": "Days Since Last Purchase",
        "Frequency": "Number of Invoices",
        "Monetary": "Total Spend (£)",
        "Cluster": "Cluster ID",
    }
)

st.caption(f"{len(display_data):,} matching customer records")

st.dataframe(
    display_data,
    hide_index=True,
    use_container_width=True,
)

csv_data = display_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Customer Data (CSV)",
    data=csv_data,
    file_name="customer_intelligence_export.csv",
    mime="text/csv",
)

# --------------------------------------------------
# 12. METHODOLOGY
# --------------------------------------------------

with st.expander("How this dashboard works"):
    st.markdown(
        """
        **Data preparation**
        - Customer records were cleaned before modelling.
        - Cancelled invoices were excluded from the sales data.
        - Monetary value was calculated from quantity multiplied by unit price.
        - Customer-level Recency, Frequency and Monetary features were created.

        **Clustering**
        - K-Means was applied to scaled Recency, Frequency and Monetary features.
        - The selected model uses four clusters.
        - Customer IDs and segment names are used for display, not as model features.

        **Visualisation**
        - Logarithmic transformations are used in selected charts to improve readability.
        - These plotting transformations do not change the saved model assignments.
        - Sidebar filters update the KPIs, charts, summary and customer explorer.
        """
    )

st.caption(
    "Customer Intelligence | Built with Python, Pandas, Plotly and Streamlit"
)


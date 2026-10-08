"""
AtmoSync - Interactive Microclimate Analytics Dashboard

Features
--------
- Interactive sidebar filters
- Responsive KPI dashboard
- Automatic environmental insights
- Intraday temperature analysis
- Humidity and solar-radiation trends
- LULC comparison
- Location ranking
- NDVI-temperature relationship
- Correlation analysis
- Temperature anomaly detection
- Microclimate environmental score
- Interactive spatial map
- Filtered-data explorer
- CSV download
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AtmoSync | Microclimate Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "microclimate_cleaned.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["cdTimestamp"]
    )

    return df


try:

    df = load_data()

except Exception as error:

    st.error(
        "Unable to load the processed dataset."
    )

    st.code(str(error))

    st.stop()


# ============================================================
# DATA VALIDATION
# ============================================================

if df.empty:

    st.error("The dataset is empty.")

    st.stop()


required_columns = [
    "cdTimestamp",
    "Location_ID",
    "Latitude",
    "Longitude",
    "LULC_Type",
    "Temperature",
    "Humidity",
    "Wind_Speed",
    "Solar_Radiation",
    "Precipitation",
    "Air_Pressure",
    "NDVI",
    "Time_Period"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "Required columns are missing from the dataset:"
    )

    st.write(missing_columns)

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("🌍 AtmoSync")

st.caption(
    "Interactive Microclimate Analytics & Environmental Intelligence"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 AtmoSync")

st.sidebar.caption(
    "Dashboard Controls"
)

st.sidebar.divider()


# ============================================================
# LOCATION FILTER
# ============================================================

all_locations = sorted(
    df["Location_ID"]
    .dropna()
    .unique()
)


selected_locations = st.sidebar.multiselect(
    "📍 Locations",
    options=all_locations,
    default=all_locations
)


# ============================================================
# LULC FILTER
# ============================================================

all_lulc = sorted(
    df["LULC_Type"]
    .dropna()
    .unique()
)


selected_lulc = st.sidebar.multiselect(
    "🌱 LULC Type",
    options=all_lulc,
    default=all_lulc
)


# ============================================================
# TIME PERIOD FILTER
# ============================================================

all_periods = sorted(
    df["Time_Period"]
    .dropna()
    .unique()
)


selected_periods = st.sidebar.multiselect(
    "🕐 Time Period",
    options=all_periods,
    default=all_periods
)


# ============================================================
# TEMPERATURE FILTER
# ============================================================

temperature_min = float(
    df["Temperature"].min()
)

temperature_max = float(
    df["Temperature"].max()
)


selected_temperature = st.sidebar.slider(
    "🌡 Temperature Range",
    min_value=temperature_min,
    max_value=temperature_max,
    value=(
        temperature_min,
        temperature_max
    ),
    step=0.5
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["Location_ID"].isin(selected_locations)
    &
    df["LULC_Type"].isin(selected_lulc)
    &
    df["Time_Period"].isin(selected_periods)
    &
    df["Temperature"].between(
        selected_temperature[0],
        selected_temperature[1]
    )
].copy()


# ============================================================
# EMPTY RESULT
# ============================================================

if filtered_df.empty:

    st.warning(
        "No observations match the selected filters."
    )

    st.stop()


# ============================================================
# SIDEBAR SUMMARY
# ============================================================

st.sidebar.divider()

st.sidebar.metric(
    "Observations",
    f"{len(filtered_df):,}"
)

st.sidebar.metric(
    "Locations",
    filtered_df["Location_ID"].nunique()
)

st.sidebar.metric(
    "LULC Categories",
    filtered_df["LULC_Type"].nunique()
)


# ============================================================
# DASHBOARD TABS
# ============================================================

tabs = st.tabs(
    [
        "Overview",
        "Trends",
        "LULC Analysis",
        "Locations",
        "Relationships",
        "Anomalies",
        "Spatial",
        "Data"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tabs[0]:

    st.header("Environmental Overview")

    st.caption(
        "Key environmental indicators for the current filter selection."
    )


    # --------------------------------------------------------
    # KPI calculations
    # --------------------------------------------------------

    avg_temperature = filtered_df[
        "Temperature"
    ].mean()

    max_temperature = filtered_df[
        "Temperature"
    ].max()

    min_temperature = filtered_df[
        "Temperature"
    ].min()

    avg_humidity = filtered_df[
        "Humidity"
    ].mean()

    avg_ndvi = filtered_df[
        "NDVI"
    ].mean()

    avg_wind = filtered_df[
        "Wind_Speed"
    ].mean()

    avg_solar = filtered_df[
        "Solar_Radiation"
    ].mean()


    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    kpi_columns = st.columns(7)


    kpis = [
        (
            "Average Temperature",
            f"{avg_temperature:.2f} °C"
        ),

        (
            "Maximum Temperature",
            f"{max_temperature:.2f} °C"
        ),

        (
            "Minimum Temperature",
            f"{min_temperature:.2f} °C"
        ),

        (
            "Average Humidity",
            f"{avg_humidity:.2f} %"
        ),

        (
            "Average NDVI",
            f"{avg_ndvi:.2f}"
        ),

        (
            "Average Wind",
            f"{avg_wind:.2f}"
        ),

        (
            "Solar Radiation",
            f"{avg_solar:.2f}"
        )
    ]


    for column, (title, value) in zip(
        kpi_columns,
        kpis
    ):

        with column:

            st.metric(
                label=title,
                value=value
            )


    st.divider()


    # ========================================================
    # AUTOMATIC INSIGHTS
    # ========================================================

    st.subheader("Key Insights")


    hottest_row = filtered_df.loc[
        filtered_df["Temperature"].idxmax()
    ]


    coolest_row = filtered_df.loc[
        filtered_df["Temperature"].idxmin()
    ]


    hottest_station = hottest_row[
        "Location_ID"
    ]

    hottest_value = hottest_row[
        "Temperature"
    ]

    hottest_time = hottest_row[
        "cdTimestamp"
    ].strftime("%H:%M")


    coolest_station = coolest_row[
        "Location_ID"
    ]

    coolest_value = coolest_row[
        "Temperature"
    ]


    lulc_temperature = (
        filtered_df
        .groupby("LULC_Type")["Temperature"]
        .mean()
    )


    warmest_lulc = (
        lulc_temperature.idxmax()
    )

    coolest_lulc = (
        lulc_temperature.idxmin()
    )


    anomaly_count = (
        filtered_df["Temperature"] <= -5
    ).sum()


    insight_columns = st.columns(3)


    insights = [

        (
            "🔥 Peak Temperature",
            (
                f"{hottest_value:.2f}°C was recorded "
                f"at {hottest_station} around "
                f"{hottest_time}."
            )
        ),

        (
            "❄️ Lowest Temperature",
            (
                f"{coolest_value:.2f}°C was recorded "
                f"at {coolest_station}."
            )
        ),

        (
            "🌱 LULC Comparison",
            (
                f"{warmest_lulc} has the highest "
                f"average temperature, while "
                f"{coolest_lulc} has the lowest."
            )
        ),

        (
            "⚠️ Potential Extreme Values",
            (
                f"{anomaly_count:,} observations "
                f"are at or below −5°C."
            )
        ),

        (
            "📍 Spatial Coverage",
            (
                f"{filtered_df['Location_ID'].nunique()} "
                f"monitoring locations are represented."
            )
        ),

        (
            "🌿 Vegetation",
            (
                f"Average NDVI is "
                f"{avg_ndvi:.2f}."
            )
        )
    ]


    for index, (title, text) in enumerate(
        insights
    ):

        with insight_columns[
            index % 3
        ]:

            st.info(
                f"**{title}**\n\n{text}"
            )


    st.divider()


    # ========================================================
    # ENVIRONMENTAL SCORE
    # ========================================================

    st.subheader(
        "Microclimate Environmental Score"
    )


    def normalize_inverse(
        series
    ):

        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:

            return pd.Series(
                1.0,
                index=series.index
            )

        return (
            1
            - (
                (series - minimum)
                / (maximum - minimum)
            )
        )


    temperature_score = normalize_inverse(
        filtered_df["Temperature"]
    )

    humidity_score = normalize_inverse(
        abs(
            filtered_df["Humidity"] - 60
        )
    )

    ndvi_score = (
        filtered_df["NDVI"]
        .clip(-1, 1)
        + 1
    ) / 2


    environmental_score = (
        (
            temperature_score * 0.40
            +
            humidity_score * 0.25
            +
            ndvi_score * 0.35
        )
        * 100
    )


    average_environmental_score = (
        environmental_score.mean()
    )


    score_col1, score_col2 = st.columns(2)


    with score_col1:

        st.metric(
            "Environmental Score",
            f"{average_environmental_score:.1f}/100"
        )


    with score_col2:

        if average_environmental_score >= 75:

            score_label = "Favorable"

        elif average_environmental_score >= 50:

            score_label = "Moderate"

        else:

            score_label = "Needs Attention"


        st.metric(
            "Condition",
            score_label
        )


    st.caption(
        "The score is a project-specific analytical index, "
        "not an official environmental or health standard."
    )


# ============================================================
# TAB 2 — TRENDS
# ============================================================

with tabs[1]:

    st.header("Microclimate Trends")

    st.caption(
        "Intraday environmental patterns based on the selected observations."
    )


    # --------------------------------------------------------
    # Hourly aggregation
    # --------------------------------------------------------

    hourly = (
        filtered_df
        .assign(
            Hour_Number=filtered_df[
                "cdTimestamp"
            ].dt.hour
        )
        .groupby("Hour_Number")
        .agg(
            Temperature=(
                "Temperature",
                "mean"
            ),

            Humidity=(
                "Humidity",
                "mean"
            ),

            Wind_Speed=(
                "Wind_Speed",
                "mean"
            ),

            Solar_Radiation=(
                "Solar_Radiation",
                "mean"
            )
        )
        .reset_index()
        .sort_values("Hour_Number")
    )


    # --------------------------------------------------------
    # Metric selector
    # --------------------------------------------------------

    selected_trend = st.selectbox(
        "Select environmental variable",
        [
            "Temperature",
            "Humidity",
            "Wind_Speed",
            "Solar_Radiation"
        ]
    )


    trend_titles = {

        "Temperature":
            "Average Temperature by Hour",

        "Humidity":
            "Average Humidity by Hour",

        "Wind_Speed":
            "Average Wind Speed by Hour",

        "Solar_Radiation":
            "Average Solar Radiation by Hour"
    }


    y_labels = {

        "Temperature":
            "Temperature (°C)",

        "Humidity":
            "Humidity (%)",

        "Wind_Speed":
            "Wind Speed",

        "Solar_Radiation":
            "Solar Radiation"
    }


    fig_trend = px.line(
        hourly,
        x="Hour_Number",
        y=selected_trend,
        markers=True,
        title=trend_titles[
            selected_trend
        ]
    )


    fig_trend.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title=y_labels[
            selected_trend
        ],
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Multi-variable trends
    # --------------------------------------------------------

    st.subheader(
        "Temperature and Humidity"
    )


    trend_col1, trend_col2 = st.columns(2)


    with trend_col1:

        fig_temp = px.line(
            hourly,
            x="Hour_Number",
            y="Temperature",
            markers=True,
            title="Temperature"
        )

        fig_temp.update_layout(
            xaxis_title="Hour",
            yaxis_title="Temperature (°C)"
        )

        st.plotly_chart(
            fig_temp,
            use_container_width=True
        )


    with trend_col2:

        fig_humidity = px.line(
            hourly,
            x="Hour_Number",
            y="Humidity",
            markers=True,
            title="Humidity"
        )

        fig_humidity.update_layout(
            xaxis_title="Hour",
            yaxis_title="Humidity (%)"
        )

        st.plotly_chart(
            fig_humidity,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Solar radiation
    # --------------------------------------------------------

    fig_solar = px.area(
        hourly,
        x="Hour_Number",
        y="Solar_Radiation",
        title="Solar Radiation by Hour"
    )


    fig_solar.update_layout(
        xaxis_title="Hour",
        yaxis_title="Solar Radiation"
    )


    st.plotly_chart(
        fig_solar,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Temperature vs Humidity
    # --------------------------------------------------------

    st.subheader(
        "Temperature vs Humidity"
    )


    fig_temp_humidity = px.scatter(
        filtered_df,
        x="Temperature",
        y="Humidity",
        color="LULC_Type",
        hover_data=[
            "Location_ID",
            "cdTimestamp"
        ],
        opacity=0.65
    )


    fig_temp_humidity.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="Humidity (%)"
    )


    st.plotly_chart(
        fig_temp_humidity,
        use_container_width=True
    )


# ============================================================
# TAB 3 — LULC ANALYSIS
# ============================================================

with tabs[2]:

    st.header(
        "Land Use / Land Cover Analysis"
    )


    lulc_summary_dashboard = (
        filtered_df
        .groupby("LULC_Type")
        .agg(

            Average_Temperature=(
                "Temperature",
                "mean"
            ),

            Average_Humidity=(
                "Humidity",
                "mean"
            ),

            Average_Wind_Speed=(
                "Wind_Speed",
                "mean"
            ),

            Average_Solar_Radiation=(
                "Solar_Radiation",
                "mean"
            ),

            Average_NDVI=(
                "NDVI",
                "mean"
            )
        )
        .round(2)
        .reset_index()
    )


    # --------------------------------------------------------
    # Metric selector
    # --------------------------------------------------------

    lulc_metric = st.selectbox(
        "Select LULC metric",
        [
            "Average_Temperature",
            "Average_Humidity",
            "Average_Wind_Speed",
            "Average_Solar_Radiation",
            "Average_NDVI"
        ]
    )


    lulc_labels = {

        "Average_Temperature":
            "Average Temperature",

        "Average_Humidity":
            "Average Humidity",

        "Average_Wind_Speed":
            "Average Wind Speed",

        "Average_Solar_Radiation":
            "Average Solar Radiation",

        "Average_NDVI":
            "Average NDVI"
    }


    fig_lulc = px.bar(
        lulc_summary_dashboard,
        x="LULC_Type",
        y=lulc_metric,
        color="LULC_Type",
        text_auto=".2f",
        title=(
            f"{lulc_labels[lulc_metric]} "
            "by LULC Type"
        )
    )


    fig_lulc.update_layout(
        xaxis_title="LULC Type",
        yaxis_title=lulc_labels[
            lulc_metric
        ],
        showlegend=False
    )


    st.plotly_chart(
        fig_lulc,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Comparison charts
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig_temp_lulc = px.bar(
            lulc_summary_dashboard,
            x="LULC_Type",
            y="Average_Temperature",
            text_auto=".2f",
            title="Temperature by LULC"
        )

        fig_temp_lulc.update_layout(
            yaxis_title="Temperature (°C)"
        )

        st.plotly_chart(
            fig_temp_lulc,
            use_container_width=True
        )


    with col2:

        fig_ndvi_lulc = px.bar(
            lulc_summary_dashboard,
            x="LULC_Type",
            y="Average_NDVI",
            text_auto=".2f",
            title="NDVI by LULC"
        )

        fig_ndvi_lulc.update_layout(
            yaxis_title="NDVI"
        )

        st.plotly_chart(
            fig_ndvi_lulc,
            use_container_width=True
        )


    st.subheader(
        "LULC Environmental Summary"
    )


    st.dataframe(
        lulc_summary_dashboard,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4 — LOCATION ANALYSIS
# ============================================================

with tabs[3]:

    st.header(
        "Location-Level Analysis"
    )


    location_summary_dashboard = (
        filtered_df
        .groupby("Location_ID")
        .agg(

            Average_Temperature=(
                "Temperature",
                "mean"
            ),

            Maximum_Temperature=(
                "Temperature",
                "max"
            ),

            Minimum_Temperature=(
                "Temperature",
                "min"
            ),

            Average_Humidity=(
                "Humidity",
                "mean"
            ),

            Average_Wind_Speed=(
                "Wind_Speed",
                "mean"
            ),

            Average_Solar_Radiation=(
                "Solar_Radiation",
                "mean"
            ),

            Average_NDVI=(
                "NDVI",
                "mean"
            )
        )
        .round(2)
        .reset_index()
    )


    # --------------------------------------------------------
    # Location metric
    # --------------------------------------------------------

    location_metric = st.selectbox(
        "Rank locations by",
        [
            "Average_Temperature",
            "Maximum_Temperature",
            "Average_Humidity",
            "Average_Wind_Speed",
            "Average_Solar_Radiation",
            "Average_NDVI"
        ]
    )


    ascending = st.radio(
        "Ranking direction",
        [
            "Highest first",
            "Lowest first"
        ],
        horizontal=True
    )


    location_ranking = (
        location_summary_dashboard
        .sort_values(
            location_metric,
            ascending=(
                ascending == "Lowest first"
            )
        )
        .head(10)
    )


    fig_location = px.bar(
        location_ranking,
        x=location_metric,
        y="Location_ID",
        orientation="h",
        text_auto=".2f",
        title=(
            f"Top Locations by "
            f"{location_metric.replace('_', ' ')}"
        )
    )


    fig_location.update_layout(
        yaxis_title="Location",
        xaxis_title=location_metric.replace(
            "_",
            " "
        )
    )


    st.plotly_chart(
        fig_location,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Hottest and coolest locations
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    hottest_locations = (
        location_summary_dashboard
        .sort_values(
            "Average_Temperature",
            ascending=False
        )
        .head(10)
    )


    coolest_locations = (
        location_summary_dashboard
        .sort_values(
            "Average_Temperature",
            ascending=True
        )
        .head(10)
    )


    with col1:

        st.subheader(
            "🔥 Warmest Locations"
        )

        st.dataframe(
            hottest_locations,
            use_container_width=True,
            hide_index=True
        )


    with col2:

        st.subheader(
            "❄️ Coolest Locations"
        )

        st.dataframe(
            coolest_locations,
            use_container_width=True,
            hide_index=True
        )


    st.subheader(
        "Complete Location Ranking"
    )


    st.dataframe(
        location_summary_dashboard
        .sort_values(
            "Average_Temperature",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5 — RELATIONSHIPS
# ============================================================

with tabs[4]:

    st.header(
        "Environmental Relationships"
    )


    # --------------------------------------------------------
    # Scatter controls
    # --------------------------------------------------------

    relationship_col1, relationship_col2 = (
        st.columns(2)
    )


    with relationship_col1:

        x_variable = st.selectbox(
            "X-axis variable",
            [
                "NDVI",
                "Temperature",
                "Humidity",
                "Wind_Speed",
                "Solar_Radiation",
                "Precipitation",
                "Air_Pressure"
            ]
        )


    with relationship_col2:

        y_variable = st.selectbox(
            "Y-axis variable",
            [
                "Temperature",
                "Humidity",
                "Wind_Speed",
                "Solar_Radiation",
                "Precipitation",
                "Air_Pressure",
                "NDVI"
            ],
            index=0
        )


    fig_relationship = px.scatter(
        filtered_df,
        x=x_variable,
        y=y_variable,
        color="LULC_Type",
        hover_data=[
            "Location_ID",
            "cdTimestamp"
        ],
        opacity=0.65
    )


    fig_relationship.update_layout(
        xaxis_title=x_variable.replace(
            "_",
            " "
        ),

        yaxis_title=y_variable.replace(
            "_",
            " "
        )
    )


    st.plotly_chart(
        fig_relationship,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Pearson correlation
    # --------------------------------------------------------

    try:

        pearson_value = (
            filtered_df[
                [x_variable, y_variable]
            ]
            .corr(method="pearson")
            .iloc[0, 1]
        )

    except Exception:

        pearson_value = np.nan


    if not np.isnan(pearson_value):

        st.metric(
            "Pearson Correlation",
            f"{pearson_value:.3f}"
        )


    st.caption(
        "Correlation indicates statistical association, "
        "not causation."
    )


    # ========================================================
    # CORRELATION MATRIX
    # ========================================================

    st.subheader(
        "Environmental Correlation Matrix"
    )


    correlation_columns = [
        "Temperature",
        "Humidity",
        "Wind_Speed",
        "Solar_Radiation",
        "Precipitation",
        "Air_Pressure",
        "NDVI"
    ]


    correlation_matrix = (
        filtered_df[
            correlation_columns
        ]
        .corr()
        .round(2)
    )


    fig_corr = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        title="Environmental Variable Correlations"
    )


    fig_corr.update_layout(
        height=600
    )


    st.plotly_chart(
        fig_corr,
        use_container_width=True
    )


# ============================================================
# TAB 6 — ANOMALIES
# ============================================================

with tabs[5]:

    st.header(
        "Temperature Anomaly Analysis"
    )


    st.caption(
        "Anomalies are calculated relative to each "
        "location's average temperature."
    )


    # --------------------------------------------------------
    # Calculate location baseline
    # --------------------------------------------------------

    anomaly_df = filtered_df.copy()


    location_mean = (
        anomaly_df
        .groupby("Location_ID")[
            "Temperature"
        ]
        .transform("mean")
    )


    anomaly_df[
        "Temperature_Anomaly_Calculated"
    ] = (
        anomaly_df["Temperature"]
        - location_mean
    )


    # --------------------------------------------------------
    # Classify anomaly
    # --------------------------------------------------------

    def classify_anomaly(
        value
    ):

        if value <= -2:

            return "Strongly Cool"

        elif value <= -0.5:

            return "Cool"

        elif value <= 0.5:

            return "Normal"

        elif value <= 2:

            return "Warm"

        else:

            return "Strongly Warm"


    anomaly_df[
        "Anomaly_Category"
    ] = (
        anomaly_df[
            "Temperature_Anomaly_Calculated"
        ]
        .apply(classify_anomaly)
    )


    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    anomaly_distribution = (
        anomaly_df[
            "Anomaly_Category"
        ]
        .value_counts()
        .reindex(
            [
                "Strongly Cool",
                "Cool",
                "Normal",
                "Warm",
                "Strongly Warm"
            ],
            fill_value=0
        )
        .reset_index()
    )


    anomaly_distribution.columns = [
        "Category",
        "Count"
    ]


    fig_anomaly = px.bar(
        anomaly_distribution,
        x="Category",
        y="Count",
        text_auto=True,
        title="Temperature Anomaly Distribution"
    )


    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Anomaly threshold selector
    # --------------------------------------------------------

    anomaly_threshold = st.slider(
        "Show anomalies beyond ±°C",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5
    )


    strong_anomalies = anomaly_df[
        anomaly_df[
            "Temperature_Anomaly_Calculated"
        ].abs()
        >= anomaly_threshold
    ].copy()


    st.metric(
        "Detected Strong Anomalies",
        f"{len(strong_anomalies):,}"
    )


    # --------------------------------------------------------
    # Anomaly table
    # --------------------------------------------------------

    st.subheader(
        "Detected Temperature Anomalies"
    )


    st.dataframe(
        strong_anomalies[
            [
                "cdTimestamp",
                "Location_ID",
                "LULC_Type",
                "Temperature",
                "Temperature_Anomaly_Calculated",
                "Anomaly_Category"
            ]
        ]
        .sort_values(
            "Temperature_Anomaly_Calculated"
        ),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # Extreme low-temperature warning
    # --------------------------------------------------------

    extreme_count = (
        filtered_df["Temperature"] <= -5
    ).sum()


    st.warning(
        f"{extreme_count:,} observations in the "
        f"current selection have temperatures at or "
        f"below −5°C. These values should be investigated "
        f"as potential data-quality or environmental anomalies."
    )


# ============================================================
# TAB 7 — SPATIAL ANALYSIS
# ============================================================

with tabs[6]:

    st.header(
        "Spatial Microclimate Analysis"
    )

    st.caption(
        "Explore environmental conditions across monitoring stations."
    )


    # --------------------------------------------------------
    # Station aggregation
    # --------------------------------------------------------

    spatial_df = (
        filtered_df
        .groupby(
            [
                "Location_ID",
                "Latitude",
                "Longitude",
                "LULC_Type"
            ]
        )
        .agg(
            Average_Temperature=(
                "Temperature",
                "mean"
            ),

            Average_Humidity=(
                "Humidity",
                "mean"
            ),

            Average_NDVI=(
                "NDVI",
                "mean"
            ),

            Average_Wind_Speed=(
                "Wind_Speed",
                "mean"
            )
        )
        .reset_index()
    )


    # --------------------------------------------------------
    # Map variable
    # --------------------------------------------------------

    map_metric = st.selectbox(
        "Select variable to visualize",
        [
            "Average_Temperature",
            "Average_Humidity",
            "Average_NDVI",
            "Average_Wind_Speed"
        ]
    )


    map_labels = {

        "Average_Temperature":
            "Average Temperature",

        "Average_Humidity":
            "Average Humidity",

        "Average_NDVI":
            "Average NDVI",

        "Average_Wind_Speed":
            "Average Wind Speed"
    }


    # --------------------------------------------------------
    # Interactive map
    # --------------------------------------------------------

    try:

        fig_map = px.scatter_map(
            spatial_df,
            lat="Latitude",
            lon="Longitude",

            # Use COLOR for the selected metric.
            # Do NOT use the metric as marker size because
            # some environmental values can be negative.
            color=map_metric,

            # Fixed positive marker size.
            size_max=16,

            hover_name="Location_ID",

            hover_data={
                "LULC_Type": True,
                "Average_Temperature": ":.2f",
                "Average_Humidity": ":.2f",
                "Average_NDVI": ":.2f",
                "Average_Wind_Speed": ":.2f",
                "Latitude": ":.4f",
                "Longitude": ":.4f"
            },

            zoom=2,

            height=600,

            title=(
                f"{map_labels[map_metric]} "
                "by Monitoring Location"
            )
        )


        fig_map.update_traces(
            marker=dict(
                size=10
            )
        )


        fig_map.update_layout(
            map_style="open-street-map",

            margin=dict(
                l=0,
                r=0,
                t=60,
                b=0
            ),

            coloraxis_colorbar=dict(
                title=map_labels[map_metric]
            )
        )


    except AttributeError:

        # Compatibility with older Plotly versions

        fig_map = px.scatter_mapbox(
            spatial_df,
            lat="Latitude",
            lon="Longitude",

            color=map_metric,

            hover_name="Location_ID",

            hover_data={
                "LULC_Type": True,
                "Average_Temperature": ":.2f",
                "Average_Humidity": ":.2f",
                "Average_NDVI": ":.2f",
                "Average_Wind_Speed": ":.2f",
                "Latitude": ":.4f",
                "Longitude": ":.4f"
            },

            zoom=2,

            height=600,

            title=(
                f"{map_labels[map_metric]} "
                "by Monitoring Location"
            )
        )


        fig_map.update_traces(
            marker=dict(
                size=10
            )
        )


        fig_map.update_layout(
            mapbox_style="open-street-map",

            margin=dict(
                l=0,
                r=0,
                t=60,
                b=0
            ),

            coloraxis_colorbar=dict(
                title=map_labels[map_metric]
            )
        )


    # --------------------------------------------------------
    # Display map
    # --------------------------------------------------------

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Station summary
    # --------------------------------------------------------

    st.subheader(
        "Station Environmental Summary"
    )


    display_columns = [
        "Location_ID",
        "LULC_Type",
        "Latitude",
        "Longitude",
        "Average_Temperature",
        "Average_Humidity",
        "Average_NDVI",
        "Average_Wind_Speed"
    ]


    st.dataframe(
        spatial_df[
            display_columns
        ].sort_values(
            "Average_Temperature",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# TAB 8 — DATA EXPLORER
# ============================================================

with tabs[7]:

    st.header(
        "Dataset Explorer"
    )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    data_col1, data_col2, data_col3, data_col4 = (
        st.columns(4)
    )


    with data_col1:

        st.metric(
            "Observations",
            f"{len(filtered_df):,}"
        )


    with data_col2:

        st.metric(
            "Locations",
            filtered_df[
                "Location_ID"
            ].nunique()
        )


    with data_col3:

        st.metric(
            "LULC Types",
            filtered_df[
                "LULC_Type"
            ].nunique()
        )


    with data_col4:

        st.metric(
            "Variables",
            filtered_df.shape[1]
        )


    # --------------------------------------------------------
    # Dataset preview
    # --------------------------------------------------------

    st.subheader(
        "Filtered Dataset"
    )


    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=550,
        hide_index=True
    )


    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    csv_data = (
        filtered_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(
        label="⬇️ Download Filtered Dataset",
        data=csv_data,
        file_name="atmosync_filtered_data.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AtmoSync | Microclimate Analytics | "
    "Data-driven environmental exploration"
)
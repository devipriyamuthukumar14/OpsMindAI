
import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="OpsMind AI",
    page_icon="🧠",
    layout="wide"
)

try:
    API_URL = os.getenv("API_BASE_URL") or st.secrets["API_BASE_URL"]
except Exception:
    API_URL = "http://127.0.0.1:8000"

API_URL = API_URL.rstrip("/")


# ---------------- API FUNCTIONS ----------------

def api_get(endpoint):
    try:
        response = requests.get(
            f"{API_URL}/{endpoint}",
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        st.error(f"API connection failed: {error}")
        return None


def api_post(endpoint, payload):
    try:
        response = requests.post(
            f"{API_URL}/{endpoint}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        st.error(f"API request failed: {error}")
        return None


# ---------------- SIDEBAR ----------------

st.sidebar.title("🧠 OpsMind AI")
st.sidebar.caption("Intelligent IT Operations Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Ticket Classification",
        "Log Analysis",
        "History"
    ]
)

st.sidebar.divider()
st.sidebar.caption("AI-Powered IT Helpdesk & Log Analysis")


# ---------------- OVERVIEW ----------------

if page == "Overview":

    st.title("Operations Overview")
    st.write("Monitor IT support tickets and system log anomalies.")

    ticket_data = api_get("ticket-history")
    log_data = api_get("log-history")

    if ticket_data is not None and log_data is not None:

        tickets = ticket_data.get("tickets", [])
        logs = log_data.get("logs", [])

        anomalies = [
            log for log in logs
            if log["prediction"] == "Anomaly"
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tickets", ticket_data["total_records"])
        col2.metric("Logs Analyzed", log_data["total_records"])
        col3.metric("Anomalies Detected", len(anomalies))

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("Ticket Categories")

            if tickets:
                ticket_df = pd.DataFrame(tickets)

                category_counts = (
                    ticket_df["predicted_category"]
                    .value_counts()
                    .reset_index()
                )
                category_counts.columns = ["Category", "Count"]

                fig = px.bar(
                    category_counts,
                    x="Category",
                    y="Count",
                    title="Ticket Distribution",
                    text="Count"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ticket records available yet.")

        with right:
            st.subheader("Log Analysis")

            if logs:
                log_df = pd.DataFrame(logs)

                prediction_counts = (
                    log_df["prediction"]
                    .value_counts()
                    .reset_index()
                )
                prediction_counts.columns = ["Prediction", "Count"]

                fig = px.pie(
                    prediction_counts,
                    names="Prediction",
                    values="Count",
                    title="Normal vs Anomaly"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No log records available yet.")

        st.caption("Charts reflect the latest records returned by the API.")


# ---------------- TICKET CLASSIFICATION ----------------

elif page == "Ticket Classification":

    st.title("🎫 IT Ticket Classification")

    st.write(
        "Enter an IT support issue to predict its appropriate category."
    )

    with st.form("ticket_form"):

        description = st.text_area(
            "Ticket Description",
            placeholder="Example: I cannot access my account after resetting my password."
        )

        submitted = st.form_submit_button(
            "Classify Ticket",
            type="primary"
        )

    if submitted:

        if not description.strip():
            st.warning("Please enter a ticket description.")

        else:
            with st.spinner("Classifying ticket..."):

                result = api_post(
                    "classify-ticket",
                    {"description": description}
                )

            if result:

                st.success("Ticket classified successfully!")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Predicted Category",
                    result["predicted_category"]
                )

                col2.metric(
                    "Model Confidence",
                    f'{result["confidence"]:.2f}%'
                )

                if result["confidence"] < 70:
                    st.warning(
                        "Low-confidence prediction. Manual review recommended."
                    )
                elif result["confidence"] < 80:
                    st.info(
                        "Moderate-confidence prediction. Please verify the category."
                    )
                else:
                    st.success("High-confidence prediction.")


# ---------------- LOG ANALYSIS ----------------

elif page == "Log Analysis":

    st.title("📊 Intelligent Log Analysis")

    st.write(
        "Submit a system log record to identify potential anomalies."
    )

    with st.form("log_form"):

        message = st.text_area(
            "Log Message",
            placeholder="Example: data TLB error interrupt"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            severity = st.selectbox(
                "Severity",
                ["INFO", "WARNING", "ERROR", "FATAL",
                 "FAILURE", "SEVERE", "Kill"]
            )

        with col2:
            component = st.text_input(
                "Component",
                value="KERNEL"
            )

        with col3:
            source = st.text_input(
                "Source",
                value="RAS"
            )

        submitted = st.form_submit_button(
            "Analyze Log",
            type="primary"
        )

    if submitted:

        if not message.strip():
            st.warning("Please enter a log message.")

        else:

            payload = {
                "message": message,
                "severity": severity,
                "component": component,
                "source": source
            }

            with st.spinner("Analyzing system log..."):

                result = api_post("analyze-log", payload)

            if result:

                analysis = result["analysis"]

                if analysis["prediction"] == "Anomaly":
                    st.error("⚠️ Potential Anomaly Detected")
                else:
                    st.success("System Log Classified as Normal")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Prediction",
                    analysis["prediction"]
                )

                col2.metric(
                    "Anomaly Probability",
                    f'{analysis["anomaly_probability"]:.2f}%'
                )

                st.progress(
                    max(0.0, min(
                        analysis["anomaly_probability"] / 100,
                        1.0
                    ))
                )

                st.caption(
                    f'Normal probability: '
                    f'{analysis["normal_probability"]:.2f}%'
                )


# ---------------- HISTORY ----------------

elif page == "History":

    st.title("📁 Analysis History")

    tab1, tab2 = st.tabs(
        ["Ticket History", "Log History"]
    )

    with tab1:

        st.subheader("Previous Ticket Classifications")

        if st.button("Refresh Ticket History"):
            st.rerun()

        ticket_data = api_get("ticket-history")

        if ticket_data is not None:

            tickets = ticket_data.get("tickets", [])

            if tickets:
                ticket_df = pd.DataFrame(tickets)

                st.dataframe(
                    ticket_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No ticket history available.")

    with tab2:

        st.subheader("Previous Log Analyses")

        if st.button("Refresh Log History"):
            st.rerun()

        log_data = api_get("log-history")

        if log_data is not None:

            logs = log_data.get("logs", [])

            if logs:
                log_df = pd.DataFrame(logs)

                st.dataframe(
                    log_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No log history available.")


# ---------------- FOOTER ----------------

st.sidebar.divider()
st.sidebar.caption("OpsMind AI | Version 1.0.0")

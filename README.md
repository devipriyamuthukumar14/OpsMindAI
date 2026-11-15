# OpsMind AI

AI-Powered IT Helpdesk and Intelligent Log Analysis System

## Overview
OpsMind AI is an MVP that combines machine learning, API services,
knowledge retrieval, and a dashboard to support IT operations.

## Features
- **Ticket Classification:** Categorizes IT support tickets into 8 categories using TF-IDF and Logistic Regression.
- **Log Anomaly Detection:** Identifies unusual system log events using supervised Logistic Regression, with Isolation Forest as a comparison baseline.
- **Knowledge Retrieval:** Retrieves relevant troubleshooting suggestions using TF-IDF similarity.
- **REST API:** FastAPI endpoints for ticket classification, log analysis, and knowledge search.
- **History Tracking:** SQLite database for storing ticket and log analysis history.
- **Dashboard:** Streamlit interface for interacting with the system and viewing history.

## Technology Stack
Python, Pandas, NumPy, Scikit-learn, FastAPI, SQLite, Streamlit, Plotly.

## Project Status
Core modules and dashboard implementation completed.
The Streamlit frontend and FastAPI backend require separate public hosting
for a fully accessible cloud deployment.

## Note
This project is an academic MVP and has not been validated for production use.

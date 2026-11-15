
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import sys
import joblib

# --------------------------------------------------
# 1. PROJECT PATH AND MODULE IMPORTS
# --------------------------------------------------

PROJECT_PATH = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_PATH / "src"))

from log_analyzer.predictor import predict_log
from knowledge_retrieval.retriever import search_knowledge_base

from database import (
    create_tables,
    save_ticket,
    save_log,
    get_ticket_history,
    get_log_history
)

# Ensure database tables exist when the API starts
create_tables()


# --------------------------------------------------
# 2. LOAD TICKET CLASSIFICATION MODEL
# --------------------------------------------------

ticket_model = joblib.load(
    PROJECT_PATH / "models" / "ticket_classifier.pkl"
)


# --------------------------------------------------
# 3. CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="OpsMind AI",
    description="AI-Powered IT Helpdesk and Intelligent Log Analysis System",
    version="1.0.0"
)


# --------------------------------------------------
# 4. HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "OpsMind AI",
        "status": "Running",
        "message": "Welcome to OpsMind AI API"
    }


# --------------------------------------------------
# 5. HEALTH CHECK ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# 6. SYSTEM INFORMATION ENDPOINT
# --------------------------------------------------

@app.get("/info")
def system_info():
    return {
        "name": "OpsMind AI",
        "modules": [
            "Ticket Classification",
            "Log Anomaly Detection",
            "Knowledge Retrieval"
        ],
        "version": "1.0.0"
    }


# --------------------------------------------------
# 7. LOG REQUEST MODEL
# --------------------------------------------------

class LogRequest(BaseModel):
    message: str
    severity: str
    component: str
    source: str


# --------------------------------------------------
# 8. LOG ANOMALY DETECTION ENDPOINT
# --------------------------------------------------


@app.post("/analyze-log")
def analyze_log(log: LogRequest):
    log_data = log.model_dump()

    result = predict_log(log_data)

    # Save log analysis result in SQLite
    save_log(log_data, result)

    return {
        "input_log": log_data,
        "analysis": result
    }


# --------------------------------------------------
# 9. TICKET REQUEST MODEL
# --------------------------------------------------

class TicketRequest(BaseModel):
    description: str


# --------------------------------------------------
# 10. TICKET CLASSIFICATION ENDPOINT
# --------------------------------------------------


@app.post("/classify-ticket")
def classify_ticket(ticket: TicketRequest):
    prediction = ticket_model.predict([ticket.description])[0]
    probabilities = ticket_model.predict_proba([ticket.description])[0]
    confidence = float(max(probabilities)) * 100

    # Save classification result in SQLite
    save_ticket(
        ticket.description,
        str(prediction),
        round(confidence, 2)
    )

    return {
        "ticket_description": ticket.description,
        "predicted_category": str(prediction),
        "confidence": round(confidence, 2)
    }


# --------------------------------------------------
# 11. KNOWLEDGE RETRIEVAL REQUEST MODEL
# --------------------------------------------------

class KnowledgeRequest(BaseModel):
    query: str


# --------------------------------------------------
# 12. KNOWLEDGE RETRIEVAL ENDPOINT
# --------------------------------------------------

@app.post("/search-knowledge")
def search_knowledge(request: KnowledgeRequest):

    results = search_knowledge_base(
        request.query,
        top_k=3
    )

    return {
        "query": request.query,
        "results": results.to_dict(orient="records")
    }


@app.get("/ticket-history")
def ticket_history():
    """Return recent ticket classification history."""
    records = get_ticket_history(limit=20)

    return {
        "total_records": len(records),
        "tickets": records
    }


@app.get("/log-history")
def log_history():
    """Return recent log analysis history."""
    records = get_log_history(limit=20)

    return {
        "total_records": len(records),
        "logs": records
    }

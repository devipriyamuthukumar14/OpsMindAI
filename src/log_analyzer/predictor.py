
import joblib
import pandas as pd

from pathlib import Path
from scipy.sparse import hstack, csr_matrix


# Locate saved model files
PROJECT_PATH = Path(__file__).resolve().parents[2]
MODELS_PATH = PROJECT_PATH / "models"

# Load trained model and preprocessing objects
log_model = joblib.load(
    MODELS_PATH / "bgl_logistic_regression.pkl"
)

log_vectorizer = joblib.load(
    MODELS_PATH / "bgl_tfidf_vectorizer.pkl"
)

log_encoder = joblib.load(
    MODELS_PATH / "bgl_categorical_encoder.pkl"
)


def predict_log(log_record):

    log_df = pd.DataFrame([log_record])

    # Prepare message
    message_text = log_df["message"].fillna("")

    # Prepare categorical features
    categorical = log_df[
        ["severity", "component", "source"]
    ].fillna("[MISSING]")

    # Prepare numerical features
    message_features = pd.DataFrame({
        "message_length": message_text.str.len(),
        "word_count": message_text.str.split().str.len(),
        "message_missing": log_df["message"].isna().astype(int)
    })

    # Apply saved preprocessing
    text_features = log_vectorizer.transform(message_text)
    cat_features = log_encoder.transform(categorical)

    # Combine features
    features = hstack([
        text_features,
        csr_matrix(cat_features),
        csr_matrix(message_features.values)
    ], format="csr")

    # Predict
    prediction = log_model.predict(features)[0]
    probabilities = log_model.predict_proba(features)[0]

    return {
        "prediction": "Anomaly" if prediction == 1 else "Normal",
        "anomaly_probability": round(
            float(probabilities[1]) * 100, 2
        ),
        "normal_probability": round(
            float(probabilities[0]) * 100, 2
        )
    }

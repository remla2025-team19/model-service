"""
Flask API of the SMS Spam detection model model.
"""

from flask import Flask, jsonify, request
from flasgger import Swagger
import pickle
import os
import sys
import requests
from pathlib import Path
from lib_ml.preprocessing import TextPreprocessor

app = Flask(__name__)
swagger = Swagger(app)
prediction_map = {0: "negative", 1: "positive"}

classifier = None
vectorizer = None
preprocessor = TextPreprocessor()


def download_model(version, model_path):
    """
    Download model from GitHub releases if it doesn't exist locally.

    Args:
        version (str): Model version tag (e.g., v1.0.11)
        model_path (Path): Path where model should be saved

    Returns:
        bool: True if download was successful, False otherwise
    """
    # Create directory if it doesn't exist
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Download model from GitHub
    url = f"https://github.com/remla2025-team19/model-training/releases/download/{version}/sentiment_model_{version}.pkl"
    print(f"Downloading model from {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for error status codes

        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Model downloaded successfully to {model_path}")
        return True

    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        return False


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify if the service is running.
    ---
    responses:
      200:
        description: "Service is healthy"
    """
    return jsonify({"status": "healthy"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict whether a review is positive or negative.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                review:
                    type: string
                    example: This is an example of a review.
    responses:
      200:
        description: "The result of the classification: 'negative' or 'positive'."
    """
    input_data = request.get_json()
    review = input_data.get("review")
    corpus = preprocessor.preprocess_texts([review])
    # processed_sms = prepare(sms)
    features = vectorizer.transform(corpus).toarray()
    prediction = classifier.predict(features)[0]
    print(f"Prediction: {prediction}, Type: {type(prediction)}")
    prediction = int(prediction)

    res = {
        "result": prediction_map[prediction],
        "classifier": "Naive Bayes",
        "review": review,
    }
    print(res)
    return jsonify(res)


@app.route("/dumbpredict", methods=["POST"])
def dumb_predict():
    """
    Predict whether a given review is positive or negative (dumb model: always predicts 'positive').
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                review:
                    type: string
                    example: This is an example of a review.
    responses:
      200:
        description: "The result of the classification: 'negative' or 'positive'."
    """
    input_data = request.get_json()
    review = input_data.get("review")

    return jsonify(
        {"result": "positive", "classifier": "naive bayes", "review": review}
    )


if __name__ == "__main__":
    # Check if MODEL_VERSION environment variable is set
    model_version = os.environ.get("MODEL_VERSION")
    if not model_version:
        print("ERROR: MODEL_VERSION environment variable not set")
        sys.exit(1)
    print(f"Using model version: {model_version}")

    # Setup model paths

    models_cache_dir = Path(os.getenv("MODEL_CACHE_DIR", "./models_cache"))
    model_path = models_cache_dir / f"sentiment_model_{model_version}.pkl"

    # Ensure the models_cache directory exists
    models_cache_dir.mkdir(exist_ok=True)

    # Check if model exists, download if not
    if not model_path.exists():
        print(f"Model {model_path} not found. Downloading...")
        success = download_model(model_version, model_path)
        if not success:
            print("Failed to download model. Exiting.")
            sys.exit(1)

    try:
        print(f"Loading model from {model_path}")
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)
            print(f"Keys: {model_data.keys()}")
            classifier = model_data["classifier"]
            vectorizer = model_data["vectorizer"]
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # Retrieve host and port from environment
    HOST: str = os.getenv("MODEL_SERVICE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MODEL_SERVICE_PORT", "8080"))
    print(f"HOST = {HOST}, PORT = {PORT}")
    app.run(host=HOST, port=PORT, debug=True)

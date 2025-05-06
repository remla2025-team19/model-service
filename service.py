"""
Flask API of the SMS Spam detection model model.
"""
#import traceback
import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import pickle
import os
from lib_ml.preprocessing import TextPreprocessor

# from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)
prediction_map = {
    0: "negative",
    1: "positive"
}

classifier = None
vectorizer = None
preprocessor = TextPreprocessor()

@app.route('/predict', methods=['POST'])
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
    review = input_data.get('review')
    corpus = preprocessor.preprocess_texts([review])
    # processed_sms = prepare(sms)
    features = vectorizer.transform(corpus).toarray()
    prediction = classifier.predict(features)[0]
    print(f"Prediction: {prediction}, Type: {type(prediction)}")
    prediction = int(prediction)
    
    res = {
        "result": prediction_map[prediction],
        "classifier": "Naive Bayes",
        "review": review
    }
    print(res)
    return jsonify(res)

@app.route('/dumbpredict', methods=['POST'])
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
    review = input_data.get('review')
    
    return jsonify({
        "result": "positive",
        "classifier": "naive bayes",
        "review": review
    })

if __name__ == '__main__':
    model_path = 'sentiment_model.pkl'
    
    try:
      with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
        print(f"Keys: {model_data.keys()}")
        classifier = model_data['classifier']
        vectorizer = model_data['vectorizer']
    except Exception as e:
       print(f"Error loading model: {e}")

    # Retrieve host and port from environment
    HOST: str = os.getenv("MODEL_SERVICE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MODEL_SERVICE_PORT", "8080"))
    print(f"HOST = {HOST}, PORT = {PORT}")
    app.run(host=HOST, port=PORT, debug=True)
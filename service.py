"""
Flask API of the SMS Spam detection model model.
"""
#import traceback
import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import pickle

# from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)
prediction_map = {
    0: "negative",
    1: "positive"
}

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
    # processed_sms = prepare(sms)
    cv =  pickle.load(open("c1_BoW_Sentiment_Model.pkl", "rb"))
    sms_query = cv.transform([review]).toarray()
    model = joblib.load('c2_Classifier_Sentiment_Model.joblib')
    prediction = model.predict(sms_query)[0]
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
    Predict whether a given SMS is Spam or Ham (dumb model: always predicts 'ham').
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
    clf = joblib.load('c2_Classifier_Sentiment_Model.joblib')
    
    app.run(host="0.0.0.0", port=8080, debug=True)
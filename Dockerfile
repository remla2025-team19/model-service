FROM python:3.12.9-slim
WORKDIR /root
COPY requirements.txt /root/
COPY c2_Classifier_Sentiment_Model.joblib /root/
COPY c1_BoW_Sentiment_Model.pkl /root/
RUN pip install -r requirements.txt
COPY service.py /root/
ENTRYPOINT ["python"]
CMD ["service.py"]
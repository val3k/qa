FROM python:3.8-buster
ADD . /app
WORKDIR /app

ENV PYTHONPATH="/app"
RUN pip install flask requests boto3 numpy faiss-cpu
RUN export FLASK_APP=index
CMD python index.py

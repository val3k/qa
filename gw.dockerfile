FROM python:3.8-buster
ADD . /app
WORKDIR /app

ENV PYTHONPATH="/app"
RUN pip install sentence_transformers
RUN pip install flask requests boto3 uwsgi numpy
RUN export FLASK_APP=gateway
CMD uwsgi --http 0.0.0.0:5008 --wsgi-file gateway.py --master --processes 1 --threads 5
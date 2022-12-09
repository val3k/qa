FROM python:3.8-buster
ADD . /app
WORKDIR /app

ENV PYTHONPATH="/app"
RUN pip install flask requests boto3 faiss-cpu uwsgi numpy
RUN export FLASK_APP=cutter
# CMD uwsgi --http 0.0.0.0:6000 --wsgi-file cutter.py --master --processes 1 --threads 5
CMD python cutter.py
import os
import json
import requests
import boto3
import numpy as np
import faiss
from flask import Flask, jsonify, request, Response

os.environ['KNN'] = "5"


def init_s3() -> boto3.resource:
    """Create s3 resource

    Returns:
        boto3.resource: resource
    """
    s3 = boto3.resource('s3',
                        aws_access_key_id=os.environ['S3_KEY_ID'],
                        aws_secret_access_key=os.environ['S3_SECRET'],
                        endpoint_url=os.environ['S3_URL'])
    return s3

kn = os.environ['KNN']

s3_resource = init_s3()
s3bucket = s3_resource.Bucket(os.environ['S3_BUCKET'])
# Load index from s3
ind_path = os.environ['IND_PATH']
s3_prefix = os.environ['S3_PREFIX']
folder = ind_path.split('ind_')[0]
if not os.path.exists(folder):
    os.makedirs(folder)
s3bucket.download_file(s3_prefix + ind_path, ind_path)
_index = faiss.read_index(ind_path)
# Load mapping from s3
map_path = ind_path.replace('ind_', 'map_')
s3bucket.download_file(s3_prefix + map_path, map_path)
with open(map_path) as fl:
    mapq = json.load(fl)
ind_loaded = True

app = Flask(__name__)

@app.route('/find', methods=['GET', 'POST'])
def pred1():
    data = request.get_json()
    arr = np.array(data['emb'], dtype=np.float32)

    _, q_ids = _index.search(arr, k=int(kn))
    print(q_ids)
    qs = [mapq.get(f"{i}", 'not found') for i in q_ids[0]]
    return jsonify({'questions': qs})

@app.route('/checkind', methods=['GET', 'POST'])
def check():
    if ind_loaded:
        return jsonify({'status': 'yes'})
    else:
        return jsonify({'status': 'no'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000)
else:
    application = app
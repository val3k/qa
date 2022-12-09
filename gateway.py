import os
import json
import boto3
import requests
import pickle
from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer, util
import numpy as np


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

def get_centers(fpath: str) -> np.array: 
    """Load cluster centers from s3

    Args:
        fpath (str): centers file path

    Returns:
        np.array: array with centers
    """    
    s3_prefix = os.environ['S3_PREFIX']
    folder = fpath.split('clusters')[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
    s3_resource = init_s3()
    s3bucket = s3_resource.Bucket(os.environ['S3_BUCKET'])
    s3bucket.download_file(s3_prefix + fpath, fpath)

    with open(fpath, 'rb') as fl:
        centers = pickle.load(fl)
    num_cl = len(centers)
    ordered_cents = []
    for i in range(num_cl):
        ordered_cents.append(centers[str(i)])
    return np.array(ordered_cents)

def get_sent_emb(sent: str) -> np.array:
    """Get sentence embedding

    Args:
        sent (str): text sentece

    Returns:
        np.array: sentence embedding
    """    
    sents = [sent]
    embs = model.encode(sents)
    return embs

def get_clust_num(sent_emb: np.array, arr_cent: np.array) -> int:
    """Define cluster number

    Args:
        sent_emb (np.array): sentence embedding
        arr_cent (np.array): clusters centers

    Returns:
        int: cluster number
    """    
    return np.argmin(np.abs(np.array(util.cos_sim(sent_emb, arr_cent))))

# Load embedder
model_status = False
cl_dir = os.environ['CENT_PATH']
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
model_status = True
arr_cent = get_centers(cl_dir)[:4]

app = Flask(__name__)

@app.route('/send_q', methods=['GET', 'POST'])
def pred1():
    index_url = os.environ['INDEX_URL']

    r = request.get_json()
    quest = r['question']
    
    _emb = get_sent_emb(quest)
    cl_num = get_clust_num(_emb, arr_cent)

    index_url = index_url.replace('NUM', f'{cl_num}')
    data = {'emb': _emb.tolist()}
    
    response = requests.post(index_url, json=data)
    pred = response.json()['questions']
    return jsonify({'prediction': pred})

@app.route('/hcheck', methods=['GET', 'POST'])
def check_model():
    if model_status:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'not ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5008)
else:
    application = app
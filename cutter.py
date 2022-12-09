import os
import json
from typing import Mapping, List, Tuple
import boto3
import pickle
import faiss
from flask import Flask, jsonify, request


cl_qu_pth = os.environ['CLUST_RES_PATH']
emb_ind_pth = os.environ['EMB_RES_PATH']
cl_dir = os.environ['CENT_PATH']
s3_prefix = os.environ['S3_PREFIX']

app = Flask(__name__)

def build_index(clusters: Mapping, q_emb: Mapping, path_to_idx: str, version: str) -> Tuple[List, List]:
    """Build faiss index and mapping

    Args:
        clusters (Mapping): clustering results Dict[str, List[str]]
        q_emb (Mapping): questions embedinngs Dict[str, np.ndarray]
        path_to_idx (str): full index
        version (str): data version

    Returns:
        List, List: list of pathes for index and mappings
    """    
    if path_to_idx.endswith('/'):
        path_to_idx = path_to_idx[:-1]
    clust_num = [i for i in clusters.keys()]
    res_inds = []
    map_q = []
    qnum = 0
    for clust in clust_num:
        questions = clusters[f'{clust}'][:100] # for testing
        f_ind = faiss.IndexHNSWFlat(512, 10)
        id_mapping = {}
        for i, q in enumerate(questions):
            emb = q_emb.get(q)
            f_ind.add(emb)
            id_mapping[i] = q
            qnum += 1

        ind_name = f'{path_to_idx}/ind_{clust}_dg{version}'
        faiss.write_index(f_ind, ind_name)
        res_inds.append(ind_name)

        mapp_name = f'{path_to_idx}/map_{clust}_dg{version}'
        with open(mapp_name, 'w') as fl:
            json.dump(id_mapping, fl)
        map_q.append(mapp_name)

    return res_inds, map_q

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


@app.route('/build')
def build():
    # apply version to file names
    version = request.args.get('version')
    clusters_version = cl_qu_pth.replace('_dg1', f'_dg{version}')
    emb_version = emb_ind_pth.replace('_dg1', f'_dg{version}')
    cl_dir_ver = cl_dir.replace('_dg1', f'_dg{version}')

    with open(clusters_version) as fl:
        clusters = json.load(fl)
    with open(emb_version, 'rb') as fl:
        ques_emb = pickle.load(fl)
    
    pth='/app/data'
    if not os.path.exists(pth):
        os.makedirs(pth)
    ind_dirs, map_dirs = build_index(clusters, ques_emb, '/app/data', version)
    s3_resource = init_s3()
    s3bucket = s3_resource.Bucket(os.environ['S3_BUCKET'])
    
    cl_dir_remote = cl_dir_ver.replace('/data_all/', '/data/')
    s3bucket.upload_file(cl_dir_ver, s3_prefix + cl_dir_remote)
    
    for i in ind_dirs:
        s3bucket.upload_file(i, s3_prefix + i)
    for m in map_dirs:
        s3bucket.upload_file(m, s3_prefix + m)
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)
else:
    application = app
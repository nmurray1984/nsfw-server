import os
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import g
import psycopg2
import base64
import logging
import json
import requests
import random

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
app.logger.info('creating new connection')
db = psycopg2.connect(DATABASE_URL, sslmode='require')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    return db


@app.route('/')
def persist_url():
    url = request.args.get('url')
    base64url = base64.b64encode((url.encode('ascii'))).decode('ascii')
    app.logger.info('Persisting url: %s', base64url)
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    query = "insert into nsfw_server.contributed_image (url) values (%(url)s)"
    cursor.execute(query, {'url': base64url})
    conn.commit()
    cursor.close()
    conn.close()
    
    return 'complete'

@app.route('/image-test')
def image_test():
    url = request.args.get('url')
    rtn = '<!DOCTYPE html><html><body><img src="%s" /></body></html>' % url
    return rtn

# test with this -> curl --request POST --data '{"test":123, "test2":124}' http://localhost:5000/ground-truth-result/9821
@app.route('/ground-truth-result/<image_id>', methods=['POST'])
def ground_truth_result(image_id):
    if request.method == 'POST':
        app.logger.info('Saving ground truth for image: %s', image_id)
        #json_result = request.get_json(force=True)
        app.logger.info('Form Result: %s', json.dumps(request.form))
        conn = get_db()
        cursor = conn.cursor()
        query = "update nsfw_server.image_result set ground_truth_result = %(json_result)s where image_id = %(image_id)s"
        cursor.execute(query, {'image_id': image_id, 'json_result': json.dumps(request.form)})
        conn.commit()
        cursor.close()     
        return redirect('/safe-classifier')
    else:
        return 'bad request', 400

#@app.route('/ground-truth-random-image', methods=['GET'])
def ground_truth_random_image():
    conn = get_db()
    cursor = conn.cursor()
    query = '''SELECT 
    r.image_id
    FROM 
    nsfw_server.image_classification_vw r
    inner join nsfw_server.contributed_image i on i.id = r.image_id
    where 
    r.ground_class is null
    r.original_class is null
    and i.image_bytes is not null
    limit 10'''
    cursor.execute(query)
    query_results = cursor.fetchall()
    if len(query_results) == 0:
        return {"error": True}
    image_id = random.choice(query_results)[0]
    cursor.close()
    query2 = '''select image_bytes from nsfw_server.contributed_image where id = %(image_id)s'''
    cursor2 = conn.cursor()
    cursor2.execute(query2, {'image_id': image_id})
    query2_results = cursor2.fetchone()
    app.logger.info('query results: %s', query2_results)
    image_bytes = query2_results[0]
    base64str = str(base64.b64encode(image_bytes), 'utf-8')
    img_string = 'data:image/jpeg;base64,' + base64str
    return {"id": image_id, "data_url": img_string, "error": False}
    
@app.route('/safe-classifier')
def safe_classifier():
    context = ground_truth_random_image()
    if context['error'] == True:
        return render_template('no-more.html')
    return render_template('ground-truth-ui.html', context=context)

@app.after_request
def after_request_func(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

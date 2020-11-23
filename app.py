import os
from flask import Flask
from flask import request
import psycopg2
import base64
import logging

app = Flask(__name__)

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
        DATABASE_URL = os.environ['DATABASE_URL']
        json_result = request.data
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        query = "update nsfw_server.contributed_image set ground_truth_result = %(json_result)s where id = %(image_id)s"
        cursor.execute(query, {'image_id': image_id, 'json_result': json_result})
        conn.commit()
        cursor.close()
        conn.close()        
        return 'complete', 200
    else:
        return 'bad request', 400


@app.after_request
def after_request_func(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

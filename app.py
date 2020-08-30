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

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

import os
from flask import Flask
from flask import request
from PIL import Image
import requests
from io import BytesIO
import psycopg2
import base64
import hashlib
import io
import logging
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    url = request.args.get('url')
    base64url = base64.b64encode((url.encode('ascii'))).decode('ascii')
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    query = "insert into nsfw_server.contributed_image (url) values (%(url)s)"
    cursor.execute(query, {'url': base64url})
    conn.commit()
    cursor.close()
    conn.close()
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        file_extension = ''
        if img.format == 'JPEG':
            file_extension = '.jpg'
        elif img.format == 'PNG':
            file_extension = '.png'
        else:
            return 'invalid image'
        app.logger.info("file extension detected :%s", file_extension )
        m = hashlib.md5()
        m.update(response.content)
        image_md5 = m.hexdigest()
        #file_name = ''
        #with io.BytesIO() as memf:
            #img.save(memf, img.format)
            #data = memf.getvalue()
            #m.update(data)
            #image_md5 = m.hexdigest()
        file_name = '%s%s' % image_md5, file_extension
        app.logger.info('filename: %s', file_name)
    except:
        return 'problem downloading and processing image'
    return 'done'

    #encrypted_image = encrypt(image_bytes)
    #s3.write(encrypted_image, file_name)
    #scores_json = azure_content_moderator.scan(url)
    #db.write(base64url, file_name, scores_json)



if __name__ == '__main__':
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

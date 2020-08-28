import os
from flask import Flask
from flask import request
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def hello():
    url = request.args.get('url')

    #response = requests.get(url)
    #img = Image.open(BytesIO(response.content))
    
    return url

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

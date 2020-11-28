import urllib, base64, os, http.client
import urllib.parse
import psycopg2
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
import os

DATABASE_URL = os.environ['DATABASE_URL']
CONTENT_MODERATOR_ENDPOINT = os.environ['CONTENT_MODERATOR_ENDPOINT']
CONTENT_MODERATOR_SUBSCRIPTION_KEY = os.environ.get['CONTENT_MODERATOR_SUBSCRIPTION_KEY']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
query = "SELECT id, convert_from(decode(url, 'base64'), 'UTF-8') as url FROM nsfw_server.contributed_image where azure_content_moderator_result is null"
cursor.execute(query)
query_results = cursor.fetchall()

for (image_id, url) in query_results:
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': CONTENT_MODERATOR_SUBSCRIPTION_KEY,
    }

    params = urllib.parse.urlencode({
        'CacheImage': 'true'
    })

    body = '''{
        'DataRepresentation': 'URL',
        'Value': '%s'
    }''' % url

    try:
        hconn = http.client.HTTPSConnection('southcentralus.api.cognitive.microsoft.com')
        hconn.request("POST", "/contentmoderator/moderate/v1.0/ProcessImage/Evaluate?%s" % params, body, headers)
        response = hconn.getresponse()
        data = response.read()
        
        cursor2 = conn.cursor()
        update_sql = 'update nsfw_server.contributed_image set azure_content_moderator_result = %(data)s where id = %(id)s'
        cursor2.execute(update_sql, {'data': data.decode('utf-8'), 'id': image_id})
        conn.commit()
        cursor2.close()
        print(image_id, url)
    except Exception as e:
        print("Error: {0}".format(e))


cursor.close()
conn.close()
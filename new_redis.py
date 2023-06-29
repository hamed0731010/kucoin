import redis
from redis.commands.json.path import Path
import json
import threading
import  requests


redis_client = redis.Redis(host='localhost', port=6379,decode_responses=True)
try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print("Failed to connect to Redis:", str(e))
db_name=redis_client.config_get('databases')
print(f"Redis Database Name: {db_name}")
print(redis_client.client_info())
def conv(lst1,lst2):
    res={lst1[i]:lst2[i] for i in range(0,len(lst1))}
    return res
async def fetch_store():
    base_url = 'https://api.kucoin.com'
    path = '/api/v1/market/allTickers'
    u = requests.get(base_url + path)
    re = u.json()
    json_str=json.dumps(re)
    redis_client.set('person:1', json_str)


def rate_list():

    base_url = 'https://api.kucoin.com'
    path = '/api/v1/market/allTickers'
    threading.Timer(5.0, rate_list).start()
    u = requests.get(base_url + path)
    re = u.json()
    jn = re['data']['ticker']
    a=[]
    b=[]

    for x in jn:
        a.append(x['symbol'])
        b.append(x['sell'])

    s=conv(a,b)

    redis_client.set('foo', json.dumps(s))






























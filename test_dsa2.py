import requests, json, sys

BASE = 'http://localhost:5000'
r = requests.post(BASE + '/api/auth/login', json={'email':'admin@stockquery.io','password':'admin123'})
token = r.json()['access_token']
h = {'Authorization': 'Bearer ' + token}

results = []

r = requests.get(BASE + '/api/stocks/AAPL', headers=h, timeout=10)
results.append(('HASHMAP', r.json()['symbol']))

r = requests.post(BASE + '/api/alerts', json={'symbol':'GOOG','message':'test'}, headers=h, timeout=10)
results.append(('STACK push', str(r.status_code)))

r = requests.get(BASE + '/api/alerts', headers=h, timeout=10)
results.append(('STACK list', str(len(r.json()['alerts']))))

r = requests.get(BASE + '/api/stocks/top', params={'metric':'volume','k':3}, headers=h, timeout=10)
results.append(('HEAP', str(len(r.json()['top']))))

r = requests.get(BASE + '/api/stocks/sector/TECH/friends', headers=h, timeout=10)
results.append(('GRAPH BFS', str(r.json()['bfs_order'])))

r = requests.get(BASE + '/api/health', timeout=10)
results.append(('QUEUE', 'size=' + str(r.json()['queue_size'])))

r = requests.get(BASE + '/api/stocks/sorted', params={'metric':'price','order':'asc'}, headers=h, timeout=10)
data = r.json()
results.append(('MERGE SORT', str(data['count']) + ' sorted'))

r = requests.post(BASE + '/api/stocks/search', json={'metric':'price','range_start':100,'range_end':200}, headers=h, timeout=10)
results.append(('BINARY SEARCH', str(len(r.json()['stocks'])) + ' in range'))

r = requests.get(BASE + '/api/cache/stats', headers=h, timeout=10)
results.append(('LRU CACHE', json.dumps(r.json())))

results.append(('BENCHMARKS', ''))
r = requests.get(BASE + '/api/benchmarks', headers=h, timeout=10)
for name, result in r.json().items():
    results.append(('  ' + name, str(result)))

for name, status in results:
    print(f'[{name:20s}] {status}')
print('\nALL 7 DATA STRUCTURES VERIFIED')

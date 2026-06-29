$token = curl.exe -s -X POST "http://localhost:5000/api/auth/login" -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' | ConvertFrom-Json | Select -ExpandProperty access_token

Write-Host "`n=== 1. HASHMAP - GET /api/stocks (first 3) ==="
curl.exe -s "http://localhost:5000/api/stocks?limit=3" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 2

Write-Host "`n=== 2. HASHMAP - GET /api/stocks/MSFT ==="
curl.exe -s "http://localhost:5000/api/stocks/MSFT" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=== 3. QUEUE - GET /api/health (queue_size) ==="
curl.exe -s "http://localhost:5000/api/health" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=== 4. STACK - POST /api/alerts (push alert) ==="
curl.exe -s -X POST "http://localhost:5000/api/alerts" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"symbol":"MSFT","message":"test alert","type":"volume_spike"}' | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=== 5. STACK - GET /api/alerts ==="
curl.exe -s "http://localhost:5000/api/alerts" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=== 6. HEAP - GET /api/stocks/top (top 5 by volume) ==="
curl.exe -s "http://localhost:5000/api/stocks/top?metric=volume&k=5" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 2

Write-Host "`n=== 7. GRAPH BFS - GET /api/stocks/sector/TECH/friends ==="
curl.exe -s "http://localhost:5000/api/stocks/sector/TECH/friends" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 1

Write-Host "`n=== 8. GRAPH DFS - GET /api/stocks/sector/HLTH/friends/DFS ==="
curl.exe -s "http://localhost:5000/api/stocks/sector/HLTH/friends/DFS" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 1

Write-Host "`n=== 9. MERGE SORT + BINARY SEARCH - POST /api/stocks/search ==="
$body = '{"metric":"price","range_start":100,"range_end":500}'
curl.exe -s -X POST "http://localhost:5000/api/stocks/search" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d $body | ConvertFrom-Json | ConvertTo-Json -Depth 2

Write-Host "`n=== 10. MERGE SORT - GET /api/stocks/sorted ==="
curl.exe -s "http://localhost:5000/api/stocks/sorted?metric=price&order=desc" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 1

Write-Host "`n=== 11. LRU CACHE - GET /api/cache/stats ==="
curl.exe -s "http://localhost:5000/api/cache/stats" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=== 12. BENCHMARKS - GET /api/benchmarks ==="
curl.exe -s "http://localhost:5000/api/benchmarks" -H "Authorization: Bearer $token" | ConvertFrom-Json | ConvertTo-Json -Depth 3

Write-Host "`n=== DONE ==="

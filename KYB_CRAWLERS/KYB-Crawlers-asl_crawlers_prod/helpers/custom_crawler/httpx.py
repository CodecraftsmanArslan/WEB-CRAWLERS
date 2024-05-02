import time
import httpx
async def fetch_data(corporate__url, headers={} ,payload=None, method='GET' , max_retries=3 , retry=None):
    for _ in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                if method == 'POST' :
                    response = await client.post(corporate__url, json=payload, headers=headers, timeout=10.0)
                else : 
                    response = await client.get(corporate__url, json=payload, headers=headers, timeout=10.0)
                print(response.status_code)
                end_time = end_time = time.time()
                print(end_time - start_time)
                return response
        except httpx.ConnectTimeout:
            time.sleep(retry)
            print("Connection timeout, retrying...")
    return None
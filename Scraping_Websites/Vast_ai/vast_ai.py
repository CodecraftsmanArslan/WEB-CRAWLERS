import requests
import pandas as pd
import json

for i in range(0,20):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer null',
        'cookie': '_gcl_au=1.1.1274043109.1713718716; initialTrafficSource=utmcsr=(direct)|utmcmd=(none)|utmccn=(not set); _ga=GA1.1.1607651459.1713718717; G_ENABLED_IDPS=google; _fbp=fb.1.1713718720451.415723749; __stripe_mid=e1395717-4997-4515-8d06-48dfe01b85efc03188; _hjSessionUser_3469678=eyJpZCI6ImU4NDBiN2ZkLWNjNjktNTI1MS1hYWQ4LWU2NmZlMDU3YzRiNCIsImNyZWF0ZWQiOjE3MTM3MTg3MTk0NjgsImV4aXN0aW5nIjp0cnVlfQ==; __utmzzses=1; _hjSession_3469678=eyJpZCI6ImJkMDVkNjAwLWRmNzAtNDBlZC1hNGM5LTE1M2NjOTdmNmZkNiIsImMiOjE3MTM5NDk3MzQ3MzksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _clck=1x83c5e%7C2%7Cfl7%7C0%7C1572; crisp-client%2Fsession%2F734d7b1a-86fc-470d-b60a-f6d4840573ae=session_97f50d1d-9a26-4afc-94c3-86cdfe22fd0c; _clsk=1yeno77%7C1713949737223%7C1%7C1%7Cd.clarity.ms%2Fcollect; __stripe_sid=38d024ac-b458-4662-bf99-6be24511e834522513; _ga_DG15WC8WXG=GS1.1.1713949734.4.1.1713949995.58.0.0; _uetsid=981070a001a811efbe14f1b7f025e0fa; _uetvid=6659b320000011efb10643a84f0eecf9; ph_phc_IpENMLa90nPaSlnqPjGC9skNndps5CBXz5PaugV4Li8_posthog=%7B%22distinct_id%22%3A%22018f0198-75b6-7326-9660-73503a34e987%22%2C%22%24sesid%22%3A%5B1713949995498%2C%22018f0f5d-7863-78f6-bdda-33e83368e5f1%22%2C1713949735010%5D%7D',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    params = {
        'q': '{"disk_space":{"gte":16},"duration":{"gte":262144},"verified":{"eq":true},"rentable":{"eq":true},"sort_option":{"0":["score","desc"]},"order":[["score","desc"]],"num_gpus":{"gte":0,"lte":18},"allocated_storage":16,"limit":' + str(64 * (i + 1)) + ',"extra_ids":[],"type":"ask"}',
    }
    print("limit:", str(64 * (i + 1)))

    while True:
        response = requests.get('https://cloud.vast.ai/api/v0/bundles/', params=params, headers=headers)

        if response.status_code == 200:
            break
        else:
            print("Retrying to get response")

    # Now you can use the response object
    response = response.json()

    data_list = []

    offer_info = response['offers']
    for offer in offer_info:
        id=offer['id']
        cpu_name = offer['cpu_name']
        gpu_name = offer['gpu_name']
        disk_name=offer['disk_name']
        avx = offer['num_gpus']
        port=offer['direct_port_count']
        motherboard=offer['mobo_name']
        location = offer['geolocation']
        price = offer['dph_total']
        rounded_price = round(price, 3)

        offer_dict = {
            'id':id,
            'cpu_name': cpu_name,
            'type': gpu_name,
            'number': avx,
            'port':port,
            'motherboard':motherboard,
            'disk':disk_name,
            'location': location,
            'price': f"${rounded_price}/hr"
        }

        data_list.append(offer_dict)

    df=pd.DataFrame(data_list)
    df.to_csv('vast_ai_1.csv',index=False)



    
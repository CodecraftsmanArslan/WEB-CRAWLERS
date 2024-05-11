import requests
import m3u8


url = "https://www.udemy.com/assets/8851920/files/898082/8851920/2017-06-30_22-31-48-00afeddecf63055b0d97db244acbe780/1/hls/AVC_1280x720_800k_AAC-HE_64k/aa0024fa611068b9f11f30bfc967d33d307f.m3u8?provider=cloudfront&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiODk4MDgyLzg4NTE5MjAvMjAxNy0wNi0zMF8yMi0zMS00OC0wMGFmZWRkZWNmNjMwNTViMGQ5N2RiMjQ0YWNiZTc4MC8xLyIsImV4cCI6MTcxMzgyMzc5M30._tVpH6C3icnZ5dPWFEFMC3O6CQmkOKnsy5kzNL7917w&v=1"
r = requests.get(url)

playlist = m3u8.loads(r.text)
with open("video.ts", "wb") as f:
    for segment in playlist.data['segments']:
        url=segment['uri']
        r=requests.get(url)
        f.write(r.content)











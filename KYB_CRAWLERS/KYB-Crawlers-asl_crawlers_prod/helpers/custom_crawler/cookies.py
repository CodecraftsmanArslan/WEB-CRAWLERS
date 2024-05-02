"""Import required libraries"""
from tkinter import N
from urllib import response
import requests


# Dynamic GET request
def send_get_request(url):
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response

# Dynamic POST request
def send_post_request(url, body):
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    response = requests.post(url,body, headers=headers,)
    return response

# Get cookies from request
def get_cookies_from_request(method,url, body=""):

    if method == 'GET':
        response = send_get_request(url)
    else:
        response = send_post_request(url, body)
    
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
    set_cookie_header = response.headers.get("Set-Cookie")

    if set_cookie_header is not None:
        header_cookie = set_cookie_header.split(';')[0]
        if header_cookie is not None:
            key_value= header_cookie.split('=')
            if key_value[1] not in cookies_dict:
                cookies_dict[key_value[0]] = key_value[1]

    return cookies_dict


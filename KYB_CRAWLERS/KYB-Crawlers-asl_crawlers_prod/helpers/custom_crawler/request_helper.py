"""Import requried packages"""
import requests
import time
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv
from SlackNotifyKYB import SlackNotifier
from proxies_list import PROXIES

load_dotenv()

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
notify:SlackNotifier=None
def make_request(url, method="GET", params=None, data=None, headers=headers, timeout=60, max_retries=3, retry_interval=60, proxy=False, json=None,verify=True):
    """
    Makes an HTTP request with retries and error handling.
    @param:url (str): The URL to make the request to.
    @param: method (str, optional): The HTTP method to use (default is "GET").
    @param: params (dict, optional): The parameters to include in the request (default is None).
    @param: data (dict, optional): The data to include in the request body (default is None).
    @param: headers (dict, optional): The headers to include in the request (default is None).
    @param: timeout (int, optional): The timeout for the request in seconds (default is 60).
    @param: max_retries (int, optional): The maximum number of retries (default is 3).
    @param: retry_interval (int, optional): The interval between retries in seconds (default is 60).
    @param: notify (object, optional): The notifier object to send notifications (default is None).
    @return object: The response object if the request is successful, otherwise None.
    """
    global notify
    response = None
    for retry in range(max_retries):
        try:
            if proxy:
                for proxy in PROXIES:
                    host, port, username, password = proxy.split(':')
                    proxies = {
                        'http': f'http://{username}:{password}@{host}:{port}',
                        'https': f'http://{username}:{password}@{host}:{port}',
                    }
                    try:
                        response = requests.request(method, url, params=params, data=data, headers=headers,
                            proxies=proxies,json=json,
                            timeout=timeout,verify=verify)
                        return response
                    except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}")
                        continue
                return response
            else:
                try:
                    # Send the HTTP request
                    response = requests.request(method, url, params=params, data=data, headers=headers, timeout=timeout, json=json, verify=verify)
                    return response
                except:
                    pass

        except RequestException as e:
            time.sleep(retry_interval)
            print(f'Request failed. Retrying ({retry+1}/{max_retries})...')
            notify.notify({
                "event": "fail",
                "message": f"Request failed on URL {url}\nError Message: {e}"
            })
        
        if retry+1 == max_retries:
            print(f'Failed to make request after {max_retries} retries.')
            return None

def create_requests_session() -> requests.Session:
    s = requests.Session()
    return s

def setup_notify(notifier_obj: SlackNotifier):
    global notify
    notify = notifier_obj
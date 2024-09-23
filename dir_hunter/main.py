
from datetime import datetime
import threading
import requests
import time
import sys
import os


def path(x):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), x)


TIMEOUT = 3
PAYLOADS_FILE = "../data/dir_list/common-dir-1.txt"
PAYLOADS_PATH = path(PAYLOADS_FILE)

http_responses = [
    {"code": 200, "message": "OK"},
    {"code": 301, "message": "Moved Permanently"},
    {"code": 302, "message": "Found"},
    {"code": 403, "message": "Forbidden"},
    {"code": 404, "message": "Not Found"},
    {"code": 500, "message": "Internal Server Error"},
    {"code": 502, "message": "Bad Gateway"},
    {"code": 503, "message": "Service Unavailable"},
    {"code": 401, "message": "Unauthorized"},
    {"code": 429, "message": "Too Many Requests"},
    {"code": 418, "message": "I'm a teapot"},
    {"code": 307, "message": "Temporary Redirect"},
    {"code": 308, "message": "Permanent Redirect"}
]

ignore_codes = [404, 429]
response_codes = [response['code'] for response in http_responses if response['code'] not in ignore_codes]

def get_time():
	current_time = datetime.now().strftime('%m-%d-%Y %I:%M:%S%p')
	return current_time

def check_directory(url, payload):
	new_url = f"{url}/{payload}"
	try:
		response = requests.get(new_url, timeout=TIMEOUT)
		if response.status_code in response_codes:
			print(f"[+] /{payload:<15}{response.status_code}")
		else:
			print(f"trying /{payload}{' '*15}", end="\r")
	except requests.exceptions.RequestException:
		print(f"trying /{payload}{' '*15}", end="\r")

def worker(url, payloads):
	for payload in payloads:
		check_directory(url, payload)

def main():
	args = sys.argv[1:]
	url = args[0]

	with open(PAYLOADS_PATH) as file:
		payloads = [i.strip() for i in file.readlines()]

	worker(url, payloads)

if __name__ == "__main__":
	main()

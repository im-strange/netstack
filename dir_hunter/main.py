
from datetime import datetime
from tqdm import tqdm
import configparser
import threading
import argparse
import requests
import time
import sys
import os


def get_time():
	current_time = datetime.now().strftime('%m-%d-%Y %I:%M:%S%p')
	return current_time

class Scanner:
	def __init__(self, config_file, url, wordlist=None):
		self.name = "main"
		self.url = url
		self.lock = threading.Lock()

		self.config = configparser.ConfigParser()
		self.config.read(config_file)

		# load configuration settings
		self.wordlist = self.config.get("files", "wordlist_path") if not wordlist else wordlist
		self.connection_timeout = int(self.config.get("settings", "connection_timeout"))
		self.read_timeout = int(self.config.get("settings", "read_timeout"))
		self.thread_count = self.config.get("settings", "thread_count")
		self.verbose = self.config.getboolean("settings", "verbose")
		self.output_file = self.config.get("settings", "output_file")
		self.timeout = (self.connection_timeout, self.read_timeout)
		self.status_codes = [int(code) for code in self.config.get("settings", "status_codes").split(',')]

	# display settings
	def display_settings(self):
		print(f"\n[{get_time()}] scan started")
		print(f"{' '*4}* target_url     : {self.url}")
		print(f"{' '*4}* wordlist       : {self.wordlist}")
		print(f"{' '*4}* status_codes   : {self.status_codes}")
		print(f"{' '*4}* verbose        : {self.verbose}")
		print()

	# main scan function
	def scan(self):
		# check if wordlist exists
		if not os.path.exists(self.wordlist):
			print(f"[{self.name}] wordlist file not found: {self.wordlist}")
			exit(2)

		# read
		with open(self.wordlist) as file:
			wordlist = file.read().splitlines()

		# results
		results = []
		threads = []

		# call make_request() function for each word
		for word in wordlist:
			url = f"{self.url}{word}" if self.url.endswith("/") else f"{self.url}/{word}"
			thread = threading.Thread(target=self.make_request, args=(url, results))
			thread.daemon = True
			threads.append(thread)
			thread.start()

		# join threads
		for thread in threads:
			thread.join()

		# save results
		self.save_results(results)


	# request with the custom url
	def make_request(self, url, results):
		try:
			print(f"\r\033[K[{self.name}] trying {url}", end="\r")
			response = requests.get(url, timeout=self.timeout)

			if response.status_code in self.status_codes:
				with self.lock:
					results.append((get_time(), url, response.status_code))
				print(f"[{response.status_code}] {url}")

		except requests.exceptions.Timeout:
			if self.verbose:
				print(f"[{self.name}] request timed out for: {url}")

		except requests.exceptions.RequestException as e:
			if self.verbose:
				print(f"[{self.name}] error for {url}: {e}")


	# save results to a file
	def save_results(self, results):
		if len(results) >= 1:
			with open(self.output_file, "a") as file:
				for time, url, status in results:
					file.write(f"[{time}] {url} - {status}\n")
			print(f"\r\033[K[{self.name}] results saved to {self.output_file}")
		else:
			print(f"\r\033[K[{self.name}] no directory found from '{self.wordlist}' to target site")

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


def main():
	# get the name and basename
	filename = os.path.basename(__file__)
	basename = filename.split(".")[0]

	# custom argument parser
	class CustomArgumentParser(argparse.ArgumentParser):
		def print_help(self):
			lines = [
				f"usage: python {filename} <url> [OPTIONS]"
			]
			for line in lines:
				print(line)

		def error(self, message):
			print(f"[{basename}] {message}")
			exit(2)

	# add arguments
	parser = CustomArgumentParser()
	parser.add_argument("-u", "--url", required=True)
	parser.add_argument("-w", "--wordlist", required=True)

	# get the given arguments
	args = parser.parse_args()
	url = args.url
	wordlist = args.wordlist

	# start
	config_file = "script.conf"
	scanner = Scanner(config_file, url, wordlist=wordlist)
	scanner.display_settings()
	scanner.scan()


# main function
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print(f"\r\033[K[info] stopped")

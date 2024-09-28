
try:
	from datetime import datetime
	from tqdm import tqdm
	import configparser
	import threading
	import argparse
	import requests
	import time
	import sys
	import os

except ModuleNotFoundError as e:
	print(f"[main] {e}")
	exit(2)

# colors
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
GRAY = '\033[90m'
RESET = '\033[0m'

# get current time
def get_time():
	current_time = datetime.now().strftime('%m-%d-%Y %I:%M:%S%p')
	return current_time

class Scanner:
	def __init__(self, config_file, url, wordlist=None):
		self.name = "main"
		self.url = url
		self.lock = threading.Lock()
		self.results_lock = threading.Lock()

		# open config file
		self.config = configparser.ConfigParser()
		self.config.read(config_file)

		# load configuration settings
		self.wordlist = self.config.get("files", "wordlist_path") if not wordlist else wordlist
		self.connection_timeout = int(self.config.get("settings", "connection_timeout"))
		self.read_timeout = int(self.config.get("settings", "read_timeout"))
		self.thread_count = int(self.config.get("settings", "thread_count"))
		self.verbose = self.config.getboolean("settings", "verbose")
		self.output_file = self.config.get("settings", "output_file")
		self.timeout = (self.connection_timeout, self.read_timeout)
		self.status_codes = [int(code.strip()) for code in self.config.get("settings", "status_codes").split(',')]
		self.sleep_time = float(self.config.get("settings", "sleep_time"))
		self.counter = 0

	# display settings
	def display_settings(self):
		print(f"\n{GRAY}[{YELLOW}{get_time()}{GRAY}]{RESET} scan started")
		print(f"{' '*4}[+] status_codes : {','.join(str(num) for num in self.status_codes)}")
		print(f"{' '*4}[+] target_url   : {self.url}")
		print(f"{' '*4}[+] wordlist     : {self.wordlist}")
		print(f"{' '*4}[+] verbose      : {self.verbose}")
		print(f"{' '*4}[+] thread       : {self.thread_count}")
		print(f"{' '*4}[+] output       : {self.output_file}")
		print(f"{' '*4}[+] sleep_time   : {self.sleep_time}")
		print()

	# thread worker
	def thread_worker(self, payloads, results):
		for payload in payloads:
			self.make_request(payload, results)

			with self.lock:
				self.counter += 1

			#  wait before sending another request
			time.sleep(self.sleep_time)

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

		total_lines = len(wordlist)
		chunk_size = len(wordlist) // self.thread_count

		# call make_request() function for each word
		for i in range(self.thread_count):
			start = i * chunk_size
			end = None if i == (self.thread_count - 1) else (i + 1) * chunk_size
			payload_range = wordlist[start:end]

			thread = threading.Thread(target=self.thread_worker, args=(payload_range, results))
			thread.daemon = True
			threads.append(thread)
			thread.start()

		while any(thread.is_alive() for thread in threads):
			with self.lock:
				progress = round((self.counter / total_lines) * 100, 2)
				print(f"\r\033[K{GRAY}[{YELLOW}{self.counter}/{len(wordlist)}{GRAY}]{RESET} scanning {progress}%", end="\r")

		print(f"\r\033[K{GRAY}[{YELLOW}{get_time()}{GRAY}]{RESET} Finished")

		# join threads
		for thread in threads:
			thread.join()

		# save results
		self.save_results(results)


	# request with the custom url
	def make_request(self, payload, results):
		url = f"{self.url}{payload}" if self.url.endswith("/") else f"{self.url}/{payload}"
		try:
			response = requests.get(url, timeout=self.timeout)

			if response.status_code in self.status_codes:
				with self.results_lock:
					results.append((get_time(), url, response.status_code))
				print(f"\r\r\r\r\r{GRAY}[{GREEN}{response.status_code}{GRAY}] {BLUE}{url}{RESET}")

		except requests.exceptions.Timeout:
			if self.verbose:
				print(f"\r\r\r\r\r[{self.name}] request timed out for: {url}")

		except requests.exceptions.RequestException as e:
			if self.verbose:
				print(f"\r\r\r\r\r[{self.name}] trying {url} - host is down")


	# save results to a file
	def save_results(self, results):
		if len(results) >= 1:
			with open(self.output_file, "a") as file:
				for time, url, status in results:
					file.write(f"[{time}] {url} - {status}\n")
			print()
			print(f"\r\033[K[{self.name}] results saved to {self.output_file}")
		else:
			print()
			print(f"\r\033[K[{self.name}] no directory found from '{self.wordlist}' to target site")


# typewrite animation
def type(words, speed=0.005):
	for letter in words:
		print(letter, end="", flush=True)
		time.sleep(speed)
	print()


# main function to call
def main():
	# get the name and basename
	filename = os.path.basename(__file__)
	basename = filename.split(".")[0]

	# custom argument parser
	class CustomArgumentParser(argparse.ArgumentParser):
		def print_help(self):
			tabsize = 2
			lines = [
				f"usage: python {filename} <url> [OPTIONS]",
				f"\npositional arguments:",
				f"{' '*tabsize}{'-w, --wordlist':<15} wordlist path [default=dir_list/list1.txt]",
				f"{' '*tabsize}{'-u, --url':<15} target url",
				f"\noptional arguments:",
				f"{' '*tabsize}{'-s, --status':<15} target status code",
				f"{' '*tabsize}{'-t, --threads':<15} thread count [default=5]",
				f"{' '*tabsize}{'-o, --output':<15} output file [default=results.txt]",
				f"{' '*tabsize}{'--sleep':<15} delay before next request [default=0.2]",
				f"\nexamples:",
				f"{' '*tabsize}python {filename} -u https://example.com -w mywordlist.txt",
				f"{' '*tabsize}python {filename} -u http://localhost:5000/ -t 1 -s 200,201,202,203",
				f"{' '*tabsize}python {filename} -u https://example.com -o output.txt"
			]
			for line in lines:
				print(line)
				time.sleep(0.05)

		def error(self, message):
			type(f"[{basename}] {message}")
			type(f"[{basename}] see '--help' for more info")
			exit(2)

	# add arguments
	parser = CustomArgumentParser()
	parser.add_argument("-u", "--url", required=True)
	parser.add_argument("-w", "--wordlist", default="dir_list/list1.txt")
	parser.add_argument("-s", "--status")
	parser.add_argument("-t", "--threads", type=int)
	parser.add_argument("-o", "--output")
	parser.add_argument("--sleep", type=float)
	parser.add_argument("--verbose", action="store_true")

	# get the given arguments
	args = parser.parse_args()
	url = args.url
	wordlist = args.wordlist

	# start
	config_file = "script.conf"
	scanner = Scanner(config_file, url, wordlist=wordlist)

	if args.status:
		try:
			scanner.status_codes = list(map(int, args.status.split(",")))
		except ValueError:
			type(f"[{scanner.name}] invalid value given for --status-code: '{args.status}'")
			type(f"[{scanner.name}] must be single or comma-separated integer")
			exit(2)

	if args.threads: scanner.thread_count = args.threads
	if args.output: scanner.output_file = args.output
	if args.sleep: scanner.sleep_time = args.sleep
	if args.verbose: scanner.verbose = True

	scanner.display_settings()
	scanner.scan()
	print()


# main function
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print(f"\r\033[K[info] stopped")
	except OSError:
		print(f"\r\033[K[info] too many open files, exiting..")

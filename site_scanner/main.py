
from bs4 import BeautifulSoup
import argparse
import requests
import time
import sys
import os

# check status code
def check_status_code(url):
	try:
		response = requests.get(url)
		print(f"[info] link is accessible")
		print(f"{' '*4}* URL: {url}")
		print(f"{' '*4}* status: {response.status_code}")
		return True

	except requests.RequestException as e:
		print(f"[info] error accessing url: {e}")
		exit(2)


# get all the links from a url
def extract_links(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")

	a_tags = soup.find_all("a", href=True)
	print(f"[info] {len(a_tags)} links found")

	links = []
	for a_tag in a_tags:
		links.append(a_tag["href"])

	for link in links:
		time.sleep(0.01)
		print(f"{' '*4}* {link}")


# extract meta and title
def extract_meta_and_title(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")

	title = soup.title.string if soup.title else "no title found"
	meta_tags = soup.find_all("meta")

	print(f"[info] title: {title}")

	for meta in meta_tags:
		time.sleep(0.01)
		print(f"{' '*4}* {meta.attrs}")


# extract headers
def get_headers(url):
	response = requests.get(url)
	headers = response.headers

	longest_key = max([len(key) for key, val in headers.items()])

	print(f"[info] headers:")
	for key, val in headers.items():
		print(f"{' '*4}* {key:<{longest_key+5}} {val}")


# check for forms
def check_forms(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	forms = soup.find_all("form")

	print(f"[info] {len(forms)} forms found")
	for form in forms:
		print(f"form {forms.index(form)}:")
		print(f"{' '*4}action: {form.get('action')}")
		print(f"{' '*4}method: {form.get('method')}")

		inputs = form.find_all("input")
		for input_field in inputs:
			name = input_field.get('name')
			type = input_field.get('type')
			print(f"{' '*4}name: {name if name else 'None':<15} type: {type if type else 'None'}")


# check for redirect
def check_redirect(url):
	response = requests.get(url, allow_redirects=True)
	if response.history:
		print(f"[info] redirect detected. final url: {response.url}")
	else:
		print(f"[info] no redirect detected")


def breakline(n=50):
	print("="*n)

# main function to call
def main():
	filename = os.path.basename(__file__)
	basename = filename.split('.')[0]

	# custom argument parser
	class CustomArgumentParser(argparse.ArgumentParser):
		def print_help(self):
			lines = [
				f"usage: python {filename} <url> [OPTIONS]",
				f"\narguments & options:",
				f"{' '*4}{'url':<15} target link",
				f"{' '*4}{'--links':<15} extract links",
				f"{' '*4}{'--meta':<15} extract title and meta",
				f"{' '*4}{'--check':<15} check status code",
				f"{' '*4}{'--headers':<15} check headers",
				f"{' '*4}{'--forms':<15} check for forms",
				f"{' '*4}{'--redirect':<15} check for redirect"
			]
			for line in lines:
				print(line)

		def error(self, message):
			print(f"[{basename}] {message}")
			print(f"[{basename}] try '--help' for manual")
			exit(2)

	# parser
	parser = CustomArgumentParser()
	parser.add_argument("url")
	parser.add_argument("--links", action="store_true")
	parser.add_argument("--meta", action="store_true")
	parser.add_argument("--headers", action="store_true")
	parser.add_argument("--forms", action="store_true")
	parser.add_argument("--redirect", action="store_true")

	# given arguments
	args = parser.parse_args()
	url = args.url

	check_status_code(url)

	if args.links:
		breakline()
		extract_links(url)

	if args.meta:
		breakline()
		extract_meta_and_title(url)

	if args.headers:
		breakline()
		get_headers(url)

	if args.forms:
		breakline()
		check_forms(url)

	if args.redirect:
		breakline()
		check_redirect(url)

	if len(sys.argv) > 2:
		breakline()

# main
if __name__ == "__main__":
	# run the main function
	try:
		main()

	# if interrupted by user
	except KeyboardInterrupt:
		print(f"[::] stopped")
		exit()


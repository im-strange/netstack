
from tqdm import tqdm
import configparser
import threading
import argparse
import socket
import socks
import json
import time
import sys
import os


# returns the current path
def path(x):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), x)


CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

REF_FILE = path(config["settings"]["port_services_file"])
TIMEOUT = int(config["settings"]["timeout_per_connect"])

try:
	with open(REF_FILE) as file:
		service_names = json.load(file)
except FileNotFoundError:
	print(f"[info] file for port service names not found")


# returns the service name of a port
def get_service_name(ports):
	names = []
	for port in ports:
		name = service_names.get(str(port))
		if name:
			names.append([port, name])
		else:
			names.append([port, "unknown service"])
	return names


# get ip from a domain
def get_ip(domain):
	try:
		ip_addr = socket.gethostbyname(domain)
		return ip_addr
	except socket.gaierror as e:
		return None


# returns a list of target port based on port_str
def parse_port(port_str):
	# if range
	if "-" in port_str:
		pattern = port_str.split("-")
		start_port, end_port = int(pattern[0]), int(pattern[1])
		port_list = list(range(start_port, end_port + 1))
		return port_list

	# if list
	elif "," in port_str:
		port_list = [int(port) for port in port_str.split(",")]
		return port_list

	# else, it must be a single port
	else:
		return [int(port_str)]


# scan a single port
def scan_port(ip, port, open_ports):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.settimeout(TIMEOUT)
			result = sock.connect((ip, port))
			open_ports.append(port)
	except (socket.timeout, socket.error, ConnectionRefusedError):
		pass


# scan multiple ports
def scan_ports(ip, ports):
	open_ports = []
	threads = []
	for port in tqdm(ports, leave=False):
		thread = threading.Thread(target=scan_port, args=(ip, port, open_ports,))
		thread.daemon = True
		threads.append(thread)
		thread.start()
	for thread in threads:
		thread.join()
	return open_ports


# display infos
def display_settings():
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	REF_FILE = path(config["settings"]["port_services_file"])
	TIMEOUT = int(config["settings"]["timeout_per_connect"])

	print()
	print(f"[+] ref_file : {REF_FILE}")
	print(f"[+] timeout  : {TIMEOUT}")
	print()


# display the result
def display_result(ip, target_ports, open_ports):
	if len(open_ports) > 0:
		print(f"{' '*4}{'PORT':<10}SERVICE")
		port_service_names = get_service_name(open_ports)
		for open_port in port_service_names:
			print(f"{' '*4}{open_port[0]:<10}{open_port[1]}")
			time.sleep(0.01)
	print()


# redirect socket to tor
def set_tor_proxy():
	socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 9050)
	socket.socket = socks.socksocket


# main function to call
def main():
	filename = os.path.basename(__file__)
	class CustomArgumentParser(argparse.ArgumentParser):
		def print_help(self):
			lines = [
				f"usage: python {filename} <host> [OPTIONS]",
				f"\narguments & options:",
				f"{' '*4}{'host':<15} target host/s",
				f"{' '*4}{'-p, --port':<15} target port/s [default=1-1000]",
				f"{' '*4}{'-d, --domain':<15} enable domain scanning",
				f"{' '*4}{'-v, --verbose':<15} print scanning info",
				f"{' '*4}{'-t, --tor':<15} set tor proxy",
				f"\nexamples:",
				f"{' '*4}python {filename} localhost -p 1-10000",
				f"{' '*4}python {filename} google.com,example.com --port 443,80"
			]
			for line in lines:
				print(line)

		def error(self, message):
			print(f"[{filename.split('.')[0]}] {message}")
			print(f"[{filename.split('.')[0]}] see '--help' for manual")
			exit(2)

	parser = CustomArgumentParser()
	parser.add_argument("target")
	parser.add_argument("-p", "--port", default="1-1000")
	parser.add_argument("-d", "--domain", action="store_true")
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-t", "--tor", action="store_true")

	args = parser.parse_args()
	hosts = args.target.split(",")
	ports = parse_port(args.port)

	if args.verbose:
		display_settings()

	if args.tor:
		set_tor_proxy()

	for host in hosts:
		if args.domain:
			ip_addr = get_ip(host)
			if ip_addr:
				result = scan_ports(host, ports)
				print(f"\n[info] {len(result)}/{len(ports)} were found open @{ip_addr}:")
				display_result(host, ports, result)
			else:
				print(f"[info] error fetching host's ip")
				exit(2)

		else:
			result = scan_ports(host, ports)
			print(f"\n[info] {len(result)}/{len(ports)} were found open @{host}:")
			display_result(host, ports, result)


if __name__ == "__main__":
	main()

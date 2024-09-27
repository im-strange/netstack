
import configparser
import requests
import time
import sys
import os


# check needed files if existing
def check_files(file_list):
	missing_files = []

	for file_path in file_list:
		if not os.path.exists(file_path):
			missing_files.append(file_path)

	if missing_files:
		print(f"[info] missing file/directory detected")
		for file in missing_files:
			print(f"{' '*4}* {file}")

	else:
		print(f"[info] all files and directories exist")
		for file in file_list:
			print(f"{' '*4}* {file}")


# read info in config file
def read_config(config_file):
	config = configparser.ConfigParser()
	config.read(config_file)

	payloads_dir = config.get("files", "payloads_dir")
	return payloads_dir


# print all values in config
def print_config(config_file):
	config = configparser.ConfigParser()
	config.read(config_file)

	for section in config.sections():
		print(f"[{section}]")
		for key, val in config.items(section):
			print(f"{' '*4}{key} -> {val}")

# modify config
def modify_config(config_file, section, key, new_value):
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	if config.has_section(section):
		config.set(section, key, new_value)
		print(f"[info] updated {key} to {new_value} in section {section}")

	else:
		print(f"[info] section {section} does not exist")
		exit(2)


# check if the site is vulnerable with payload
def try_payload(url, payload):
	pass


# main function to call
def main():
	used_files = [
		"config.ini"
	]

	check_files(used_files)


# main
if __name__ == "__main__":
	main()

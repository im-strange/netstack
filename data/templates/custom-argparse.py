
import argparse

class CustomArgumentParser(argparse.ArgumentParser):
	def print_help(self):
		lines = [
			f"usage: "
		]
		for line in lines:
			print(line)

	def error(self, message):
		print(message)
		exit(2)

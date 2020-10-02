import logging
import os
import subprocess


# === Echo Control =============================================================

class Echo:
def off():
	subprocess.run(['stty', '-echo'], check=True)
def on():
	subprocess.run(['stty', 'echo'], check=True)
def clear():
	subprocess.call('clear' if os.name == 'posix' else 'cls')



# === Printing & Logging ======================================================

logging.basicConfig(filename='/home/pi/logs/camera.timelapse.log', level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
class Console:
	def print(message, prefix = ' ', suffix = ' '):
		print(str(prefix) + str(message) + str(suffix)) 
	def log(message, prefix = ' ', suffix = ' '):
		print('\033[94m' + str(prefix) + str(message) + str(suffix)+ '\033[0m')
		logging.info(str(message))
	def debug(message, prefix = ' ', suffix = ' '):
		print(str(prefix) + 'DEBUG: ' + str(message) + str(suffix))
		logging.debug(str(message))
	def info(message, prefix = ' ', suffix = ' '):
		print(str(prefix) + 'INFO: ' + str(message) + str(suffix))
		logging.info(str(message))
	def warn(message, prefix = '\n ', suffix = ' '):
		print('\033[93m' + str(prefix) + 'WARNING: ' + str(message) + str(suffix) + '\033[0m')
		logging.warning(str(message))
	def error(message, prefix = '\n ', suffix = ' '):
		print('\033[91m' + str(prefix) + 'ERROR: ' + str(message) + str(suffix) + '\033[0m')
		logging.error(str(message))
	def critical(message, prefix = '\n ', suffix = '\n '):
		print('\033[91m' + str(prefix) + 'CRITICAL: ' + str(message) + str(suffix) + '\033[0m')
		logging.critical(str(message))
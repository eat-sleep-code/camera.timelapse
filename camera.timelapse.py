from picamera import PiCamera
import ffmpeg
import argparse
import datetime
import subprocess
import threading
import time

version = "2020.08.18"

camera = PiCamera()
camera.resolution = camera.MAX_RESOLUTION


# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--interval', dest='interval', help='Set the timelapse interval')
parser.add_argument('--framerate', dest='framerate', help='Set the output framerate')
parser.add_argument('--renderVideo', dest='renderVideo', help='Set whether a video is generated every 24 hours')
parser.add_argument('--outputFolder', dest='outputFolder', help='Set the folder where images will be saved')
args = parser.parse_args()


interval = args.interval or 60
try:
	interval = int(interval)
except:
	interval = 60


framerate = args.framerate or 60
try:
	framerate = int(framerate)
except:
	framerate = 60

	
renderVideo = args.renderVideo or True
if renderVideo != False
	renderVideo = True

	
outputFolder = args.outputFolder or "dcim/"
if outputFolder.endswith('/') == False:
	outputFolder = outputFolder+"/"


# === Echo Control =============================================================

def echoOff():
	subprocess.run(['stty', '-echo'], check=True)
def echoOn():
	subprocess.run(['stty', 'echo'], check=True)
def clear():
	subprocess.call('clear' if os.name == 'posix' else 'cls')
clear()


# === Functions ================================================================

def getFileName(imageCounter = 1):
	now = datetime.datetime.now()
	datestamp = now.strftime("%Y%m%d")
	extension = ".jpg"
	return datestamp + "-" + str(imageCounter).zfill(8) + extension

# ------------------------------------------------------------------------------

def getFilePath(imageCount = 1):
	try:
		os.makedirs(outputFolder, exist_ok = True)
	except OSError:
		print (" ERROR: Creation of the output folder %s failed." % path)
		echoOn()
		quit()
	else:
		return outputFolder + getFileName(imageCounter)

# ------------------------------------------------------------------------------

def captureTimelapse:
	global interval
	global outputFolder
	for filename in camera.capture_continuous(getFilePath({counter})):	
		time.sleep(interval) #seconds

# ------------------------------------------------------------------------------

def convertSequenceToVideo(dateToConvert):
	global framerate
	global outputFolder
	dateToConvertStamp = dateToConvert.strftime("%Y%m%d")
	output_options = {
		'crf': 20,
		'preset': 'slower',
		'movflags': 'faststart',
		'pix_fmt': 'yuv420p'
	}
	ffmpeg
	.input(outputFolder + dateToConvertStamp +'-*.jpg', pattern_type='glob', framerate=framerate)
	.filter_('deflicker', mode='pm', size=10)
	.filter_('scale', size='hd1080', force_original_aspect_ratio='increase')
	.output(dateToConvertStamp + '.mp4', **output_options)
	.run()	


# === Timelapse Capture ========================================================

try: 

	camera.start_preview(fullscreen=False, resolution=(1920, 1080), window=(0, 0, 1920, 1080))
	time.sleep(2)	

	captureThread = threading.Thread(captureTimelapse, args=(,))
	captureThread.start()

	while renderVideo:
		yesterday = (datetime.date.today() - datetime.timedelta(days = 1))
		yesterdayStamp = yesterday.strftime("%Y%m%d")
		if exists(outputFolder + yesterdayStamp + ".mp4") == False:
			convertThread = threading.Thread(convertSequenceToVideo, args=(yesterday,)
			convertThread.start()
		time.sleep(3600)


except KeyboardInterrupt:
	echoOn()
	sys.exit(1)

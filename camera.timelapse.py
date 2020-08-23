from picamera import PiCamera
import argparse
import datetime
import keyboard
import os
import subprocess
import sys
import threading
import time

version = "2020.08.22"

camera = PiCamera()
#camera.resolution = camera.MAX_RESOLUTION
camera.resolution = (1920, 1080)

# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--interval', dest='interval', help='Set the timelapse interval')
parser.add_argument('--framerate', dest='framerate', help='Set the output framerate')
parser.add_argument('--outputFolder', dest='outputFolder', help='Set the folder where images will be saved')
parser.add_argument('--renderVideo', dest='renderVideo', help='Set whether a video is generated every 24 hours')
parser.add_argument('--uploadVideo', dest='uploadVideo', help='Set whether to automatically upload videos to YouTube')
parser.add_argument('--privacy', dest='privacy', help='If uploading a video, set the privacy of the video')
args = parser.parse_args()


interval = args.interval or 10
try:
	interval = int(interval)
except:
	interval = 60


framerate = args.framerate or 60
try:
	framerate = int(framerate)
except:
	framerate = 60
shutter = int((1/(int(framerate)*2)) * 1000000)
camera.shutter_speed = shutter

	
renderVideo = args.renderVideo or True
if renderVideo != False:
	renderVideo = True
renderingInProgress = False


uploadVideo = args.uploadVideo or False
if renderVideo != True:
	renderVideo = False

outputFolder = args.outputFolder or "dcim/"
if outputFolder.endswith('/') == False:
	outputFolder = outputFolder+"/"

privacy = args.privacy or "public"

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

def getFilePath(imageCounter = 1):
	try:
		os.makedirs(outputFolder, exist_ok = True)
	except OSError:
		print (" ERROR: Creation of the output folder %s failed." % path)
		echoOn()
		quit()
	else:
		return outputFolder + getFileName(imageCounter)

# ------------------------------------------------------------------------------

def captureTimelapse():
	try:
		global interval
		global outputFolder
		started = datetime.datetime.now().strftime("%Y%m%d")
		while True:
			for filename in camera.capture_continuous(getFilePath('{counter:08d}')):				
				if started != datetime.datetime.now().strftime("%Y%m%d"):
					started = datetime.datetime.now().strftime("%Y%m%d")
					break
				else:				
					time.sleep(interval) #seconds
	except: 
		print(' ERROR: Could not capture image. ')

# ------------------------------------------------------------------------------

def convertSequenceToVideo(dateToConvert):
	try:
		global framerate
		global renderingInProgress
		global outputFolder		
		renderingInProgress = True
		dateToConvertStamp = dateToConvert.strftime("%Y%m%d")		
		outputFilePath = dateToConvertStamp + '.mp4'	
		# The following runs out of memory as it is not hardware accelerated, perhaps in the future?
		# subprocess.call('cd ' + outputFolder +  '&& ffmpeg -y -r 60 -i '+dateToConvertStamp+'-%08d.jpg -s hd1080 -vcodec libx265 -crf 20 -preset slow '+ outputFilePath, shell=True)
		# The following is not as an efficient codec, but encoding is hardware accelerated and should work for the transient purposes it is used for.
		subprocess.call('cd ' + outputFolder +  '&& ffmpeg -y -r 60 -i '+dateToConvertStamp+'-%08d.jpg -s hd1080 -qscale:v 3 -vcodec mpeg4 '+ outputFilePath, shell=True)
		renderingInProgress = False
		if uploadVideo: 
			try:		
				print('Uploading video...')	
				uploadDescription = 'Timelapse for ' + dateToConvert.strftime("%Y-%m-%d")
				subprocess.call('python3 camera.timelapse/camera.timelapse.upload.py --file ' + outputFilePath + ' --title ' + dateToConvertStamp + ' --description ' + uploadDescription + ' --privacyStatus ' + privacy + ' --noauth_local_webserver ' , shell=True)
			except Exception as ex:
				print(' WARNING: YouTube upload may have failed! ' + str(ex)) 	
	except ffmpeg.Error as ex:
		print(' ERROR: Could not convert sequence to video.')


# === Timelapse Capture ========================================================

try: 
	os.chdir('/home/pi') 
	#print(camera.shutter_speed)		
	while True:
		if keyboard.is_pressed('ctrl+c') or keyboard.is_pressed('esc'):
			# clear()
			echoOn()
			break

		camera.start_preview(fullscreen=False, resolution=(1920, 1080), window=(60, 60, 640, 360))
		time.sleep(2)	

		captureThread = threading.Thread(target=captureTimelapse)
		captureThread.start()

		while renderVideo:			
			if renderingInProgress == False:
				time.sleep(interval)
				yesterday = (datetime.date.today() - datetime.timedelta(days = 1))
				yesterdayStamp = yesterday.strftime("%Y%m%d")
				firstFrameExists = os.path.exists(outputFolder + yesterdayStamp + '-00000001.jpg')
				videoExists = os.path.exists(outputFolder + yesterdayStamp + '.mp4')
				if firstFrameExists == True and videoExists == False:
					convertThread = threading.Thread(target=convertSequenceToVideo, args=(yesterday,))
					convertThread.start()
					#convertSequenceToVideo(yesterday)
			time.sleep(3600)


except KeyboardInterrupt:
	camera.close()
	echoOn()
	sys.exit(1)

else:
	echoOn()
	sys.exit(0)

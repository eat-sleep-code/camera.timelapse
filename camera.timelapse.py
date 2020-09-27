from picamera import PiCamera
from PIL import Image
import argparse
import datetime
import glob
import fractions
import keyboard
import numpy
import os
import shutil
import statistics
import subprocess
import sys
import threading
import time

version = '2020.09.27'

camera = PiCamera()
#camera.resolution = camera.MAX_RESOLUTION
camera.resolution = (1920, 1080)
camera.sensor_mode = 3
camera.framerate = 1


# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--interval', dest='interval', help='Set the timelapse interval', type=int)
parser.add_argument('--framerate', dest='framerate', help='Set the output framerate', type=int)
parser.add_argument('--rotate', dest='rotate', help='Rotate the camera in 90* increments', type=int)
parser.add_argument('--outputFolder', dest='outputFolder', help='Set the folder where images will be saved', type=str)
parser.add_argument('--retention', dest='retention', help='Set the number of days to locally retain the captured files', type=int)
parser.add_argument('--waitUntilAnalysis', dest='waitUntilAnalysis', help='Set whether to perform an initial analysis', type=bool)
parser.add_argument('--renderVideo', dest='renderVideo', help='Set whether a video is generated every 24 hours', type=bool)
parser.add_argument('--uploadVideo', dest='uploadVideo', help='Set whether to automatically upload videos to YouTube', type=bool)
parser.add_argument('--privacy', dest='privacy', help='Set the privacy status of the YouTube video', type=str)



args = parser.parse_args()


interval = args.interval or 10
try:
	interval = int(interval)
except:
	interval = 10


framerate = args.framerate or 60
try:
	framerate = int(framerate)
except:
	framerate = 60
shutter = int((1/(int(framerate)*2)) * 10000000)
defaultFramerate = 30


rotate = args.rotate or 0
try:
	rotate = int(rotate)
except:
	rotate = 0


retention = args.retention or 7
try: 
	retention = int(retention)
except:
	retention = 7


waitUntilAnalysis = args.waitUntilAnalysis or False
if waitUntilAnalysis != True:
	waitUntilAnalysis = False
	waitUntilAnalysisStatus = -1
else:
	waitUntilAnalysisStatus = 1

renderVideo = args.renderVideo or True
if renderVideo != False:
	renderVideo = True
renderingInProgress = False


uploadVideo = args.uploadVideo or False
if uploadVideo != True:
	uploadVideo = False


outputFolder = args.outputFolder or 'dcim/'
if outputFolder.endswith('/') == False:
	outputFolder = outputFolder+'/'


privacy = args.privacy or 'public'





brightnessThreshold = 125
darknessThreshold = 35


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
	global waitUntilAnalysisStatus

	now = datetime.datetime.now()
	datestamp = now.strftime('%Y%m%d')
	extension = '.jpg'
	if waitUntilAnalysisStatus != -1:
		extension = '~.jpg' 	
	return datestamp + '/' + str(imageCounter).zfill(8) + extension


# ------------------------------------------------------------------------------

def getFilePath(imageCounter = 1):
	now = datetime.datetime.now()
	datestamp = now.strftime('%Y%m%d')
	try:
		os.makedirs(outputFolder, exist_ok = True)
		try:
			os.makedirs(outputFolder + datestamp, exist_ok = True)
		except OSError:
			print ('\n ERROR: Creation of the output folder ' + outputFolder + datestamp + ' failed!' )
			echoOn()
			quit()
	except OSError:
		print ('\n ERROR: Creation of the output folder ' + outputFolder + ' failed!' )
		echoOn()
		quit()
	else:
		return outputFolder + getFileName(imageCounter)

# ------------------------------------------------------------------------------

def captureTimelapse():
	try:
		global interval
		global outputFolder
		global waitUntilAnalysisStatus

		started = datetime.datetime.now().strftime('%Y%m%d')

		# Set counter start based on last image taken today (allows multiple distinct sequences to be taken in one day)
		try:
			latestImagePath = max(glob.iglob(outputFolder + started + '/*.jpg'),key=os.path.getmtime)
			counter = int(latestImagePath.replace(outputFolder + started + '/', '').replace('.jpg', '')) + 1
		except:
			counter = 1
			pass

		preAnalysisCounter = counter
		
		print(' INFO: Starting timelapse sequence at an interval of ' + str(interval) + ' seconds...')		
		while True:
			if waitUntilAnalysisStatus == 0:
				waitUntilAnalysisStatus = -1
				counter = preAnalysisCounter 
				
			if started != datetime.datetime.now().strftime('%Y%m%d'):
				# It is a new day, reset the counter
				started = datetime.datetime.now().strftime('%Y%m%d')
				counter = 1
			
			camera.capture(getFilePath(counter))
			counter += 1					
			time.sleep(interval)
	except Exception as ex: 
		print('\n WARNING: Could not capture most recent image. ' + str(ex))
		


# ------------------------------------------------------------------------------

def analyzeLastImages():
	global interval
	global framerate
	global waitUntilAnalysisStatus
 	
	try:
		time.sleep(interval * 1.5) 
		print('\n INFO: Starting image analysis... ')
		measuredBrightnessList = []
		
		while True:	
			try:
				started = datetime.datetime.now().strftime('%Y%m%d')

				latestImagePath = max(glob.iglob(outputFolder + started + '/*.jpg'),key=os.path.getmtime)
				latestImage = Image.open(latestImagePath)
				measuredBrightness = numpy.mean(latestImage)
				measuredBrightnessList.append(float(measuredBrightness))
				if len(measuredBrightnessList) >= (framerate * 0.25):
					measuredAverageBrightness = statistics.mean(measuredBrightnessList)
					print(' INFO: Average brightness of ' + str(int(framerate * 0.25)) + ' recent images: ' + str(measuredAverageBrightness))
					if waitUntilAnalysisStatus == 1:
						print(' INFO: Removing files created during initial analysis... ')
						waitUntilAnalysisStatus = 0
						for analysisFile in glob.iglob(outputFolder + started + '/*~.jpg'):
							os.remove(analysisFile)
					if measuredAverageBrightness < (darknessThreshold - 10) and measuredAverageBrightness > -1:
						if camera.framerate >= 30:
							print(' INFO: Entering long exposure mode based on analysis of last image set... ')
							slowFramerate = fractions.Fraction(1, 10)							
							try:							
								camera.framerate = slowFramerate
							except Exception as ex:
								print('\n WARNING: Unable to set framerate to ' + str(slowFramerate) + ' ' + str(ex))
								pass						
					elif measuredAverageBrightness > (darknessThreshold + 10):
						if camera.framerate < 30:
							print(' INFO: Exiting long exposure mode based on analysis of last image set...  ')
							camera.framerate = 30

					if measuredAverageBrightness > (brightnessThreshold + 25) and measuredAverageBrightness > -1:
						if camera.shutter_speed == 0 or camera.shutter_speed > 1000: 
							print(' INFO: Increasing shutter speed based on analysis of last image set... [1000]')
							camera.shutter_speed = 1000
						elif camera.shutter_speed > 100:
							print(camera.shutter_speed)
							print(' INFO: Increasing shutter speed based on analysis of last image set... [50]')
							camera.shutter_speed = 50
					elif measuredAverageBrightness < (brightnessThreshold - 25):
						if camera.shutter_speed < 100 and camera.shutter_speed != 0:
							print(' INFO: Decreasing shutter speed based on analysis of last image set... [1000]')
							camera.shutter_speed = 1000
						elif camera.shutter_speed > 900: 
							print(' INFO: Setting shutter speed to "auto" based on analysis of last image set... ')
							camera.shutter_speed = 0 # Auto
					
					measuredBrightnessList.clear()

			except:
				# Ignore errors as sometimes a file will still be in use and can't be analyzed
				pass
			time.sleep(interval)
	except Exception:
		print('\n WARNING: Could not analyze most recent image. ')

# ------------------------------------------------------------------------------

def convertSequenceToVideo(dateToConvert):
	try:
		global framerate
		global renderingInProgress
		global outputFolder		
		global uploadVideo
		renderingInProgress = True
		dateToConvertStamp = dateToConvert.strftime('%Y%m%d')		
		outputFilePath = dateToConvertStamp + '.mp4'	
		print('\n INFO: Converting existing image sequence to video... ')
		# The following runs out of memory as it is not hardware accelerated, perhaps in the future?
		# subprocess.call('cd ' + outputFolder +  '&& ffmpeg -y -r 60 -i '+dateToConvertStamp+'/%08d.jpg -s hd1080 -vcodec libx265 -crf 20 -preset slow '+ outputFilePath, shell=True)
		# The following is not as an efficient codec, but encoding is hardware accelerated and should work for the transient purposes it is used for.
		subprocess.call('cd ' + outputFolder +  '&& ffmpeg -y -r 60 -i '+dateToConvertStamp+'/%08d.jpg -s hd1080 -qscale:v 3 -vcodec mpeg4 '+ outputFilePath, shell=True)
		renderingInProgress = False
		print( '\n INFO: Image conversion complete: ' + outputFilePath )
		if uploadVideo == True: 
			try:		
				print('\n INFO: Uploading video to YouTube... ')	
				uploadDescription = 'Timelapse for ' + dateToConvert.strftime('%Y-%m-%d')
				subprocess.call('python3 camera.timelapse/camera.timelapse.upload.py --file ' + outputFolder + outputFilePath + ' --title "' + dateToConvertStamp + '" --description "' + uploadDescription + '" --privacyStatus "' + privacy + '" --noauth_local_webserver ' , shell=True)
			except Exception as ex:
				print('\n WARNING: YouTube upload may have failed! ' + str(ex) ) 
				pass
		else:
			print('\n INFO: To upload the video to YouTube, start the program with the argument: --uploadVideo True ')
	except ffmpeg.Error as ex:
		print('\n ERROR: Could not convert sequence to video. ' + str(ex))
		pass

# ------------------------------------------------------------------------------

def cleanup():
	try:
		global outputFolder
		global retention
		now = time.time()
		time.sleep(5)
		print('\n INFO: Starting removal of files older than ' + str(retention) + ' days... ')
		for item in os.listdir(outputFolder):
			itemPath = os.path.join(outputFolder, item)
			itemModified = os.stat(itemPath).st_mtime
			itemCompare = now - (retention * 86400)
			if itemModified < itemCompare:
				if os.path.isdir(itemPath):
					shutil.remove(itemPath)
				else:
					os.remove(itemPath)
		print(' INFO: Cleanup complete')
	except Exception as ex:
		print('\n ERROR: ' + str(ex) )


# === Timelapse Capture ========================================================

try: 
	os.chdir('/home/pi') 

	print('\n Camera (Timelapse) ' + version )
	print('\n ----------------------------------------------------------------------\n')
	
	#print(camera.shutter_speed)		
	while True:
		try:
			if keyboard.is_pressed('ctrl+c') or keyboard.is_pressed('esc'):
				# clear()
				echoOn()
				break
		except:
			# Keyboard commands will throw an exception in SSH sessions, so ignore
			pass
			
		if rotate > 0:
			camera.rotation = rotate

		camera.start_preview(fullscreen=False, resolution=(1920, 1080), window=(60, 60, 640, 360))				
		time.sleep(3)	
		camera.framerate = defaultFramerate
		camera.shutter_speed = shutter
		
		# print(' Shutter Speed: ' + str(camera.exposure_speed)) 
		# camera.iso = 400
		#print(' ISO: ' + str(camera.iso))
		captureThread = threading.Thread(target=captureTimelapse)
		captureThread.start()

		analysisThread = threading.Thread(target=analyzeLastImages)
		analysisThread.start()

		if retention > 0:
			cleanupThread = threading.Thread(target=cleanup)
			cleanupThread.start()
		else:
			print('\n WARNING: Retaining captured files indefinitely ')
			print('          Please ensure that sufficient storage exists or set a retention value ')

		while renderVideo:			
			if renderingInProgress == False:
				time.sleep(120)
				yesterday = (datetime.date.today() - datetime.timedelta(days = 1))
				yesterdayStamp = yesterday.strftime('%Y%m%d')
				firstFrameExists = os.path.exists(outputFolder + yesterdayStamp + '/00000001.jpg')
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

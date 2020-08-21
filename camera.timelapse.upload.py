from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import httplib
import httplib2
import keyboard
import os
import random
import sys
import time

version = "2020.08.21"

validPrivacyStatus = ("public", "private", "unlisted")

# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, help="Select the file to upload")
parser.add_argument("--title", default="Timelapse" help="Set the video title")
parser.add_argument("--description", default="Timelapse Video", help="Set the video description")
parser.add_argument("--category", default="22", help="Set the video category.  [ https://developers.google.com/youtube/v3/docs/videoCategories/list ]")
parser.add_argument("--keywords", default="timelapse", help="Set the keywords (comma-seperated)")
parser.add_argument("--privacyStatus", choices=validPrivacyStatus, default=validPrivacyStatus[0], help="Video privacy status.")
parser.add_argument("--channel", help="Set the channel ID")
args = parser.parse_args()

if not os.path.exists(args.file):
	exit("Please specify a valid file using the --file= parameter.")

# ------------------------------------------------------------------------------

httplib2.RETRIES = 1
maxRetries = 10
retryExceptions = (httplib2.HttpLib2Error, IOError, httplib.NotConnected, httplib.IncompleteRead, httplib.ImproperConnectionState, httplib.CannotSendRequest, httplib.CannotSendHeader, httplib.ResponseNotReady, httplib.BadStatusLine)
retryStatusCodes = [500, 502, 503, 504]

# ------------------------------------------------------------------------------

configFile= "config.json"
uploadScope = "https://www.googleapis.com/auth/youtube.upload"
apiServiceName = "youtube"
apiVersion = "v3"


# === Echo Control =============================================================

def echoOff():
	subprocess.run(['stty', '-echo'], check=True)
def echoOn():
	subprocess.run(['stty', 'echo'], check=True)
def clear():
	subprocess.call('clear' if os.name == 'posix' else 'cls')
clear()


# === Functions ================================================================

def getAuthenticatedService(args):
	flow = flow_from_clientsecrets(configFile, scope=uploadScope, message="Please edit your config.json file.")
	storage = Storage("%s-oauth2.json" % sys.argv[0])
	credentials = storage.get()

	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

	return build(apiServiceName, apiVersion, http=credentials.authorize(httplib2.Http()))

# ------------------------------------------------------------------------------

def initalizeUpload(youtube, options):
	tags = None
	if options.keywords:
		tags = options.keywords.split(",")
	targetChannel = youtube.channels.list(part="id", mine=true)[0]
	if options.channel:
		if options.channel != 'DEFAULT':
			targetChannel = channel
	body=dict(snippet=dict(title=options.title, description=options.description, tags=tags, categoryId=options.category, channelId=targetChannel),status=dict(privacyStatus=options.privacyStatus))
	uploadRequest = youtube.videos().insert(part=",".join(body.keys()),body=body,media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True))
	resumableUpload(uploadRequest)

# ------------------------------------------------------------------------------

def resumableUpload(uploadRequest):
	response = None
	error = None
	retryAttempt = 0
	while response is None:
		try:
			print("Uploading file...")
      		status, response = uploadRequest.next_chunk()
			if response is not None:
				if 'id' in response:
					print("Video id '%s' was successfully uploaded." % response['id'])
				else:
 					exit("The upload failed with an unexpected response: %s" % response)
		except HttpError, e:
 			if e.resp.status in retryStatusCodes:
				error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
			else:
				raise
 		except retryExceptions, e:
			error = "A retriable error occurred: %s" % e

 		if error is not None:
 			print(error)
			retryAttempt += 1
			if retryAttempt > maxRetries:
				exit('Maximum retries exceeded.')

			maxSleep = 2 ** retry
			sleepTime = random.random() * maxSleep
			print("Sleeping %f seconds and then retrying..." % sleepTime)
			time.sleep(sleepTime)


# === Timelapse Upload ========================================================

try: 
	os.chdir('/home/pi') 
	while True:
		youtube = getAuthenticatedService(args)
  		try:
    		initalizeUpload(youtube, args)
  		except HttpError, e:
			print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

except KeyboardInterrupt:
	camera.close()
	echoOn()
	sys.exit(1)

else:
	echoOn()
	sys.exit(0)

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from functions import Echo, Console
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
import http.client
import httplib2
import keyboard
import os
import random
import sys
import subprocess
import time

version = '2021.12.06'

console = Console()
echo = Echo()
validPrivacyStatus = ('public', 'private', 'unlisted')

# === Argument Handling ========================================================
print(sys.argv)
argparser.add_argument('--file', required=True, help='Select the file to upload')
argparser.add_argument('--title', default='Timelapse', help='Set the video title', type=str)
argparser.add_argument('--description', default='Timelapse Video', help='Set the video description', type=str)
argparser.add_argument('--category', default='22', help='Set the video category.  [ https://developers.google.com/youtube/v3/docs/videoCategories/list ]', type=int)
argparser.add_argument('--keywords', default='timelapse', help='Set the keywords (comma-seperated)', type=str)
argparser.add_argument('--privacyStatus', choices=validPrivacyStatus, default=validPrivacyStatus[0], help='Video privacy status.', type=str)
args = argparser.parse_args()

if not os.path.exists(args.file):
	exit('\n ERROR: Please specify a valid file using the --file= parameter.')

# ------------------------------------------------------------------------------

httplib2.RETRIES = 1
maxRetries = 10
retryExceptions = (httplib2.HttpLib2Error, IOError, http.client.NotConnected, http.client.IncompleteRead, http.client.ImproperConnectionState, http.client.CannotSendRequest, http.client.CannotSendHeader, http.client.ResponseNotReady, http.client.BadStatusLine)
retryStatusCodes = [500, 502, 503, 504]

# ------------------------------------------------------------------------------

configFile= '/home/pi/camera.timelapse/config.json'
uploadScope = 'https://www.googleapis.com/auth/youtube.upload'
apiServiceName = 'youtube'
apiVersion = 'v3'




# === Functions ================================================================

def getAuthenticatedService(args):
	console.info('YOUTUBE: Authenticating... ', '\n ')
	flow = flow_from_clientsecrets(configFile, scope=uploadScope, message='Please edit your config.json file.')
	storage = Storage('%s-oauth2.json' % sys.argv[0])
	credentials = storage.get()

	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

	return build(apiServiceName, apiVersion, http=credentials.authorize(httplib2.Http()))

# ------------------------------------------------------------------------------

def initalizeUpload(youtube, options):
	console.info(' YOUTUBE: Initializing Upload... ')
	tags = None
	if options.keywords:
		tags = options.keywords.split(',')
	body=dict(snippet=dict(title=options.title, description=options.description, tags=tags, categoryId=options.category) ,status=dict(privacyStatus=options.privacyStatus))
	uploadRequest = youtube.videos().insert(part=','.join(body.keys()),body=body,media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True))
	resumableUpload(uploadRequest)

# ------------------------------------------------------------------------------

def resumableUpload(uploadRequest):
	console.info(' YOUTUBE: Uploading... ')
	response = None
	error = None
	retryAttempt = 0
	while response is None:
		try:
			status, response = uploadRequest.next_chunk()
			if response is not None:
				if 'id' in response:
					console.info(' YOUTUBE: Video id ' + str(response['id']) + ' was successfully uploaded.')
					echo.on()
					sys.exit(0)
				else:
 					exit(' ERROR: The upload failed with an unexpected response of ' + str(response))
		except HttpError as ex:
			if ex.resp.status in retryStatusCodes:
				error = ' YOUTUBE: A retriable HTTP error ' + str(ex.resp.status) + ' occurred: ' + str(ex.content)
			else:
				raise
		except retryExceptions as ex:
			error = ' YOUTUBE: A retriable error occurred: ' + str(ex)

		if error is not None:
			console.error(error)
			retryAttempt += 1
			if retryAttempt > maxRetries:
				exit(' ERROR: Maximum retries exceeded.')

			maxSleep = 2 ** retry
			sleepTime = random.random() * maxSleep
			console.info(' YOUTUBE: Sleeping ' + sleepTime + ' and then retrying...')
			time.sleep(sleepTime)


# === Timelapse Upload ========================================================

try: 
	os.chdir('/home/pi') 
	while True:
		youtube = getAuthenticatedService(args)
		try:
			initalizeUpload(youtube, args)
		except HttpError as ex:
			console.error(' ERROR: An HTTP error ' + str(ex.resp.status) + ' occurred: ' + str(ex.content))

except KeyboardInterrupt:
	echo.on()
	sys.exit(1)

else:
	echo.on()
	sys.exit(0)

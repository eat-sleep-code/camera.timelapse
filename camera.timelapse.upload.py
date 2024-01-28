import argparse
import httplib2
import os
import random
import sys
import time

from functions import Console
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


console = Console()
httplib2.RETRIES = 1

# === API Setup ===============================================================

clientSecretsFile = '/home/pi/camera.timelapse/config.json'
missingClientSecretsMessage = 'Could not locate client secrets file!'
tokenFile = '/home/pi/camera.timelapse/token.json'
apiScopes = ['https://www.googleapis.com/auth/youtube.upload']
apiServiceName = 'youtube'
apiVersion = 'v3'

httplib2.RETRIES = 1
maxRetries = 10
retriableExceptions = (httplib2.HttpLib2Error, IOError)
retriableStatusCodes = [500, 502, 503, 504]
validPrivacyStatuses = ('public', 'private', 'unlisted')

# === Argument Handling =======================================================

parser = argparse.ArgumentParser(description='Upload a video to YouTube')
parser.add_argument('-f', '--file', type=str, help='Path to the video file')
parser.add_argument('-t', '--title', type=str, default='Timelapse', help='Title of the video')
parser.add_argument('-d', '--description', type=str, default='Timelapse Video', help='Description of the video')
parser.add_argument('-c', '--category', type=str, default='22', help='Category of the video')
parser.add_argument('-p', '--privacyStatus', type=str, default='public', choices=['public', 'private', 'unlisted'], help='Privacy status of the video (public, private, or unlisted)')
parser.add_argument('--ignoreLength',type=bool, default=False, help='')
args = parser.parse_args()



# === Authentication ==========================================================

def getAuthenticatedService(args):
	flow = flow_from_clientsecrets(clientSecretsFile, scope=apiScopes, message=missingClientSecretsMessage)

	storage = Storage(tokenFile)
	credentials = storage.get()
	args.noauth_local_webserver = True
	args.logging_level = 'ERROR'
	if credentials is None or credentials.invalid:
		credentials = run_flow(flow, storage, args)

	return build(apiServiceName, apiVersion, http=credentials.authorize(httplib2.Http()))


# === Upload: Initialization ==================================================

def initializeUpload(youtube, options):
	tags = None
	if options.keywords:
		tags = options.keywords.split(',')

	body = dict(
		snippet=dict(
			title=options.title,
			description=options.description,
			tags=tags,
			categoryId=options.category
		),
		status=dict(
			privacyStatus=options.privacyStatus
		)
	)

	uploadRequest = youtube.videos().insert(
		part=','.join(body.keys()),
		body=body, 
		media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
	)

	resumableUpload(uploadRequest)


# === Upload: Resumable =======================================================

def resumableUpload(uploadRequest):
	response = None
	error = None
	retry = 0
	while response is None:
		try:
			console.info('Uploading file...')
			status, response = uploadRequest.next_chunk()
			if response is not None:
				if 'id' in response:
					console.info('Video id ' +  str(response['id']) + ' was successfully uploaded.')
				else:
					exit('The upload failed with an unexpected response: ' + response)
		except HttpError as ex:
			if ex.resp.status in retriableStatusCodes:
				error = 'A retriable HTTP error ' + str(ex.resp.status) + ' occurred:\n' + str(ex.content)
			else:
				raise
		except retriableExceptions as ex:
			error = 'A retriable error occurred: ' + str(ex)

		if error is not None:
			console.info(error)
			retry += 1
			if retry > maxRetries:
				exit('No longer attempting to retry.')

			maxSleep = 2 ** retry
			sleepSeconds = random.random() * maxSleep
			console.info('Sleeping ' + str(sleepSeconds) + ' seconds and then retrying...')
			time.sleep(sleepSeconds)


# -----------------------------------------------------------------------------

if not os.path.exists(args.file):
	exit('Please specify a valid file using the --file= parameter.')

youtube = getAuthenticatedService(args)
try:
	initializeUpload(youtube, args)
except HttpError as ex:
	console.error('An HTTP error ' + str(ex.resp.status) + ' occurred:\n' + str(ex.content))
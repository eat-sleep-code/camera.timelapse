import os
import json
import argparse
from functions import Console
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from moviepy.video.io.VideoFileClip import VideoFileClip


console = Console()


# === API Setup ===============================================================

clientSecretFile = '/home/pi/camera.timelapse/config.json'
scopes = ['https://www.googleapis.com/auth/youtube.upload']
apiServiceName = 'youtube'
apiVersion = 'v3'



# === Argument Handling =======================================================

parser = argparse.ArgumentParser(description='Upload a video to YouTube')
parser.add_argument('-f', '--file', type=str, help='Path to the video file')
parser.add_argument('-t', '--title', type=str, default='Timelapse', help='Title of the video')
parser.add_argument('-d', '--description', type=str, default='Timelapse Video', help='Description of the video')
parser.add_argument('-c', '--category', type=str, default='22', help='Category of the video')
parser.add_argument('-p', '--privacyStatus', type=str, default='public', choices=['public', 'private', 'unlisted'], help='Privacy status of the video (public, private, or unlisted)')
parser.add_argument('--ignoreLength',type=bool, default=False, help='')
args = parser.parse_args()



# === Check If Video Exists And Is At Least 30 Seconds Long ===================

if not os.path.isfile(args.file):
	console.error(f'Error: {args.file} does not exist or is not a file')
	exit()

ignoreLength = args.ignoreLength or False
if ignoreLength:
	console.warn(f'Skipping length check for {args.file}')
else:
	videoDuration = VideoFileClip(args.file).duration
	if videoDuration < 30:
		console.error(f'Error: {args.file} is less than 30 seconds long')
		exit()



# === Authenticate With YouTube Using The Installed Application Flow ==========

creds = None
if os.path.exists('token.json'):
	creds = Credentials.from_authorized_user_file('token.json', scopes)
if not creds or not creds.valid:
	flow = InstalledAppFlow.from_client_secrets_file(clientSecretFile, scopes)
	creds = flow.run_local_server()
	# Save the credentials for the next run
	with open('token.json', 'w') as token:
		token.write(creds.to_json())



# === Prepare Video ===========================================================

youtube = build(apiServiceName, apiVersion, credentials=creds)

title = args.title
description = args.description
category = args.category
tags = []
privacyStatus = args.privacyStatus


# === Upload Video ============================================================

filePath = args.file
mediaFile = MediaFileUpload(filePath)
try:
	uploadRequestBody = youtube.videos().insert(
		part="snippet,status",
		body={
			"snippet": {
				"title": title,
				"description": description,
				"tags": tags,
				"categoryId": category
			},
			"status": {
				"privacyStatus": privacyStatus,
			},
		},
		media_body=mediaFile,
	).execute()
	console.print(f'Successfully uploaded {args.file} to YouTube')
	console.print(f'Video URL: https://www.youtube.com/watch?v={uploadRequestBody["id"]}')
except HttpError as ex:
	console.error(f'An error occurred: {ex}')

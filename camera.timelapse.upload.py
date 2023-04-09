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


# Set up the necessary variables
clientSecretFile = '/home/pi/camera.timelapse/config.json'
scopes = ['https://www.googleapis.com/auth/youtube.upload']
apiServiceName = 'youtube'
apiVersion = 'v3'

# Parse the command line arguments
parser = argparse.ArgumentParser(description='Upload a video to YouTube')
parser.add_argument('file', type=str, help='Path to the video file')
parser.add_argument('-t', '--title', type=str, default='Timelapse', help='Title of the video')
parser.add_argument('-d', '--description', type=str, default='Timelapse Video', help='Description of the video')
parser.add_argument('category', type=str, help='Category of the video')
parser.add_argument('-p', '--privacyStatus', type=str, default='public', choices=['public', 'private', 'unlisted'], help='Privacy status of the video (public, private, or unlisted)')
args = parser.parse_args()

# Check if the video file exists
if not os.path.isfile(args.file):
    Console.print(f'Error: {args.file} does not exist or is not a file', style='bold red')
    exit()

# Check if the video is at least 30 seconds long
videoDuration = VideoFileClip(args.file).duration
if videoDuration < 30:
    Console.print(f'Error: {args.file} is less than 30 seconds long', style='bold red')
    exit()

# Authenticate with YouTube using the installed application flow
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', scopes)
if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(clientSecretFile, scopes)
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Create a YouTube API client object using the authenticated credentials
youtube = build(apiServiceName, apiVersion, credentials=creds)

# Set the metadata for the video
title = args.title
description = args.description
category = args.category
tags = []
privacyStatus = args.privacyStatus

# Upload the video file to YouTube
filePath = args.file
mediaFile = MediaFileUpload(filePath)
try:
    uploadResponse = youtube.videos().insert(
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
    Console.print(f'Successfully uploaded {args.file} to YouTube', style='bold green')
    Console.print(f'Video URL: https://www.youtube.com/watch?v={uploadResponse["id"]}', style='bold')
except HttpError as ex:
    Console.print(f'An error occurred: {ex}', style='bold red')

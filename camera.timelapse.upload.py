
import argparse
import os
import sys

from googleapiclient.http import MediaFileUpload

from functions import Console, Echo
from youtube import createService


version = '2023.01.18'

console = Console()
echo = Echo()
validPrivacyStatus = ('public', 'private', 'unlisted')

# === Argument Handling ========================================================
parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, help='Select the file to upload')
parser.add_argument('--title', default='Timelapse', help='Set the video title', type=str)
parser.add_argument('--description', default='Timelapse Video', help='Set the video description', type=str)
parser.add_argument('--category', default='22', help='Set the video category.  [ https://developers.google.com/youtube/v3/docs/videoCategories/list ]', type=int)
parser.add_argument('--keywords', default='timelapse', help='Set the keywords (comma-seperated)', type=str)
parser.add_argument('--privacyStatus', choices=validPrivacyStatus, default=validPrivacyStatus[0], help='Video privacy status.', type=str)
args = parser.parse_args()

if not os.path.exists(args.file):
	exit('\n ERROR: Please specify a valid file using the --file= parameter.')

# ------------------------------------------------------------------------------

configFile= '/home/pi/camera.timelapse/config.json'
uploadScope = 'https://www.googleapis.com/auth/youtube.upload'
apiServiceName = 'youtube'
apiVersion = 'v3'

# === Functions ================================================================

def upload(youtube, options):
	console.info(' YOUTUBE: Initializing Upload... ')
	tags = None
	if options.keywords:
		tags = options.keywords.split(',')

	videoFile = options.file
	media_file = MediaFileUpload(videoFile)
	
	requestBody = {
		'snippet': {
			'title': options.title,
			'description': options.description,
			'categoryId': options.category,
			'tags':  tags
		},
		'status': {
			'privacyStatus': options.privacyStatus,
			'selfDeclaredMadeForKids': False
		},
		'notifySubscribers': False
	}
	response = youtube.videos().insert(
		part='snippet,status',
		body=requestBody,
		media_body=media_file
	).execute()
	return response.get('id')



# === Timelapse Upload ========================================================

try: 
	os.chdir('/home/pi') 
	while True:
		youtubeService = createService(configFile, apiServiceName, apiVersion, uploadScope)
		try:
			upload(youtubeService, args)
		except Exception as ex:
			console.error(' ERROR: An error occurred: ' + str(ex))

except KeyboardInterrupt:
	echo.on()
	sys.exit(1)

else:
	echo.on()
	sys.exit(0)

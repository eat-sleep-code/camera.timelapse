import datetime
import os
import pickle
from collections import namedtuple

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from functions import Console

console = Console()

def createService(clientSecretFile, apiName, apiVersion, *scopes, prefix=''):
	scopes = [scope for scope in scopes[0]]
	
	credential = None
	appRoot = os.getcwd()
	tokenRoot = 'tokens'
	tokenFile = f'token_{apiName}_{apiVersion}{prefix}.pickle'

	if not os.path.exists(os.path.join(appRoot, tokenRoot)):
		os.mkdir(os.path.join(appRoot, tokenRoot))

	if os.path.exists(os.path.join(appRoot, tokenRoot, tokenFile)):
		with open(os.path.join(appRoot, tokenRoot, tokenFile), 'rb') as token:
			credential = pickle.load(token)

	if not credential or not credential.valid:
		if credential and credential.expired and credential.refresh_token:
			credential.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(clientSecretFile, scopes)
			credential = flow.run_local_server()

		with open(os.path.join(appRoot, tokenRoot, tokenFile), 'wb') as token:
			pickle.dump(credential, token)

	try:
		service = build(apiName, apiVersion, credentials=credential)
		console.log(apiName, apiVersion, 'service created successfully')
		return service
	except Exception as ex:
		console.error('Failed to create service instance for {apiName} : ' + str(ex))
		os.remove(os.path.join(appRoot, tokenRoot, tokenFile))
		return None



def convertToRFCDatetime(year=1900, month=1, day=1, hour=0, minute=0):
	dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
	return dt

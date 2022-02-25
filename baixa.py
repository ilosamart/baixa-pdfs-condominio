import base64
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SECRETS_DIR = f'{ROOT_DIR}/secrets'
TOKEN_JSON = f'{SECRETS_DIR}/token.json'
CREDENTIALS_JSON = f'{SECRETS_DIR}/credentials.json'
DOWNLOADS_DIR = f'{ROOT_DIR}/downloads'


def download(force=False):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_JSON):
        creds = Credentials.from_authorized_user_file(TOKEN_JSON, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_JSON, 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        messages_service = service.users().messages()
        request = messages_service.list(userId='me', q='label:!!ap-condomínio', maxResults=100)

        while request is not None:
            results = request.execute()
            request = messages_service.list_next(request, results)
            # print(results)

            for message_json in results['messages']:
                message_id = message_json['id']
                message = messages_service.get(userId='me', id=message_id).execute()

                for part in message['payload']['parts']:
                    if part['filename']:
                        file_name = part["filename"]
                        match = re.match(r'([0-9]{4})\_([0-9]{8})\.pdf', file_name)
                        if match:
                            file_date = match.group(2)
                            file_year = file_date[4:8]
                            file_month = file_date[2:4]
                            file_day = file_date[:2]
                            file_name = f'BOLETO-{file_year}-{file_month}-{file_day}.pdf'
                        else:
                            match = re.match(r'ESI\_([0-9]{4})\_([0-9]{2})\-([0-9]{4})\.pdf', file_name)
                            if match:
                                file_name = f'EXTRATO-{match.group(3)}-{match.group(2)}.pdf'
                        path = f'{DOWNLOADS_DIR}/{file_name}'
                        if not os.path.isfile(path) or force:
                            print(f'Baixando {file_name}')
                            if 'data' in part['body']:
                                data=part['body']['data']
                            else:
                                att_id = part['body']['attachmentId']
                                att = messages_service.attachments().get(userId='me', messageId=message_id,id=att_id).execute()
                                data = att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            print(f'Escrevendo {file_name} em disco no caminho {path}')
                            with open(path, 'wb') as f:
                                f.write(file_data)
                        else:
                            print(f'Já existe {file_name}!')

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    download()
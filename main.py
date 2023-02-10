import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_filter_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        # print('Labels:')
        # for label in labels:
        #     print(label['name'])

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='in:inbox',  maxResults=1).execute()


        for m in results['messages']:
            mid = m['id']
            r = service.users().messages().get(userId='me', id=mid, format='full').execute()
            title = r['payload']['headers'][0]['value']
            body = r['payload']['body']
            if body['size'] > 0:
                try:
                    data = base64.b64decode(body['data'])
                except:
                    data = base64.b64decode(body['data'] + '==')
            elif len(r['payload']['parts']) > 0:
                parts = r['payload']['parts']
                data = []
                for p in parts:
                    d = p['body']['data']
                    try:
                        part = base64.b64decode(d, '-_')
                    except Exception as e:
                        part = base64.b64decode(d + '==')
                    data.append(part)
            else:
                data = r['snippet']


            print(len(title) * '-')
            print(title)
            print(len(title) * '-')

            soups = [BeautifulSoup(dd, 'html.parser') for dd in data]
            lines = str(soups[0]).split('\r\n')
            start = 0
            end = 0
            name = ''
            email = ''
            item = ''
            lines = [line for line in lines if line]
            for i, line in enumerate(lines):
                if line.startswith('   - Your Name'):
                    name = line.split(':')[1].strip()
                elif line.startswith('   - Email'):
                    email = line.split(':')[1].strip()
                elif line.startswith('   - Select Item Purchased'):
                    item = line.split(':')[1].strip()
                if line.startswith('   - Any questions or comments so far?'):
                    start = i
                elif line.startswith('If you have any questions, reply to this email or contact us at'):
                    end = i

            if start > 0:
                comments = lines[start].split(':')[1].strip() + '\n'
                comments += '\n'.join(lines[start+1:end])
            print(f'Name: {name}')
            print(f'Email: {email}')
            print(f'Item: {item}')
            print(f'Comments: {comments}')
            print()




    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
# [END gmail_quickstart]
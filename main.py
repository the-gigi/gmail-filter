import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


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
        label_dict = {x['name']: x['id'] for x in labels}
        inbox_label_id = label_dict['INBOX']
        kneedace_label_id = label_dict['Kneedace']
        kneedace_filtered_label_id = label_dict['Kneedace Filtered']

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='in:inbox',  maxResults=1).execute()


        for m in results['messages']:
            mid = m['id']
            r = service.users().messages().get(userId='me', id=mid, format='full').execute()
            parts = r['payload'].get('parts', [])
            if len(parts) != 2:
                continue
            d = parts[0]['body']['data']
            data = base64.b64decode(d, '-_')
            soup = BeautifulSoup(data, 'html.parser')
            lines = str(soup).split('\r\n')
            start = 0
            end = 0
            name = ''
            email = ''
            item = ''
            comments = ''
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

            # skip non-kneedace emails
            if start == 0 or len(name) == 0 or len(email) == 0:
                continue

            # keep only kneedace messages with comments (others will be filtered)
            keep = len(comments.strip()) > 0

            print('-' * 20)
            print(f'Name: {name}')
            print(f'Email: {email}')
            print(f'Item: {item}')
            print(f'Comments: {comments}')

            post_data = dict(addLabelIds='', removeLabelIds=[inbox_label_id])
            if keep:
                """move to Kneedace label"""
                post_data['addLabelIds'] = [kneedace_label_id]
            else:
                """move to Kneedace Filtered label"""
                post_data['addLabelIds'] = [kneedace_filtered_label_id]

            service.users().messages().modify(userId='me', id=mid, body=post_data).execute()
            print()





    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
# [END gmail_quickstart]
import base64
import os.path
import sys
import platform
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from pathology.path import Path

script_dir = Path.script_dir()

PREFIX = prefix = '  *   ' if platform.system() == 'Windows' else '   - '
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    """
    :return:
    """
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

    service = build('gmail', 'v1', credentials=creds)
    return service


def process_message(service, payload, mid):
    parts = payload.get('parts', [])
    if len(parts) != 2:
        parts = payload.get('payload', {}).get('parts', [])
        if len(parts) != 2:
            return
    try:
        d = parts[0]['body']['data']
    except Exception as _:
        # Skip messages that don't have the expected structure
        return
    data = base64.b64decode(d, '-_')
    soup = BeautifulSoup(data, 'html.parser')
    if 'You have new submission' in str(soup).lower():
        print('yes!')
    lines = str(soup).split('\r\n')
    start = 0
    end = 0
    name = ''
    email = ''
    item = ''
    comments = ''
    lines = [line for line in lines if line]

    for i, line in enumerate(lines):
        if line.startswith('  *   Your Name :'):
            name = line.split(':')[1].strip()
        elif line.startswith(f'{PREFIX}Email'):
            email = line.split(':')[1].strip()
        elif line.startswith(f'{PREFIX}Select Item Purchased'):
            item = line.split(':')[1].strip()
        if line.startswith(f'{PREFIX}Any questions or comments so far?'):
            start = i
        elif line.startswith('If you have any questions, reply to this email or contact us at'):
            end = i

    if start > 0:
        comments = lines[start].split(':')[1].strip() + '\n'
        comments += '\n'.join(lines[start + 1:end])

    # skip non-kneadace emails
    if len(name) == 0 or len(email) == 0:
        return

    # keep only kneadace messages with comments (others will be filtered)
    keep = len(comments.strip()) > 0

    print('-' * 20)
    print(f'Name: {name}')
    print(f'Email: {email}')
    print(f'Item: {item}')
    print(f'Comments: {comments}')

    label_dict = get_labels(service)
    inbox_label_id = label_dict['INBOX']
    kneadace_label_id = label_dict['KneadAce Submission Comments']
    kneadace_filtered_label_id = label_dict['KneadAce Filtered']

    # Move kneadace message to `kneadace-submission-comments` or `KneadAce Filtered` labels
    new_label = kneadace_label_id if keep else kneadace_filtered_label_id
    post_data = dict(addLabelIds=[new_label], removeLabelIds=[inbox_label_id])

    service.users().messages().modify(userId='me', id=mid, body=post_data).execute()


def get_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
        return
    label_dict = {x['name']: x['id'] for x in labels}
    return label_dict


def main():
    if len(sys.argv) != 2:
        print('Usage: python main.py <number of emails to scan>')
        sys.exit()

    # Run in the script's directory
    os.chdir(script_dir)
    count = int(sys.argv[1])
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='in:inbox', maxResults=count).execute()
    for m in results['messages']:
        mid = m['id']
        r = service.users().messages().get(userId='me', id=mid, format='full').execute()
        headers = {x['name']: x['value'] for x in r['payload']['headers']}
        subject = headers['Subject']
        print(subject)
        print('-' * len(subject))
        if subject != 'You have new submission':
            continue
        process_message(service, r, mid)


if __name__ == '__main__':
    main()

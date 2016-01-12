import httplib2
import os
import json
import requests

import oauth2client
import apiclient 
import gdata.spreadsheet.service


import oauth2client.client
import gspread
import gspread.exceptions

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[oauth2client.tools.argparser]).parse_args()
except ImportError:
    flags = None
    

DEBUG = True

        
class GoogleSpreadSheetService(object):
    
    def __init__(self):
        self.api_data = json.load(open('API Project-22c8534a71fd.json'))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = oauth2client.client.SignedJwtAssertionCredentials(self.api_data['client_email'], self.api_data['private_key'], scope)
        self.gc = gspread.authorize(credentials)
        
        credentials = self._get_credentials()
        http_auth = credentials.authorize(httplib2.Http())
        self.gdrive_svc = apiclient.discovery.build('drive', 'v2', http=http_auth)
        
    def _get_credentials(self, client_secret_file='client_secret.json', scope='https://www.googleapis.com/auth/drive', application_name='Drive API Python Quickstart'):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'drive-python-quickstart.json')
        if DEBUG:
            print 'credential_path:', credential_path
    
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(client_secret_file, scope=scope)
            flow.user_agent = application_name
            credentials = oauth2client.tools.run_flow(flow, store, flags)
            if DEBUG:
                print 'Storing credentials to ' + credential_path
        return credentials
        
    def is_spreadsheet_exist(self, name):
        response = self.gdrive_svc.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'").execute()
        # print response
        with open('output.log', 'w+') as f:
            f.write(json.dumps(response))
        for item in response.get("items"):
            print item.get("title")
            if item.get("title") == name:
                return True
        return False
        
    def create_a_spreadsheet(self, name):
        body = {
          'mimeType': 'application/vnd.google-apps.spreadsheet',
          'title': name
        }
        file = self.gdrive_svc.files().insert(body=body).execute()
        file_id = file.get('id')
        if DEBUG:
            print file_id
            print self.api_data.get("client_email")
        
        permission = self.gdrive_svc.permissions().insert(fileId=file_id, body={
          'value': self.api_data.get("client_email"),
          'type': 'user',
          'role': 'writer'
                }).execute()
                
        return self.get_spreadsheet(name)
        
    def get_spreadsheet(self, name):
        return self.gc.open(name)


class FacebookPostParser(object):
    
    def __init__(self):
        self.access_token = self._get_access_token()
        
    def _get_access_token(self):
        client_id = "198868903558179"
        client_secret = "79974c299c933d563ee78378977fbc8d"
        access_token_exchange_url = "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (client_id, client_secret)
        if DEBUG:
            print 'access_token_exchange_url:', access_token_exchange_url
        res = requests.get(access_token_exchange_url)
        if DEBUG:
            print 'res.text:', res.text
        return res.text.split("=")[1]

    def _get_comments(self, object_id):
        comments_url = 'https://graph.facebook.com/v2.2/%s/comments?access_token=%s&format=json&method=get&pretty=0' % (object_id, self.access_token)
        if DEBUG:
            print 'comments_url:', comments_url
        res = requests.get(comments_url)
        json_dict = json.loads(res.text)
        if DEBUG:
            print 'res.text:', res.text
            print 'json_dict:', json_dict
        
        users_dict = {}
        comments_list = []
        for comment in json_dict['data']:
            user_info = comment['from']
            user_id = user_info['id']
            if user_id not in users_dict.keys():
                users_dict[user_id] = user_info
            comment['from'] = user_id
            if DEBUG:
                print 'comment:', comment
            comments_list.append(comment)
        return users_dict, comments_list
    
    def _parse_url(self, url):
        tokens = url.split("/")
        object_id = tokens[-2]
        owner_id = tokens[-3].split(".")[-1]
        return owner_id, object_id
    
    def parse_facebook_comments(self, url, level=1, merge_comments=False):
        owner_id, object_id = self._parse_url(url)
        if DEBUG:
            print 'owner_id:', owner_id
            print 'object_id:', object_id
        
        total_comments_dict = {}
        users_dict, comments_list = self._get_comments(object_id)
        if DEBUG:
            print 'users_dict:', users_dict
            print 'comments_list:', comments_list
        
        for comment in comments_list:
            if comment['from'] == owner_id:
                owner_comment_id = comment['id']
                if DEBUG:
                    print 'owner_comment_id:', owner_comment_id
                users_dict_lv2, comments_list_lv2 = self._get_comments(owner_comment_id)
                users_dict.update(users_dict_lv2)
                total_comments_dict[owner_comment_id] = comments_list_lv2
        if DEBUG:
            print 'users_dict:', users_dict
            print 'total_comments_dict:', total_comments_dict
            
        return users_dict, total_comments_dict
        

def update_google_spreadsheet(sh, users_dict, comments_dict):
    
    SHEET_COUNT = len(comments_dict)
    SHEET_NAME_ROW = 1
    SHEET_DESC_ROW = 2
    SHEET_COLUMN_OFFSET = 2
    
    USER_COUNT = len(users_dict)
    USER_COLUMN = 1
    USER_ROW_OFFSET = 2
    
    MESSAGE_OWNER_ROW = 1
    MESSAGE_ROW = 2
    MESSAGE_COLUMN_OFFSET = 2
    
    for comment_id in sorted(comments_dict.keys()):
        comments_list = comments_dict[comment_id]
        title_worksheet = comment_id
        MESSAGE_COUNT = len(comments_list)
        ws = sh.add_worksheet(title=title_worksheet, rows=USER_COUNT + USER_ROW_OFFSET, cols=MESSAGE_COUNT + MESSAGE_COLUMN_OFFSET)
        #ws = sh.worksheet(title_worksheet)
        
        for comment_idx, comment in enumerate(comments_list):
            ws.update_cell(MESSAGE_OWNER_ROW, MESSAGE_COLUMN_OFFSET + comment_idx + 1, users_dict[comment['from']]['name'])
            ws.update_cell(MESSAGE_ROW, MESSAGE_COLUMN_OFFSET + comment_idx + 1, comment['message'])
            
        for user_idx, user_id in enumerate(sorted(users_dict.keys())):
            user = users_dict[user_id]
            ws.update_cell(USER_ROW_OFFSET + user_idx + 1, USER_COLUMN, user['name'])
    
    title_worksheet = "summary"
    ws = sh.add_worksheet(title=title_worksheet, rows=USER_COUNT + USER_ROW_OFFSET, cols=SHEET_COUNT + SHEET_COLUMN_OFFSET)
    #ws = sh.worksheet(title_worksheet)
    
    for comment_idx, comment_id in enumerate(sorted(comments_dict.keys())):
        ws.update_cell(SHEET_NAME_ROW, SHEET_COLUMN_OFFSET + comment_idx + 1, comment_id)
        ws.update_cell(SHEET_DESC_ROW, SHEET_COLUMN_OFFSET + comment_idx + 1, ' ')
    
    for user_idx, user_id in enumerate(sorted(users_dict.keys())):
        user = users_dict[user_id]
        ws.update_cell(USER_ROW_OFFSET + user_idx + 1, USER_COLUMN, user['name'])


if __name__ == "__main__":
    
    facebook_url = "https://www.facebook.com/CHENCHENDream/photos/a.564037330395674.1073741829.544424085690332/744783488987723/?type=3&theater"
    facebook_url = "https://www.facebook.com/groups/135465599994004/permalink/456147351259159/"
    facebook_post_parser = FacebookPostParser()
    #users_dict, comments_dict = facebook_comment_parser.parse_facebook_comments(facebook_url)
    '''
    if DEBUG:
        print users_dict
        for user_id, comments_list in comments_dict.iteritems():
            print 'User:', users_dict[user_id]['name']
            for comment in comments_list:
                print '\tMessage:', comment['message']
    '''
    '''
    spreadsheet_name = "AutoGenRobot11"
    g_ss_svc = GoogleSpreadSheetService()
    sh = g_ss_svc.create_a_spreadsheet(spreadsheet_name)
    update_google_spreadsheet(sh, users_dict, comments_dict)
    '''
    access_token = facebook_post_parser.access_token
    object_id = "456147351259159"
    comments_url = 'https://graph.facebook.com/v2.2/%s?access_token=%s&format=json&method=get&pretty=0' % (object_id, access_token)
    if DEBUG:
        print 'comments_url:', comments_url
    res = requests.get(comments_url)
    json_dict = json.loads(res.text)
    print json_dict
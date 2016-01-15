import httplib2
import os
import json
import requests
import datetime

import oauth2client
import apiclient 
import gdata.spreadsheet.service


import oauth2client.client
import gspread
import gspread.exceptions


DEBUG = False

        
class GoogleSpreadSheetService(object):
        
    def __init__(self):
        print os.getcwd()
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
            flags = argparse.ArgumentParser(parents=[oauth2client.tools.argparser]).parse_args(['--noauth_local_webserver'])
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
        
    def create_a_spreadsheet(self, name, email_list=[]):
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
                
        for email in email_list:
            permission = self.gdrive_svc.permissions().insert(fileId=file_id, body={
              'value': email,
              'type': 'user',
              'role': 'writer'
                    }).execute()
                
        return self.get_spreadsheet(name)
        
    def get_spreadsheet(self, name):
        return self.gc.open(name)
        
        
def pair2index(row, column):
    mapping = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    NUMBER_OF_ALPHABET = len(mapping)
    
    remained = (column - 1) % NUMBER_OF_ALPHABET
    if column <= NUMBER_OF_ALPHABET:
        column_rep = mapping[column-1]
    else:
        remained = (column - 1) % NUMBER_OF_ALPHABET
        multiple = (column - remained) / NUMBER_OF_ALPHABET
        column_rep = mapping[multiple-1] + mapping[remained]
    
    return column_rep + str(row)
        
        
def update_google_spreadsheet(sh, users_dict, post_list):
    
    SHEET_COUNT = len(post_list)
    SHEET_NAME_COL = 1
    SHEET_DESC_COL = 2
    SHEET_ROW_OFFSET = 2
    sheet_name_start_pos = pair2index(SHEET_ROW_OFFSET + 1, SHEET_NAME_COL)
    sheet_name_end_pos = pair2index(SHEET_ROW_OFFSET + len(post_list), SHEET_NAME_COL)
    sheet_desc_start_pos = pair2index(SHEET_ROW_OFFSET + 1, SHEET_DESC_COL)
    sheet_desc_end_pos = pair2index(SHEET_ROW_OFFSET + len(post_list), SHEET_DESC_COL)
    
    USER_COUNT = len(users_dict)
    USER_ID_ROW = 1
    USER_NAME_ROW = 2
    USER_COL_OFFSET = 2
    user_id_start_pos = pair2index(USER_ID_ROW, USER_COL_OFFSET + 1)
    user_id_end_pos = pair2index(USER_ID_ROW, USER_COL_OFFSET + USER_COUNT)
    user_name_start_pos = pair2index(USER_NAME_ROW, USER_COL_OFFSET + 1)
    user_name_end_pos = pair2index(USER_NAME_ROW, USER_COL_OFFSET + USER_COUNT)
    
    MESSAGE_ID_COL = 1
    MESSAGE_CONTENT_COL = 2
    MESSAGE_ROW_OFFSET = 2
    message_id_start_pos = pair2index(MESSAGE_ROW_OFFSET + 1, MESSAGE_ID_COL)
    message_content_start_pos = pair2index(MESSAGE_ROW_OFFSET + 1, MESSAGE_CONTENT_COL)
    
    for post_idx, post in enumerate(post_list):
        comment_list = post.get('comments')
        comment_level = post.get('comment_level')
        
        title_worksheet = "post%d" % post_idx
        MESSAGE_COUNT = len(comment_list)
        ws = sh.add_worksheet(title=title_worksheet, rows=MESSAGE_COUNT + MESSAGE_ROW_OFFSET, cols=USER_COUNT + USER_COL_OFFSET)
        #ws = sh.worksheet(title_worksheet)
        ttl_cells = []
        
        if MESSAGE_COUNT > 0:
            message_id_end_pos = pair2index(MESSAGE_ROW_OFFSET + MESSAGE_COUNT , MESSAGE_ID_COL)
            message_content_end_pos = pair2index(MESSAGE_ROW_OFFSET + MESSAGE_COUNT, MESSAGE_CONTENT_COL)
            
            #message_id_cells = ws.range("%s:%s" % (message_id_start_pos, message_id_end_pos))
            #message_content_cells = ws.range("%s:%s" % (message_content_start_pos, message_content_end_pos))
            message_cells = ws.range("%s:%s" % (message_id_start_pos, message_content_end_pos))
            for comment_idx, comment in enumerate(comment_list):
                if comment_level > 1:
                    revised_message = "\n".join(["[%s] %s" % (subcomment['from']['name'], subcomment['message']) for subcomment in comment])
                    comment_id = comment[0]['id']
                else:
                    revised_message = "[%s] %s" % (comment['from']['name'], comment['message'])
                    comment_id = comment['id']
                #message_id_cells[comment_idx].value = comment_id
                #message_content_cells[comment_idx].value = revised_message
                message_cells[comment_idx*2].value = comment_id
                message_cells[comment_idx*2+1].value = revised_message
            #ttl_cells += message_id_cells
            #ttl_cells += message_content_cells
            ttl_cells += message_cells
            
        if USER_COUNT > 0:
            #user_id_cells = ws.range("%s:%s" % (user_id_start_pos, user_id_end_pos))
            #user_name_cells = ws.range("%s:%s" % (user_name_start_pos, user_name_end_pos))
            user_cells = ws.range("%s:%s" % (user_id_start_pos, user_name_end_pos))
            for user_idx, user_id in enumerate(sorted(users_dict.keys())):
                #user_id_cells[user_idx].value = users_dict[user_id]['id']
                #user_name_cells[user_idx].value = users_dict[user_id]['name']
                user_cells[user_idx].value = users_dict[user_id]['id']
                user_cells[user_idx + USER_COUNT].value = users_dict[user_id]['name']
            #ttl_cells += user_name_cells
            ttl_cells += user_cells
        
        if len(ttl_cells) > 0:
            ws.update_cells(ttl_cells)

    title_worksheet = "summary"
    ws = sh.add_worksheet(title=title_worksheet, rows=SHEET_COUNT + SHEET_ROW_OFFSET, cols=USER_COUNT + USER_COL_OFFSET)
    #ws = sh.worksheet(title_worksheet)
    ttl_cells = []
    
    if SHEET_COUNT > 0:
        sheet_name_cells = ws.range("%s:%s" % (sheet_name_start_pos, sheet_name_end_pos))
        sheet_desc_cells = ws.range("%s:%s" % (sheet_desc_start_pos, sheet_desc_end_pos))
        for post_idx, post in enumerate(post_list):
            sheet_name_cells[post_idx].value = "post%d" % post_idx
            sheet_desc_cells[post_idx].value = post_list[post_idx].get('message')
        ttl_cells += sheet_name_cells
        ttl_cells += sheet_desc_cells

    if USER_COUNT > 0:
        user_id_cells = ws.range("%s:%s" % (user_id_start_pos, user_id_end_pos))
        user_name_cells = ws.range("%s:%s" % (user_name_start_pos, user_name_end_pos))
        for user_idx, user_id in enumerate(sorted(users_dict.keys())):
            user_id_cells[user_idx].value = users_dict[user_id]['id']
            user_name_cells[user_idx].value = users_dict[user_id]['name']
        ttl_cells += user_name_cells
        
    if len(ttl_cells) > 0:
        ws.update_cells(ttl_cells)

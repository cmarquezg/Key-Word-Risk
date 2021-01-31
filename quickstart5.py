# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gmail_quickstart]
from __future__ import print_function
import pickle
import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

def sendtomysql(messagestodb):
    # https://pynative.com/python-mysql-insert-data-into-database-table/
    for message_db in messagestodb:
        print("Data to be send to the databasase:")
        print(message_db)

        id = message_db['id']
        emaildate = message_db['date']
        sender = message_db['sender']
        body64 = message_db['body64']
        body_ascii = message_db['body_ascii']
        print(id)
        print(emaildate)
        print(sender)
        print(body64)
        print(body_ascii)
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='keyrisk',
                                                 user='keywordrisk',
                                                 password='keywordpassword21')
                   
            sql = "INSERT INTO keysrisktable (id, emaildate, sender, body64, body_ascii) VALUES (%s, %s, %s, %s, %s)"
            val = (id, emaildate, sender, body64, body_ascii)
         
                   
            cursor = connection.cursor()
            cursor.execute(sql, val)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into keysrisktable table")
            cursor.close()
    
        except mysql.connector.Error as err:
            print("Failed to insert record into keysrisktable table {}".format(err))
    
        finally:
            if (connection.is_connected()):
                connection.close()
                print("MySQL connection is close")


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#def main():
    #"""Shows basic usage of the Gmail API. Lists the user's Gmail labels. """
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

# Call the Gmail API
results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])

'''
if not labels:
    print('No labels found.')
else:
    print('Labels:')
    for label in labels:
        print(label['name'])

'''

# List messages that match the 'risk' keyword:
results = service.users().messages().list(userId='me',q='Risk').execute()
messages = results.get('messages')

#Declare a list to store all id(s)
messageslist=[]

#all matching messages will be extracted and their id(s) will be stored in messageslist
if not messages:
    print('No messages found.')
else:
    print('Messages obtained from gmail account')
    for message in messages:
        messageslist.append(message['id'])
        print([message])

#Declare a list to store all messages that will be sent to the db
messagestodb=[]

#for each id, get the message
for i in messageslist:
    # Declare a dictionary to store all message relevant data
    messagesdata = {}
    messageitem = service.users().messages().get(userId='me',id=i).execute()
    #print(messageitem)
    messagesdata['id'] = (messageitem)["id"]
    messagesdata['date'] = (messageitem)["payload"]["headers"][1]["value"]
    messagesdata['sender'] = (messageitem)["payload"]["headers"][4]["value"]
    messagesdata['body64'] = (messageitem)["payload"]["parts"][0]['body']['data']
    messagesdata['body64'] = messagesdata['body64'].replace("-", "+").replace("_", "/")    #improve base64 decoding
    base64_message = messagesdata['body64']
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    messagesdata['body_ascii'] = message_bytes.decode('ascii')
    # Check if "Risk" is in the ascii body
    if "Risk" in messagesdata['body_ascii']:
        print('A messages with "Risk" in the body was found')
        print(messagesdata)
        messagestodb.append(messagesdata)
    else:
        pass

sendtomysql(messagestodb)


#if __name__ == '__main__':
#    main()
# [END gmail_quickstart]


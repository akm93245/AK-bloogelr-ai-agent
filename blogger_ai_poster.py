import requests
import datetime
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# DeepSeek settings
DEEPSEEK_API_KEY = 'sk-7dc260caa363423ab3601e6176a8c3d6'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Blogger settings
CLIENT_SECRETS_FILE = 'client_secret.json'  # Make sure this file is in your repo
TOKEN_FILE = 'blogger_token.json'
BLOGGER_ID = '6756683184561235068'
SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate_blogger():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('blogger', 'v3', credentials=creds)

def generate_blog_post():
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful blog post writer."},
            {"role": "user", "content": "Write a short, interesting blog post for a general audience about tech or daily life."}
        ],
        "temperature": 0.7,
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response.raise_for_status()
    content = response.json()
    text = content['choices'][0]['message']['content']
    return "Daily AI Blog - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text

def post_to_blogger(service, title, content):
    post = {
        'kind': 'blogger#post',
        'title': title,
        'content': content
    }
    posts = service.posts()
    result = posts.insert(blogId=BLOGGER_ID, body=post).execute()
    print(f"Post published: {result['url']}")

def main():
    service = authenticate_blogger()
    title, content = generate_blog_post()
    post_to_blogger(service, title, content)

if __name__ == '__main__':
    main()

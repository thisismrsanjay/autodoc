import os
import openai
import json
from flask import Flask, request, jsonify, render_template
import requests
import base64
import documentation as doc

def get_github_file_content(user, repo, path, token):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f'Request returned status code {response.status_code}')
    print(response)
    content = base64.b64decode(response.json()['content']).decode('utf-8')
    
    payload = {
        "code": content
    }

    result  = doc.ask(f"\n\n read the code and generate a README.md for it in markdown format",payload)
    return result

# Replace these with your own details
user = 'thisismrsanjay'
repo = 'isltorch'
path = 'hubconf.py'
token = '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'





app = Flask(__name__)












@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process_url', methods=['POST'])
def handle_process_url():
    return get_github_file_content(user, repo, path, token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

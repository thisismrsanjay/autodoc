import requests
import base64

def get_github_file_content(user, repo, path, token):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f'Request returned status code {response.status_code}')
    
    content = base64.b64decode(response.json()['content']).decode('utf-8')
    return content

# Replace these with your own details
user = 'thisismrsanjay'
repo = 'isltorch'
path = 'hubconf.py'
token = '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'

content = get_github_file_content(user, repo, path, token)
print(content)

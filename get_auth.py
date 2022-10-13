import requests
import os

login = os.environ["ExpertAiUser"]
pw = os.environ["ExpertAiPw"]
r = requests.post('https://developer.expert.ai/oauth2/token', json={'username': login, 'password': pw})

with open("token.txt","w") as f:
    f.write(r.text)
    os.environ["ExpertAiToken"] = r.text

print(r.status_code)
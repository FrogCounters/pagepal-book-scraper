To use, change these system environment variables to have your expert ai login:
"ExpertAiUser": YOUR_EAI_USERNAME
"ExpertAiPw": YOUR_EAI_PW
Alternatively you could just edit these directly into the python script on lines 4 and 5

login = //YOUR EAI USERNAME HERE

pw = //YOUR EAI PW HERE

then run get_auth.py (you should have a new txt file with your secret)
after that you can just run get_texts.py and new analysis files should appear

api_requests.py contains the Analyzer class, which contains methods for calling the expertai api links directly and two other useful methods, one for splitting paragraphs into sentences using disambiguation, another for taking lists of strings and outputting lists of emotions.

get_texts.py has a hardcoded list of urls, and uses get requests to retrieve their HTMLs, and parses it for text and book information. the api_requests methods are used to get information from these books. It outputs txt files for what the texts of the book looks like after parsing, and json files which will be used to send to the firebase.

analyse_jsons.py retrieves the json files and uses the information to send post requests to our firebase. It makes use of firebase_bridge.py which contains the method for posting stories.

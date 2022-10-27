import requests
import os
import json
from pprint import pprint
import time
# make_url = lambda x: lambda y: "/" + x + y
# detect_maker = make_url("detect")
# r = requests.post("https://nlapi.expert.ai/v2/detect/hate-speech/en", headers=header, json=input)



class Analyzer():
    
    def __init__(self):
        self.exists = True
        self.api_base = "https://nlapi.expert.ai/"
        self.api_version = "v2/"
        self.token = self.get_auth_token()
        self.header = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + self.token}
        self.detectors = ["esg-sentiment/","hate-speech/"]
        self.language = "en/"

    def _result_decorator(f):
        def inner(self, *args):
            f(self, *args)
            return self.current_result
        return inner

    def _make_url(self, part):
        return os.path.join(self.api_base, self.api_version, part)
    
    def _make_url_detector(self, part):
        return os.path.join(self._make_url(os.path.join("detect/", part)), self.language)
    
    def _make_url_analyzer_specific(self, context, analysis):
        return self._make_url(os.path.join("analyze/", context, self.language, analysis))
    
    def _make_url_analyzer(self, context):
        return self._make_url(os.path.join("analyze/", context, self.language))
    
    def _make_url_classifier(self, classification):
        return self._make_url(os.path.join("categorize/", classification, self.language))
    
    def _make_url_contexts(self):
        return self._make_url("contexts/")

    def api_hate_speech(self):
        return self._make_url_detector("hate-speech/")
    
    def api_esg_sentiment(self):
        return self._make_url_detector("esg-sentiment/")
    
    def api_sentiment(self): #sentiment full
        return self._make_url_analyzer_specific(context="standard/", analysis="sentiment/")
    
    def api_disambiguation(self):
        return self._make_url_analyzer_specific(context="standard/", analysis="disambiguation/")

    def api_full_analysis(self):
        return self._make_url_analyzer(context="standard/")
    
    def api_emotional_traits(self):
        return self._make_url_classifier(classification="emotional-traits/")
    
    @_result_decorator
    def _get_request(self, url):
        self.target = url
        self.current_result = requests.get(url, headers=self.header)

    @_result_decorator    
    def _post_request(self, url, data):
        self.target = url
        self.current_result = requests.post(url, headers=self.header, json=data)
    
    def get_auth_token(self, env_login_key = "EAI_USERNAME", env_pw_key = "EAI_PASSWORD"):
        
        r = requests.post('https://developer.expert.ai/oauth2/token', json={'username': os.environ[env_login_key], 'password': os.environ[env_pw_key]})
        
        if not r.text or r.status_code != 200:
            print("Could not get token")
            raise Exception
        
        token = r.text

        return token

    def hate_speech(self, input_text):
        inp = {"document":{"text": input_text}}
        return self._post_request(self.api_hate_speech(), inp)
    
    def sentiment(self, input_text):
        inp = {"document":{"text": input_text}}
        return self._post_request(self.api_sentiment(), inp)
    
    def full_analysis(self, input_text):
        inp = {"document":{"text": input_text}}
        return self._post_request(self.api_full_analysis(), inp)

    def contexts(self):
        return self._get_request(self._make_url_contexts())
    
    def emotions(self, input_text):
        inp = {"document":{"text": input_text}}
        return self._post_request(self.api_emotional_traits(), inp)
    
    def disambiguation(self, input_text):
        inp = {"document":{"text": input_text}}
        return self._post_request(self.api_disambiguation(), inp)
    
    def split_para(self, paras):
        sentences = []
        total = len(paras)
        counter = 0
        for para in paras:
            print("Splitting para", counter, "/", total)
            counter += 1
            change = 0
            try:
                raw_dis = self.disambiguation(para).json()["data"]
            except requests.exceptions.JSONDecodeError:
                print("encountered JSONDecodeError while disambiguating")
                print("Para:", para)
                print("Sleeping...")
                time.sleep(2)
                # input("Press enter to reattempt")
                raw_dis = self.disambiguation(para).json()["data"]
            except Exception as e:
                print(e)
                input("Enter to continue debug:")
                print("Error line:" + para)
                print(self.disambiguation(para).status_code)
                input("Enter to continue debug (ends prog):")
                raise(e)
            for sentence in raw_dis["sentences"]:
                start = sentence["start"]
                end = sentence["end"]

                current_sentence = para[start:end + 1]                    
                sentences.append(current_sentence)
                change += 1
            
            #add blank line at the end of paragraph
            sentences.append("\n")
            # if change > 0:
            #     sentences[-1] = sentences[-1] + "\n"
        # print(sentences)
        return sentences
    
    def emotions_from_list(self, xs):
        emotions = []
        counter = 0
        total = len(xs)
        for line in xs:
            emo_string = ""

            # debug
            print("Getting Emotions", counter, "/", total)
            counter += 1

            if not line.strip():
                emotions.append(emo_string)
                continue

            try:
                r = self.emotions(line)
                raw_emotions = r.json()
            except requests.exceptions.JSONDecodeError:
                print("Error line:" + line)
                # input("Press enter to re-ping the API")
                print("Request:", r)
                print("Sleeping...")
                time.sleep(2)
                r = self.emotions(line)
                raw_emotions = r.json()
            except Exception as e:
                print(e)
                input("Enter to continue debug:")
                print("Error line:" + line)
                print(r.status_code)
                print("Content")
                print(r.content)
                print("Request")
                print(r)
                input("Enter to continue debug (ends prog):")
                raise(e)
            
            for category in raw_emotions["data"]["categories"]:
                emo_string += category["label"] + ","

            emotions.append(emo_string)

        return emotions
    
    def hate_from_string(self, sentence):
        hate = ""
        # print("Hating on sentence", sentence)
        if not sentence.strip():
            return hate
        r = self.hate_speech(sentence.strip())
        try:
            raw_hate_speech = r.json()["data"]
        except requests.exceptions.JSONDecodeError:
            print("Error line:", sentence)
            # input("Press enter to re-ping the API")
            r = self.hate_speech(sentence.strip())
            raw_hate_speech = r.json()["data"]
        
        for category in raw_hate_speech["categories"]:
            hate += category["label"] + ","

        return hate


def test(analyzer: Analyzer, text: str):
    test_context = False
    test_hate_speech = True

    if test_context:
        res = analyzer.contexts()
        print("---Contexts---")
        pprint(res.text)
        print("Status code:", res.status_code)
        print("---Contexts---")
        input()
    
    if test_hate_speech:
        res = analyzer.hate_speech(text)
        print("---Hate Speech---")
        # print("Text:", res.text)
        print("Categories")
        pprint(res.json()["data"]["categories"])
        print("Status code:", res.status_code)
        print("---Hate Speech---")
        input()




def make_raw_filename(title):
    return title + ".json"

def main():
    testing = False
    input_text = "I hate niggas."
    expert_ai = Analyzer()
  
    if testing:
        test(expert_ai, input_text)
    
    print(expert_ai.hate_from_string(input_text))

    return

if __name__ == "__main__":
    main()
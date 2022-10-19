import requests
import os
import json

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
    
    def get_auth_token(self, sys_env_key = "ExpertAiToken"):
        token = ""
        with open("token.txt","r") as f:
            for line in f:
                token += line.strip()

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
        for para in paras:
            print(para)
            change = 0
            raw_dis = self.disambiguation(para).json()["data"]
            for sentence in raw_dis["sentences"]:
                start = sentence["start"]
                end = sentence["end"]

                current_sentence = para[start:end]                    
                sentences.append(current_sentence)
                change += 1
            
            #add blank line at the end of paragraph
            if change > 0:
                sentences[-1] = sentences[-1] + "\n"
        
        return sentences
    
    def emotions_from_list(self, xs):
        emotions = []
        for line in xs:
            raw_emotions = self.emotions(line).json()
            emo_string = ""
            for category in raw_emotions["data"]["categories"]:
                emo_string += category["label"] + ","

            emotions.append(emo_string)

        return emotions


def test(analyzer):
    test = analyzer.contexts()
    print(test.text)
    print(test.status_code)

def make_raw_filename(title):
    return title + ".json"

def main():
    testing = False
    # input_text = "The happy black cat was a very happy cat who lead a happy life as a happy little cat. The happy black cat could be happy in a hat since his happy little home was black just like the cat." #testing purposes

    expert_ai = Analyzer()

    books = {}

    for file in os.listdir(r"./texts"):
        if file.endswith(".json"):
            title = file.rstrip(".txt").rstrip(".json")
            if os.path.exists(os.path.join("raw_analysis", make_raw_filename(title))):
                print(title + " already exists in raw_analysis/")
                continue



            books[title] = {"sentences":[], "emotions":[]}
            with open(os.path.join(r"texts", file), "r", encoding = "utf-8") as f:
                for line in f:                    
                    try:
                        debug = []
                        raw_line = line.strip()
                        raw_dis = expert_ai.disambiguation(raw_line).json()["data"]
                        for sentence in raw_dis["sentences"]:
                            start = sentence["start"]
                            end = sentence["end"]

                            current_sentence = raw_line[start:end]                    
                            books[title]["sentences"].append(current_sentence)
                            output = expert_ai.emotions(current_sentence)
                            debug.append(output)
                            output_emotions = output.json()
                            emo_string = ""
                            for category in output_emotions["data"]["categories"]:
                                emo_string += category["label"] + ","

                            books[title]["emotions"].append(emo_string)

                    except Exception as e:
                        print(e)
                        print(expert_ai.target)
                        print(debug[-1].status_code)
                        print("input line was:" + raw_line)
                        break
            
            with open(os.path.join("raw_analysis", make_raw_filename(title)), "w", encoding="utf-8") as f:
                json.dump(books[title], f, indent=4)

    


    if testing:
        test(expert_ai)

    # hateful_jordan = expert_ai.emotions(input_text)


    # with open("output_full_analysis.json", "w", encoding="utf-8") as f:
    #     json.dump(hateful_jordan.json(), f, indent=4)

    # with open("output_emotions.json", "w", encoding="utf-8") as f:
    #     json.dump(hateful_jordan.json(), f, indent=4)
    
    # raw_data = hateful_jordan.json()

    # print(hateful_jordan.url)
    # emo_string = ""
    # for category in raw_data["data"]["categories"]:
    #     print(category["label"])
    # print(hateful_jordan.status_code)

    return

if __name__ == "__main__":
    main()
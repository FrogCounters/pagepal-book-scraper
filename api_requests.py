import requests
import os



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
    
    def _make_url_contexts(self):
        return self._make_url("contexts/")

    def api_hate_speech(self):
        return self._make_url_detector("hate-speech/")
    
    def api_esg_sentiment(self):
        return self._make_url_detector("esg-sentiment/")
    
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
    
    def contexts(self):
        return self._get_request(self._make_url_contexts())

def test(analyzer):
    test = analyzer.contexts()
    print(test.text)
    print(test.status_code)

def main():
    input_text = "Michael Jordan was one of the best basketball players of all time. Scoring was Jordan stand-out skill, but he still holds a defensive NBA record, with eight steals in a half."

    expert_ai = Analyzer()
    if True:
        test(expert_ai)
    
    # print(expert_ai.target)
    return

if __name__ == "__main__":
    main()
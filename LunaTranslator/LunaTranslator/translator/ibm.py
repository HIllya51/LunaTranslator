import requests
from translator.basetranslator import basetrans
import json

class TS(basetrans):

    def translate(self, query):
        self.checkempty(['apikey'])
        self.checkempty(['apiurl'])
        apikey = self.config['apikey']
        url = self.config['apiurl'] + '/v3/translate?version=2018-05-01'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'text': [query],
            'source': self.srclang,
            'target': self.tgtlang
        }
        
        try:
            response = requests.post(url, auth=('apikey', apikey), headers=headers, data=json.dumps(data))
            result = response.json()
            translation = result['translations'][0]['translation']
            return translation  
        except Exception as e:
            raise Exception("Translation failed. Error: {}".format(str(e)))

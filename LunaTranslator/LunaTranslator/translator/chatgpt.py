from traceback import print_exc 
import os
import  json 
from translator.basetranslator import basetrans
import os

class TS(basetrans):
    def langmap(self):
        return {'zh': 'Simplified Chinese', 'ja': 'Japanese', 'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'ko': 'Korean', 'fr': 'French', 'cht': 'Traditional Chinese', 'vi': 'Vietnamese', 'tr': 'Turkish', 'pl': 'Polish', 'uk': 'Ukrainian', 'it': 'Italian', 'ar': 'Arabic', 'th': 'Thai'}
    def __init__(self,typename ) :  
        self.context=[]
        super( ).__init__(typename) 
    def inittranslator(self):
        self.api_key=None 
    def translate(self, query):
        self.checkempty(['SECRET_KEY','model'])
        self.contextnum=int(self.config['附带上下文个数'])
        api_type=self.config['api_type']
        if api_type in [1,2]:
            api_version='2023-05-15'
        else :
            api_version=None

        try:
            temperature = float(self.config['Temperature'])
        except:
            temperature = 0.3
        if self.config['使用自定义promt']:
            message=[
                {'role':'user','content':self.config['自定义promt']}
            ]
        else:
            message=[
                {"role": "system", "content": "You are a translator"},
                    {"role": "user", "content": "translate from {} to {}".format(self.srclang,self.tgtlang)},
            ]
        
        for _i in range(min(len(self.context)//2 ,self.contextnum)):
            i=len(self.context)//2-min(len(self.context)//2 ,self.contextnum)+_i
            message.append(self.context[i*2])
            message.append(self.context[i*2+1])
        message.append({"role": "user", "content": query}) 
        if api_type==1:#azure
            headers={'api-key':self.multiapikeycurrent['SECRET_KEY']}
        else:#open_ai/azure_ad
            headers = {
                'Authorization': 'Bearer ' + self.multiapikeycurrent['SECRET_KEY'],
                'Content-Type': 'application/json',
            }
        if api_version:
            params={'api-version':api_version}
        else:params=None
        usingstream=self.config['流式输出']
        data=dict(
            model=self.config['model'],
            messages=message,
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=temperature,
            stream=usingstream
        ) 
        response=self.session.post(
            self.config['OPENAI_API_BASE'] + self.config['Appedix'],
            params=params,
            headers=headers, 
            json=data,
            stream=usingstream
        )
        if usingstream:
            message=''
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data[6:])
                    msg = json_data["choices"][0]["delta"]['content']
                    yield msg
                    message+=msg
                except:
                    raise Exception(response_data)
            
        else:
            try:
                message = response.json()['choices'][0]['message']['content'].replace('\n\n', '\n').strip()
                yield message
            except: 
                raise Exception(response.text)
        self.context.append( {"role": "user", "content": query})
        self.context.append({
            'role':"assistant",
            "content":message
        })
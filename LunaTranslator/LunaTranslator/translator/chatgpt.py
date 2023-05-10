from traceback import print_exc
import zipimport
import os
openai=zipimport.zipimporter(os.path.join(os.path.dirname(__file__), 'openai.zip') ).load_module('openai')
import  json

from translator.basetranslator import basetrans
import os

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}
    def __init__(self,typename ) :  
        self.context=[]
        super( ).__init__(typename) 
    def inittranslator(self):
        self.api_key=None 
    def translate(self, query):
        os.environ['https_proxy']=self.proxy['https'] if self.proxy['https'] else ''
        os.environ['http_proxy']=self.proxy['http'] if self.proxy['http'] else ''
        self.checkempty(['SECRET_KEY','model'])
        self.contextnum=int(self.config['附带上下文个数'])
        secret_key = self.config['SECRET_KEY'] 
        if secret_key != self.api_key:
            self.api_key = secret_key
            # 对api_key频繁赋值会消耗性能
            openai.api_key = secret_key

        openai.OPENAI_API_BASE=self.config['OPENAI_API_BASE']
        
        try:
            temperature = float(self.config['Temperature'])
        except:
            temperature = 0.3
        
        message=[
            {"role": "system", "content": "You are a translator"},
                {"role": "user", "content": f"translate from {self.srclang} to {self.tgtlang}"},
        ]
        
        for _i in range(min(len(self.context)//2 ,self.contextnum)):
            i=len(self.context)//2-min(len(self.context)//2 ,self.contextnum)+_i
            message.append(self.context[i*2])
            message.append(self.context[i*2+1])
        message.append({"role": "user", "content": query}) 

        response = openai.ChatCompletion.create(
            model=self.config['model'],
            messages=message,
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=temperature,
            stream=False
        )
        

        try:
            message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()
            self.context.append( {"role": "user", "content": query})
            self.context.append({
                'role':"assistant",
                "content":message
            })
            return message
        except: 
            raise Exception(json.dumps(response))
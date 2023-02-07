import yaml
import json
print()

with open('engines.json','w') as ff:
    ff.write(json.dumps(yaml.load(open('engines.yaml','r')),ensure_ascii=False))
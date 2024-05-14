
DeckName="LunaDeck"

ModelName="LunaModel"

global_port = 8765

model_fileds=["word","explain","image","audio"]

model_css=''

model_htmlfront = """
{{word}}
<br>
{{explain}}
<br>
{{image}}
    """
model_htmlback = """
{{word}}
<br>
{{explain}}
<br>
{{image}}
    """

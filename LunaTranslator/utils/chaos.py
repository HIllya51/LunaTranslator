from utils.config import globalconfig
def checkchaos(text ):
        code=globalconfig['accept_encoding']
        chaos=True
        for c in code:
            try:
                text.encode(c)
                chaos=False
                break
            except:
                pass
        return chaos
def checkencoding(code):
    try:
        ''.encode(code)
        return True
    except LookupError:
        return False
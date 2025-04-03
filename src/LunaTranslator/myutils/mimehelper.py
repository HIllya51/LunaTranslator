import json, os

cachejson: dict = None
defaultmime = "application/octet-stream"


def query_mime(ext: str):
    if not ext.startswith("."):
        if "." not in ext:
            ext = "." + ext
        else:
            ext = os.path.splitext(ext)[1]
    # https://gist.github.com/AshHeskes/6038140
    global cachejson
    if not cachejson:
        with open(
            "files/static/file-extension-to-mime-types.json",
            "r",
            encoding="utf8",
        ) as ff:
            cachejson = json.load(ff)
    mime = cachejson.get(ext.lower())
    if mime:
        return mime
    import mimetypes

    mime_type, _ = mimetypes.guess_type(ext)
    return mime_type or defaultmime

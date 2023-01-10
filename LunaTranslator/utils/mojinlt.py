import requests

x = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
y = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
trans = str.maketrans(x, y)


def nlt(text, token):
    try:
        response = requests.post(
            "https://api.mojidict.com/parse/functions/nlt-tokenizeText",
            json={
                "text": text,
                "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
                "_SessionToken": token,
            },
            headers={
                "content-type": "text/plain",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            },
        )

        return [
            {
                "orig": result["surface_form"],
                "hira": result["reading"].translate(trans),
                "cixing": result["pos"],
            }
            for result in response.json()["result"]["result"]
        ]
    except:
        return []

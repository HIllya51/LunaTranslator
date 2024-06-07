from translator.basetranslator import basetrans
import uuid


class TS(basetrans):
    def translate(self, query):
        self.checkempty(["key1"])

        # Add your key and endpoint
        key = self.multiapikeycurrent["key1"]
        endpoint = "https://api.cognitive.microsofttranslator.com"

        # location, also known as region.
        # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
        location = self.config["Location"]

        path = "/translate"
        constructed_url = endpoint + path

        params = {"api-version": "3.0", "from": self.srclang, "to": self.tgtlang}

        headers = {
            "Ocp-Apim-Subscription-Key": key,
            # location required if you're using a multi-service or regional (not global) resource.
            "Ocp-Apim-Subscription-Region": location,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        # You can pass more than one object in body.
        body = [{"text": query}]

        request = self.proxysession.post(
            constructed_url, params=params, headers=headers, json=body
        )
        response = request.json()
        try:
            return response[0]["translations"][0]["text"]
        except:
            raise Exception(request.text)

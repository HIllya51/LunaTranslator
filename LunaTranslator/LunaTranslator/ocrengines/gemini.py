import os, uuid, gobject
import requests
import base64
class OCR(baseocr):
    def ocr(self, imagebinary):
        self.checkempty(["key"])
        api_key = self.config["key"]
        image_data = imagebinary
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Ocr this picture"},
                        {"inlineData": {"mimeType": "image/png", "data": image_data}},
                    ]
                }
            ]
        }
        
        # Set up the request headers and URL
        headers = {"Content-Type": "application/json"}
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # Send the request
        response = requests.post(url, headers=headers, json=payload)
        
        # Handle the response
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(response.text)

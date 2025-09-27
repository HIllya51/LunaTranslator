import requests

global_port = 8765
global_host = "127.0.0.1"


class AnkiException(Exception):
    pass


class AnkiUnknownException(Exception):
    pass


class AnkiModelExists(AnkiException):
    pass


class AnkiNoteDuplicate(AnkiException):
    pass


def invoke(action, **params):
    response = requests.get(
        "http://{}:{}".format(global_host, global_port),
        json={"action": action, "params": params, "version": 6},
    )
    try:
        response = response.json()
        if len(response) != 2:
            raise AnkiException("response has an unexpected number of fields")
        if "error" not in response:
            raise AnkiException("response is missing required error field")
        if "result" not in response:
            raise AnkiException("response is missing required result field")
        if response["error"] is not None:
            if response["error"] == "Model name already exists":
                raise AnkiModelExists()
            elif response["error"] == "cannot create note because it is a duplicate":
                raise AnkiNoteDuplicate(response["error"])
            else:
                raise AnkiException(response["error"])
        return response["result"]
    except AnkiException as e:
        raise e
    except Exception as e:
        raise AnkiUnknownException(e)


class Deck:
    @staticmethod
    def create(name):
        invoke("createDeck", deck=name)
        return Deck(name)

    @staticmethod
    def NamesAndIds():
        return [Deck(k, v) for k, v in invoke("deckNamesAndIds").items()]

    def __init__(self, name, did=None):
        self.name = name
        self.did = did

    def __repr__(self):
        return "(Deck {},{})".format(self.name, self.did)

    def delete(self):
        return invoke("deleteDecks", decks=[self.name], cardsToo=True)

    @property
    def Config(self):
        return invoke("getDeckConfig", deck=self.name)

    @Config.setter
    def Config(self, config):
        return invoke("saveDeckConfig", config=config)


class Card:
    def __repr__(self):
        return "(Card {})".format(self.cardId)

    def __init__(self, cardId):
        self.cardId = cardId

    def forget(self):
        return invoke("forgetCards", cards=[self.cardId])

    def relearn(self):
        return invoke("relearnCards", cards=[self.cardId])

    def answer(self):
        return invoke("answerCards", cards=[self.cardId])

    @property
    def Info(self):
        return invoke("cardsInfo", cards=[self.cardId])[0]

    @staticmethod
    def find(query="deck:current"):
        return [Card(_) for _ in invoke("findCards", query=query)]

    @property
    def Deck(self):
        return Deck(list(invoke("getDecks", cards=[self.cardId]).keys())[0])


class Model:
    @staticmethod
    def create(modelName, inOrderFields: list, css, isCloze, cardTemplates):
        invoke(
            "createModel",
            modelName=modelName,
            inOrderFields=inOrderFields,
            css=css,
            isCloze=isCloze,
            cardTemplates=cardTemplates,
        )
        return Model(modelName)

    def __init__(self, name):
        self.name = name

    def updateStyling(self, css):
        return invoke("updateModelStyling", model={"name": self.name, "css": css})

    def updateTemplates(self, templates):
        return invoke(
            "updateModelTemplates", model={"name": self.name, "templates": templates}
        )


class Note:
    @staticmethod
    def add(
        deckName,
        modelName,
        fields: dict,
        allowDuplicate: bool,
        tags: list,
        audio: list,
        picture: list,
    ):
        return invoke(
            "addNote",
            note={
                "deckName": deckName,
                "modelName": modelName,
                "fields": fields,
                "options": {
                    "allowDuplicate": allowDuplicate,
                    # "duplicateScope": "deck",
                    # "duplicateScopeOptions": {
                    #     "deckName": "Default",
                    #     "checkChildren": False,
                    #     "checkAllModels": False,
                    # },
                },
                "tags": tags,
                "audio": audio,
                "picture": picture,
            },
        )

    @staticmethod
    def find(DeckName, word):
        return invoke("findNotes", query='deck:"{}" w:"{}"'.format(DeckName, word))

    @staticmethod
    def delete(notes):
        return invoke("deleteNotes", notes=notes)

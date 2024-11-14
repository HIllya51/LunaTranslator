from translator.basetranslator_dev import basetransdev
import time, os
from myutils.utils import createenglishlangmap


class commonllmdev(basetransdev):
    jsfile = ...
    textarea_selector = ...
    button_selector = ...
    function1 = ...
    function2 = ...

    def langmap(self):
        return createenglishlangmap()

    def injectjs(self):
        with open(
            os.path.join(os.path.dirname(__file__), self.jsfile),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read() % (
                self.function1,
                self.function2,
            )
        self.Runtime_evaluate(js)

    def dotranslate(self, content): ...

    def translate(self, content):
        self.injectjs()
        prompt = self._gptlike_createsys("use_custom_prompt", "custom_prompt")
        content = prompt + content
        self.Runtime_evaluate(
            "document.querySelector(`{}`).foucs()".format(repr(self.textarea_selector))
        )
        self.clear_input()
        self.send_keys(content)
        # chatgpt网站没有焦点时，用这个也可以。
        self.Runtime_evaluate(
            'textarea=document.querySelector({});textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                repr(self.textarea_selector), content
            )
        )

        try:
            # 月之暗面
            while self.Runtime_evaluate(
                "document.querySelector({}).disabled".format(repr(self.button_selector))
            )["result"]["value"]:
                time.sleep(0.1)
        except:
            pass
        self.Runtime_evaluate(
            "document.querySelector({}).click()".format(repr(self.button_selector))
        )
        if self.config["usingstream"]:
            __ = [""]

            def ___(__):
                time.sleep(0.1)
                thistext = self.Runtime_evaluate("thistext")["result"]["value"]

                if thistext.startswith(__[0]):
                    yield thistext[len(__[0]) :]
                else:
                    yield "\0"
                    yield thistext
                __[0] = thistext

            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                yield from ___(__)
            yield from ___(__)
        else:
            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                time.sleep(0.1)
                continue
            yield self.Runtime_evaluate("thistext")["result"]["value"]

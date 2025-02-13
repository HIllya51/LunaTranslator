class Process:
    def process_before(self, text: str):
        context = {}
        return text, context

    def process_after(self, res: str, context):
        return res

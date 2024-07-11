class Process:
    def process_before(self, text):
        context = {}
        return text, context

    def process_after(self, res, context):
        return res

    @staticmethod
    def get_setting_window(parent_window):
        pass

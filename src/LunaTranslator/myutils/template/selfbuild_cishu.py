from cishu.cishubase import cishubase


class MyCishu(cishubase):
    backgroundparser = ""
    use_github_md_css = False

    def init(self):
        pass

    def search(self, word: str) -> str: ...

    def getUrl(self, word: str) -> str: ...

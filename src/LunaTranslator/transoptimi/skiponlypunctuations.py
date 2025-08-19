from myutils.mecab import punctuations


class Process:

    def process_before(self, s):
        if all(_ in punctuations for _ in s):
            return None
        return s

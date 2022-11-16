def checkchaos(text,code=['gbk','shift-jis']):
        chaos=True
        for c in code:
            try:
                text.encode(c)
                chaos=False
                break
            except:
                pass
        return chaos
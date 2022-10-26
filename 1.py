import fugashi

dic_dir_path = r"C:\Users\11737\AppData\Local\Programs\Python\Python38\Lib\site-packages\unidic_lite\dicdir" .replace('\\','/')
tagger = fugashi.Tagger("-r nul -d {} -Owakati".format(dic_dir_path))
print(dir(tagger))
print(dir(tagger.parseToNodeList("麩菓子は麩を主材料とした日本の菓子")[0]))

print( (tagger.parseToNodeList("麩菓子は麩を主材料とした日本の菓子")[0].feature))
# '麩 菓子 は 麩 を 主材 料 と し た 日本 の 菓子'

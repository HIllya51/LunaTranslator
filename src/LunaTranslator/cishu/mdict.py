import base64, uuid, gobject
from cishu.cishubase import DictTree
from myutils.config import isascii
from traceback import print_exc
from myutils.audioplayer import bass_code_cast
import json, os, re
from cishu.mdict_.readmdict import MDX, MDD, MDict
import hashlib, sqlite3, functools
import NativeUtils
from myutils.mimehelper import query_mime


class IndexBuilder(object):
    # todo: enable history
    def checkinfo(self, fn):
        return "{}_{}".format(os.path.getmtime(fn), os.path.getsize(fn))

    def checkneedupdate(self, md, db):
        if not os.path.isfile(db):
            return True
        need = True
        try:
            with open(db + ".txt", "r") as ff:
                need = self.checkinfo(md) != ff.read()
        except:
            pass
        return need

    def checkneedupdateafter(self, md, db):
        with open(db + ".txt", "w") as ff:
            ff.write(self.checkinfo(md))

    def __init__(
        self,
        fname,
        passcode=None,
        enable_history=False,
    ):

        self._mdx_file = fname
        self._mdict_mdds = []
        self._mdd_dbs = []
        _filename, _file_extension = os.path.splitext(fname)
        assert _file_extension == ".mdx"
        assert os.path.isfile(fname)
        self._mdict = MDX(fname, substyle=True)
        _mdxmd5 = (
            os.path.basename(_filename)
            + "_"
            + hashlib.md5(_filename.encode("utf8")).hexdigest()
        )
        _targetfilenamebase = gobject.getcachedir("mdict/index/" + _mdxmd5)
        self._mdx_db = _targetfilenamebase + ".mdx.v3.db"
        # make index anyway

        self._make_mdx_index_checked(self._mdx_db)
        self.makemdds(_filename, _targetfilenamebase)

    def makemdds(self, _filename, _targetfilenamebase):
        i = 0
        while True:
            extra = "" if i == 0 else ".%d" % i
            i += 1
            end = extra + ".mdd"
            if os.path.isfile(_filename + end):
                mdd = MDD(_filename + end)
                self._mdict_mdds.append(mdd)
                self._mdd_dbs.append(_targetfilenamebase + end + ".v3.db")
                self._make_mdd_index_checked(mdd, self._mdd_dbs[-1])
            else:
                break

    def _make_mdd_index_checked(self, mdd: MDD, db_name):
        if self.checkneedupdate(mdd._fname, db_name):
            self._make_mdict_index(mdd, db_name, False)
            self.checkneedupdateafter(mdd._fname, db_name)

    def _make_mdx_index_checked(self, db_name):
        if self.checkneedupdate(self._mdx_file, db_name):
            self._make_mdict_index(self._mdict, db_name, True)
            self.checkneedupdateafter(self._mdx_file, db_name)

    def _make_mdict_index(self, mdd: MDict, db_name, ismdx):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdd._key_list = mdd._read_keys()
        index_list = list(mdd.items())
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            """ CREATE TABLE MDX_INDEX
               (key_text text not null{},
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_start integer,
                record_end integer,
                offset integer
                )""".format(
                " unique" if (not ismdx) else ""
            )
        )
        tuple_list = [
            (
                item["key_text"],
                item["file_pos"],
                item["compressed_size"],
                item["decompressed_size"],
                item["record_start"],
                item["record_end"],
                item["offset"],
            )
            for item in index_list
        ]
        c.executemany("INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?)", tuple_list)

        c.execute(
            """
                CREATE{} INDEX key_index ON MDX_INDEX (key_text)
                """.format(
                " UNIQUE" if (not ismdx) else ""
            )
        )

        conn.commit()
        conn.close()

    def get_mdx_by_index(self, index):
        data = self._mdict.read_records(index)
        record = self._mdict._treat_record_data(data)
        return record

    def lookup_indexes(self, db, keyword, ignorecase=None):
        indexes = []
        if ignorecase:
            sql = 'SELECT * FROM MDX_INDEX WHERE lower(key_text) = lower("{}")'.format(
                keyword
            )
        else:
            sql = 'SELECT * FROM MDX_INDEX WHERE key_text = "{}"'.format(keyword)
        with sqlite3.connect(db) as conn:
            cursor = conn.execute(sql)
            for result in cursor:
                index = {}
                index["file_pos"] = result[1]
                index["compressed_size"] = result[2]
                index["decompressed_size"] = result[3]
                index["record_start"] = result[4]
                index["record_end"] = result[5]
                index["offset"] = result[6]
                indexes.append(index)
        return indexes

    def mdx_lookup(self, keyword, ignorecase=None):
        lookup_result_list = []
        indexes = self.lookup_indexes(self._mdx_db, keyword, ignorecase)
        for index in indexes:
            lookup_result_list.append(self.get_mdx_by_index(index))
        return lookup_result_list

    def mdd_lookup(self, keyword, ignorecase=None):
        lookup_result_list = []
        for i in range(len(self._mdict_mdds)):
            indexes = self.lookup_indexes(self._mdd_dbs[i], keyword, ignorecase)
            for index in indexes:
                lookup_result_list.append(self._mdict_mdds[i].read_records(index))
        return lookup_result_list

    @staticmethod
    def get_keys(db, query=""):
        if not db:
            return []
        if query:
            if "*" in query:
                query = query.replace("*", "%")
            else:
                query = query + "%"
            sql = 'SELECT key_text FROM MDX_INDEX WHERE key_text LIKE "' + query + '"'
        else:
            sql = "SELECT key_text FROM MDX_INDEX"
        with sqlite3.connect(db) as conn:
            cursor = conn.execute(sql)
            keys = [item[0] for item in cursor]
            return keys

    def get_mdd_keys(self, query=""):
        _ = []
        for f in self._mdd_dbs:
            _.extend(self.get_keys(f, query))
        return _

    def get_mdx_keys(self, query=""):
        return self.get_keys(self._mdx_db, query)


from cishu.cishubase import cishubase
import re


class mdict(cishubase):
    def getdistance(self, f):
        _ = self.extraconf[f]

        distance = _["distance"]
        if distance == -1:
            distance = self.config["distance"]
        return distance

    def gettitle(self, f, index: IndexBuilder):
        _ = self.extraconf[f]
        title = _["title"]
        if title is None:
            t: str = os.path.basename(f)[:-4]
            if index._mdict._title != "":
                t1 = index._mdict._title
                if (isascii(t1)) and (isascii(t)):
                    t = t1
                elif not isascii(t1):
                    t = t1
            title = t
        return title

    def getpriority(self, f):
        return self.extraconf[f]["priority"]

    def getFoldFlow(self, f):
        return self.extraconf[f]["FoldFlow"]

    def init_once_mdx(self, f):
        if not os.path.isfile(f):
            return
        absf = os.path.abspath(f)
        if absf in self.dedump:
            return
        self.dedump.add(absf)
        _ = self.extraconf[f] = self.extraconf.get(f, {})
        _["priority"] = _.get("priority", 100)  # 越大展示的越靠前
        _["distance"] = _.get(
            "distance", -1
        )  # -1是跟随mdict全局distance，否则使用私有distance
        _["title"] = _.get("title", None)  # None是使用默认显示名，否则使用自定义显示名
        _["FoldFlow"] = _.get(
            "FoldFlow", False
        )  # None是使用默认显示名，否则使用自定义显示名
        if os.path.exists(f):
            try:
                index = IndexBuilder(f)

                self.builders.append((f, index))

            except:
                print(f)

                print_exc()

    def checkpath(self):
        self.builders = []
        self.dedump = set()
        for f in self.config["paths"]:
            if not f.strip():
                continue
            if not os.path.exists(f):
                continue
            if os.path.isfile(f):
                self.init_once_mdx(f)
                continue
            for _dir, _, _fs in os.walk(f):
                for _f in _fs:
                    if not _f.lower().endswith(".mdx"):
                        continue
                    _f = os.path.join(_dir, _f)
                    self.init_once_mdx(_f)

    def init(self):
        try:
            with open("userconfig/mdict_config.json", "r", encoding="utf8") as ff:
                self.extraconf = json.loads(ff.read())
        except:
            self.extraconf = {}
        self.checkpath()
        try:
            with open(
                gobject.getuserconfigdir("mdict_config.json"), "w", encoding="utf8"
            ) as ff:
                ff.write(json.dumps(self.extraconf, ensure_ascii=False, indent=4))
        except:
            pass

    def querycomplex(self, word, distance, index: IndexBuilder):

        if not distance:
            return sorted(index.get_mdx_keys(word))[: self.config["max_num"]]
        results = []
        diss = {}
        dedump = set()
        for k in index.get_mdx_keys("*" + word + "*"):
            if k in dedump:
                continue
            dedump.add(k)
            dis = NativeUtils.distance(k, word)
            if dis <= distance:
                results.append(k)
                diss[k] = dis
        return sorted(results, key=lambda x: diss[x])[: self.config["max_num"]]

    def parse_url_in_mdd(self, index: IndexBuilder, url1: str):
        url1 = url1.replace("/", "\\")
        if not url1.startswith("\\"):
            if url1.startswith("."):
                url1 = url1[1:]
            else:
                url1 = "\\" + url1
        find = index.mdd_lookup(url1)
        if not find:
            return None
        return find[0]

    def tryloadurl(self, index: IndexBuilder, base, url: str, audiob64vals: dict):
        _local = os.path.join(base, url)
        iscss = url.lower().endswith(".css")
        _type = 0
        file_content = None
        if iscss:
            _type = 1
        if os.path.exists(_local) and os.path.isfile(_local):
            with open(os.path.join(base, url), "rb") as f:
                file_content = f.read()
            return _type, file_content

        if url.startswith("entry://"):
            return 3, "javascript:safe_mdict_search_word('{}')".format(url[8:])
        if url.startswith("sound://"):
            file_content = self.parse_url_in_mdd(index, url[8:])
            if not file_content:
                return
            ext = os.path.splitext(url)[1].lower()[1:]
            if True:  # ext in ("aac", "spx", "opus"):
                new, ext = bass_code_cast(file_content, fr=ext)
                file_content = new
            varname = "var_" + hashlib.md5(file_content).hexdigest()
            audiob64vals[varname] = base64.b64encode(file_content).decode()
            return 3, "javascript:mdict_play_sound('{}',{})".format(
                query_mime(ext), varname
            )
        file_content = self.parse_url_in_mdd(index, url)
        if not file_content:
            return
        return _type, file_content

    def subcallback(
        self,
        index,
        fn,
        base,
        audiob64vals: dict,
        hrefsrcvals: dict,
        divclass: str,
        csscollect: dict,
        match: re.Match,
    ):
        url: str = match.groups()[0]
        matchall: str = match.group()
        if url.startswith("#") or url.startswith("https:") or url.startswith("http:"):
            return matchall
        _type_1 = matchall.split("=")[0]
        try:
            file_content = self.tryloadurl(index, base, url, audiob64vals)
        except:
            print_exc()
            print("unknown", fn, url)
            return matchall
        if not file_content:
            print(fn, url)
            return matchall
        _type, file_content = file_content
        if _type == -1:
            return matchall
        elif _type == 3:
            return matchall.replace(url, file_content)
        elif _type == 1:
            css = self.parse_stylesheet(
                file_content.decode("utf8", errors="ignore"), divclass
            )
            if css:
                csscollect[url] = css
                return None
            else:
                return matchall
        elif _type == 0:
            varname = "var_" + hashlib.md5(file_content).hexdigest()
            hrefsrcvals[varname] = (
                _type_1,
                query_mime(url),
                base64.b64encode(file_content).decode(),
            )
            return matchall.replace(url, varname)

        return matchall

    def repairtarget(
        self,
        index,
        fn,
        html_content: str,
        audiob64vals: dict,
        hrefsrcvals: dict,
        divclass: str,
        csscollect: dict,
    ):
        base = os.path.dirname(fn)
        parser = functools.partial(
            self.subcallback,
            index,
            fn,
            base,
            audiob64vals,
            hrefsrcvals,
            divclass,
            csscollect,
        )
        for patt in (
            'src="([^"]+)"',
            'href="([^"]+)"',
            """src='([^']+)'""",
            """href='([^']+)'""",
        ):
            html_content = re.sub(patt, parser, html_content)

        return '<div class="{}">{}</div>'.format(divclass, html_content)

    def searchthread_internal(self, index: IndexBuilder, k, __safe):
        allres = []
        if k in __safe:  # 避免循环引用
            return []
        __safe.append(k)
        for content in index.mdx_lookup(k):
            match = re.match("@@@LINK=(.*)", content.strip())
            if match:
                match = match.groups()[0]
                allres += self.searchthread_internal(index, match, __safe)
            else:
                allres.append(content)
        return allres

    def expand_repetition_marks(self, text):
        """
        展开日语中的叠字符号（々、ゝ、ヽ、〱等）为完整重复形式。

        Args:
            text (str): 输入的日语文本，可能包含叠字符号。

        Returns:
            str: 展开叠字符号后的文本。
        """
        # 正则表达式匹配叠字符号及其前一个字符
        pattern = re.compile(
            r"([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff])(々|ゝ|ヽ|〱)"
        )

        def replace_match(match):
            char, repetition_mark = match.group(1), match.group(2)
            # 根据不同的叠字符号处理
            if repetition_mark == "々":
                # 々：重复前一个汉字
                return char * 2
            elif repetition_mark == "ゝ":
                # ゝ：重复前一个平假名
                return char * 2
            elif repetition_mark == "ヽ":
                # ヽ：重复前一个片假名
                return char * 2
            elif repetition_mark == "〱":
                # 〱：重复前一个字符（通用）
                return char * 2
            else:
                return char + repetition_mark

        # 使用正则替换
        expanded_text = pattern.sub(replace_match, text)
        return expanded_text

    def searchthread(self, allres, i, word, audiob64vals, hrefsrcvals):
        f, index = self.builders[i]
        results = []
        __safe = []
        try:
            keys = self.querycomplex(word, self.getdistance(f), index)
            if not keys:
                # 只有正常查不到时，才尝试展开
                word1 = self.expand_repetition_marks(word)
                if word1 != word:
                    keys2 = self.querycomplex(word1, self.getdistance(f), index)
                    for _ in keys2:
                        if _ in keys:
                            continue
                        keys.append(_)
            for k in keys:
                for content in sorted(
                    set(self.searchthread_internal(index, k, __safe))
                ):
                    results.append(content)
        except:

            print_exc()
        if not results:
            return
        divclass = "luna_" + str(uuid.uuid4())
        csscollect = {}
        for i in range(len(results)):
            results[i] = self.repairtarget(
                index, f, results[i], audiob64vals, hrefsrcvals, divclass, csscollect
            )
        collectresult = "".join(results)
        if csscollect:
            collectresult += "<style>\n"
            for css in csscollect.values():
                collectresult += css + "\n"
            collectresult += "</style>\n"
        allres.append(
            (
                self.getpriority(f),
                self.getFoldFlow(f),
                self.gettitle(f, index),
                collectresult,
            )
        )

    def generatehtml_tabswitch(self, allres):
        btns = []
        contents = []
        idx = 0
        for _, foldflow, title, res in allres:
            klass2 = "tab-pane_mdict_internal"
            klass1 = "tab-button_mdict_internal"
            if idx == 0:
                klass2 += " active"
                klass1 += " active"
            btns.append(
                """<button type="button" onclick="onclickbtn_mdict_internal('buttonid_mdict_internal{idx}')" id="buttonid_mdict_internal{idx}" class="{klass}" data-tab="tab_mdict_internal{idx}">{title}</button>""".format(
                    idx=idx, title=title, klass=klass1
                )
            )
            contents.append(
                """<div id="tab_mdict_internal{idx}" class="{klass}">{res}</div>""".format(
                    idx=idx, res=res, klass=klass2
                )
            )
            idx += 1
        res = """
<script>
function onclickbtn_mdict_internal(_id) {
    tabPanes = document.querySelectorAll('.tab-widget_mdict_internal .tab-pane_mdict_internal');
    tabButtons = document.querySelectorAll('.tab-widget_mdict_internal .tab-button_mdict_internal');
        for (i = 0; i < tabButtons.length; i++)
            tabButtons[i].classList.remove('active');
        for (i = 0; i < tabPanes.length; i++)
            tabPanes[i].classList.remove('active');

        document.getElementById(_id).classList.add('active');

        tabId = document.getElementById(_id).getAttribute('data-tab');
        tabPane = document.getElementById(tabId);
        tabPane.classList.add('active');
    }
</script>
<style>
.centerdiv_mdict_internal {
    display: flex;
    justify-content: center;
}
.tab-widget_mdict_internal .tab-button_mdict_internals_mdict_internal {
    display: flex;
}

.tab-widget_mdict_internal .tab-button_mdict_internal {
    padding: 7px 15px;
    background-color: #cccccccc;
    border: none;
    cursor: pointer;
    display: inline-block;
    line-height: 20px;
}

.tab-widget_mdict_internal .tab-button_mdict_internal.active {
    background-color: #cccccc44;
}

.tab-widget_mdict_internal .tab-content_mdict_internal .tab-pane_mdict_internal {
    display: none;
    padding: 10px;
}

.tab-widget_mdict_internal .tab-content_mdict_internal .tab-pane_mdict_internal.active {
    display: block;
}
</style>"""
        res += """
<div class="tab-widget_mdict_internal">
    <div class="centerdiv_mdict_internal"><div>
        {btns}
    </div>
    </div>
    <div>
        <div class="tab-content_mdict_internal">
            {contents}
        </div>
    </div>
</div>
""".format(
            btns="".join(btns), contents="".join(contents)
        )
        return res

    def generatehtml_flow(self, allres):
        content = """<style>.collapsible-list {
        list-style: none;
        padding: 0;
    }
    
    .collapsible-header {
        background-color: #dddddd50;
        padding: 8px;
        cursor: pointer;
        border: 1px solid #ddd;
        border-bottom: none;
    }
    
    .collapsible-content {
        display: none;
        padding: 10px;
        border: 1px solid #ddd;
    }</style>
<script>
function mdict_flowstyle_clickcallback(_id)
{
content = document.getElementById(_id).nextElementSibling;
if (content.style.display === 'block') {
    content.style.display = 'none';
} else {
    content.style.display = 'block';
}
if(window.LUNAJSObject)
        LUNAJSObject.mdict_fold_callback(_id,content.style.display)
}</script>"""
        lis = []

        for _, foldflow, title, res in allres:
            extra = "display: block;"
            if foldflow:
                extra = "display: none;"
            uid = str(uuid.uuid4())
            lis.append(
                r"""<div><div class="collapsible-header" id="{}" onclick="mdict_flowstyle_clickcallback('{}')">{}</div><div class="collapsible-content" style="{}">
               {}
            </div></div>""".format(
                    uid, uid, title, extra, res
                )
            )
        content += r"""
<div class="collapsible-list">
         {}
    </div>""".format(
            "".join(lis)
        )

        return content

    def search(self, word):
        allres = []
        audiob64vals = {}
        hrefsrcvals = {}
        for i in range(len(self.builders)):
            self.searchthread(allres, i, word, audiob64vals, hrefsrcvals)
        if len(allres) == 0:
            return
        allres.sort(key=lambda _: -_[0])
        func = "<script>"
        func += """
function replacelongvarsrcs(varval, varname)
{
let type=varval[0]
let elements = document.querySelectorAll('['+type+'="'+varname+'"]');
for(let i=0;i<elements.length;i++)
    elements[i][type]="data:"+varval[1]+";base64," + varval[2]
}
var lastmusicplayer=false;
function mdict_play_sound(ext, b64){

if(window.LUNAJSObject)
        LUNAJSObject.luna_audio_play_b64(b64)
    else{
    const music = new Audio();
    music.src="data:"+ext+";base64,"+b64
    if(lastmusicplayer!=false)
    {
        lastmusicplayer.pause()
    }
    lastmusicplayer=music
    music.play();
    }
}
function safe_mdict_search_word(word){
   if(window.LUNAJSObject)
        LUNAJSObject.luna_search_word(word)
}"""
        for varname, val in audiob64vals.items():
            func += '{}="{}"\n'.format(varname, val)
        func += "</script><script id='replacelongvarsrcs_1'>"
        for varname, (_type, mime, val) in hrefsrcvals.items():
            func += '{}=["{}","{}","{}"]\n'.format(varname, _type, mime, val)
            func += 'replacelongvarsrcs({},"{}")\n'.format(varname, varname)
        func += 'document.getElementById("replacelongvarsrcs_1").remove()'
        func += "</script>"
        if self.config["stylehv"] == 0:
            return self.generatehtml_tabswitch(allres) + func
        elif self.config["stylehv"] == 1:
            return self.generatehtml_flow(allres) + func

    def tree(self):
        if len(self.builders) == 0:
            return

        class everydict(DictTree):
            def __init__(self, ref: "mdict", f, index: IndexBuilder) -> None:
                self.f = f
                self.index = index
                self.ref = ref

            def text(self):
                return self.ref.gettitle(self.f, self.index)

            def childrens(self) -> list:
                return sorted(list(set(self.index.get_mdx_keys("*"))))

        class DictTreeRoot(DictTree):
            def __init__(self, ref: "mdict") -> None:
                self.ref = ref

            def childrens(self) -> "list[DictTree]":
                saves = []
                for f, index in self.ref.builders:
                    saves.append(
                        (self.ref.getpriority(f), everydict(self.ref, f, index))
                    )
                saves.sort(key=lambda x: x[0])
                i = []
                for _, _i in saves:
                    i.append(_i)
                return i

        return DictTreeRoot(self)

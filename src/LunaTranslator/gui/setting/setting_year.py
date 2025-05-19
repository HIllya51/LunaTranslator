from qtsymbols import *
import gobject
import os
from gui.usefulwidget import WebviewWidget
from datetime import datetime, timedelta
from myutils.config import savehook_new_data, globalconfig, extradatas

timestamps = [1609459200, 1672531200, 1704067200, 1720032000]


def split_range_into_days(times):
    everyday = {}
    for start, end in times:
        if start == 0:
            everyday[0] = end
            continue

        start_date = datetime.fromtimestamp(start)
        end_date = datetime.fromtimestamp(end)

        current_date = start_date
        while current_date <= end_date:
            end_of_day = current_date.replace(
                hour=23, minute=59, second=59, microsecond=0
            )
            end_of_day = end_of_day.timestamp() + 1

            if end_of_day >= end_date.timestamp():
                useend = end_date.timestamp()
            else:
                useend = end_of_day
            duration = useend - current_date.timestamp()
            today = end_of_day - 1
            if today not in everyday:
                everyday[today] = 0
            everyday[today] += duration
            current_date += timedelta(days=1)
            current_date = current_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
    return everyday


def calc_uid_times(inf):
    everytimes = {}
    for uid, ls in inf.items():
        x = 0
        for s, e in ls:
            x += e - s
        if int(x):
            everytimes[uid] = x

    return everytimes


def getthisyearinfo(allinfos):
    current_year = datetime.now().year * 12 + datetime.now().month
    yearinfos = {}
    for uid, ls in allinfos.items():
        yearinfos[uid] = []
        for s, e in ls:
            date = datetime.fromtimestamp(s)
            if date.year * 12 + date.month + 12 >= current_year:
                yearinfos[uid].append((s, e))
        if len(yearinfos[uid]) == 0:
            yearinfos.pop(uid)
    return yearinfos


def geteverygameeveryday(yearinfos):
    x = {}
    for uid, ls in yearinfos.items():
        x[uid] = split_range_into_days(ls)
    return x


def group_by_month(timerangeindays):
    every = {}
    for uid, ls in timerangeindays.items():

        inmonths = {}
        for day, time in ls.items():
            # 将时间戳转换为日期对象（时间戳为毫秒，需要除以1000）
            date = datetime.fromtimestamp(day)
            if date.month not in inmonths:
                inmonths[date.month] = 0
            inmonths[date.month] += time
        every[uid] = inmonths
    return every


def have_game_days_count(everydays):
    days = set()
    for info in everydays.values():
        for d in info:
            days.add(d)
    return len(days)


def everymonths_game_images(everymonth):
    months = {}
    for i in range(1, 13):
        months[i] = {}
    for uid in everymonth:
        for m, tm in everymonth[uid].items():
            months[m][uid] = tm
    return months


def getuidimage_local(uid):
    data = savehook_new_data.get(uid)
    if not data:
        return
    main = savehook_new_data[uid].get("currentmainimage")
    if (main in savehook_new_data[uid].get("imagepath_all", [])) and os.path.exists(
        extradatas["localedpath"].get(main, main)
    ):
        return os.path.abspath(extradatas["localedpath"].get(main, main))
    else:
        for _ in savehook_new_data[uid].get("imagepath_all", []):
            if os.path.exists(extradatas["localedpath"].get(_, _)):
                return os.path.abspath(extradatas["localedpath"].get(_, _))


def getuidimage(uid):
    l = getuidimage_local(uid)
    if l:
        return l
    data = savehook_new_data.get(uid)
    if not data:
        return
    main = savehook_new_data[uid].get("currentmainimage")
    if (main in savehook_new_data[uid].get("imagepath_all", [])) and main.startswith(
        "http"
    ):
        return main
    else:
        for _ in savehook_new_data[uid].get("imagepath_all", []):
            if _.startswith("http"):
                return os.path.abspath(_)


def guji_word(everytimes, alleverytimes):
    cnt_zishu = 0
    for uid in everytimes:
        data = savehook_new_data.get(uid)
        if not data:
            continue
        if not everytimes[uid]:
            return
        cnt_zishu += (
            data.get("statistic_wordcount", 0) * everytimes[uid] / alleverytimes[uid]
        )
    return cnt_zishu


def getimages(xx):
    uids = list(xx.keys())
    uids.sort(key=lambda x: -xx[x])
    tu = []
    for uid in uids:
        img = getuidimage(uid)
        if img:
            tu.append(img)
    return tu


def getallgamelabels(yearinfos):
    developers = {}
    webtags = {}
    # 可以考虑玩的最多的游戏的标签，和玩的时间最长的标签
    for uid in yearinfos:
        data = savehook_new_data.get(uid)
        if not data:
            continue
        img = getuidimage(uid)
        if not img:
            continue
        for dev in data["developers"]:
            if dev not in developers:
                developers[dev] = []
            developers[dev].append(img)
        for tag in data["webtags"]:
            tag = globalconfig["tagNameRemap"].get(tag, tag)
            if tag not in webtags:
                webtags[tag] = []
            webtags[tag].append(img)
    return developers, webtags


def yearsummary(self, basel: QHBoxLayout):
    allinfos = gobject.baseobject.playtimemanager.all()  # {uid:[[s,e]]}
    yearinfos = getthisyearinfo(allinfos)  # {uid:[[s,e]]}
    alleverytimes = calc_uid_times(allinfos)  # {uid:time}
    everytimes = calc_uid_times(yearinfos)  # {uid:time}
    everydays = geteverygameeveryday(yearinfos)  # {uid:{day_tms:time}}
    everymonth = group_by_month(everydays)  # {uid:{month:time}}
    everymonth_uid_time = everymonths_game_images(everymonth)  # {month:{uid:time}}
    everymonth_time = {
        k: sum(v.values()) for k, v in everymonth_uid_time.items()
    }  # {month:time}
    uids = list(everytimes.keys())
    uids.sort(key=lambda x: -everytimes[x])
    tu = getimages(everytimes)
    tu_m = {}
    for m, info in everymonth_uid_time.items():
        tu_m[m] = getimages(info)
    developer, webtags = getallgamelabels(yearinfos)
    with open(r"LunaTranslator\htmlcode/yearsummary/yearsummary.value.js", "w", encoding="utf8") as ff2:
        ff2.write(
            r"""
GAMES_YEAR_PLAYED={GAMES_YEAR_PLAYED}
TIME_YEAR_PLAYED={TIME_YEAR_PLAYED}
COUNT_ZISHU_YEAR_PLAYED={COUNT_ZISHU_YEAR_PLAYED}
TIME_YEAR_PLAYED_DAY={TIME_YEAR_PLAYED_DAY}
TOP25_TIME_IMAGE={TOP25_TIME_IMAGE}
TOP25_TIME_IMAGE_M={TOP25_TIME_IMAGE_M}
everymonth_time={everymonth_time}
developer={developer}
webtags={webtags}
""".format(
                developer=developer,
                webtags=webtags,
                GAMES_YEAR_PLAYED=len(everytimes),
                TIME_YEAR_PLAYED=int(sum(everytimes.values()) / 3600),
                COUNT_ZISHU_YEAR_PLAYED=int(guji_word(everytimes, alleverytimes)),
                TIME_YEAR_PLAYED_DAY=have_game_days_count(everydays),
                TOP25_TIME_IMAGE=tu,
                TOP25_TIME_IMAGE_M=tu_m,
                everymonth_time=everymonth_time,
            )
        )

    link = os.path.abspath(r"LunaTranslator\htmlcode/yearsummary/yearsummary.html")
    try:
        _ = WebviewWidget(self)
        _.navigate(link)
    except:
        _ = QWidget()
        os.startfile(link)
    basel.addWidget(_)

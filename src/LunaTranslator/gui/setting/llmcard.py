from qtsymbols import *
import copy
import functools
import uuid

from myutils.config import globalconfig, translatorsetting, ocrsetting, _TR
from myutils.llmcard import (
    LLM_MODEL_CARD_DEFAULT,
    ensure_llm_model_cards,
    normalize_llm_model_card,
    ordered_llm_model_card_ids,
)
from myutils.proxy import getproxy
from myutils.utils import APIType, common_list_models
from gui.customparams import customparams
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import getIconButton, getsmalllabel, makescroll, request_delete_ok
from gui.dynalang import LGroupBox


def list_models(typename, regist: dict):
    return common_list_models(
        getproxy(),
        APIType(regist["API接口地址"]()),
        regist.get("SECRET_KEY", lambda: "")().split("|")[0],
    )


def _llm_model_card_argstype():
    return {
        "name": {"name": "名称", "rank": 0},
        "capabilities": {"name": "能力", "type": "llm_capabilities", "rank": 0.1},
        "API接口地址": {"rank": 1, "type": "llm_api_urls"},
        "SECRET_KEY": {"rank": 2, "name": "API Key", "type": "textlist"},
        "model": {
            "rank": 3,
            "type": "lineedit_or_combo",
            "list_function": "list_models",
            "list_cache": "modellistcache",
        },
        "modellistcache": {"type": "list_cache"},
        "Temperature": {"type": "spin", "min": 0, "max": 2, "step": 0.01},
        "max_tokens": {
            "type": "intspin",
            "min": 1,
            "max": 1000000,
            "appends": ["use_max_completion_tokens"],
        },
        "use_max_completion_tokens": {
            "name": "使用 max_completion_tokens",
            "type": "switch",
        },
        "top_p": {
            "refswitch": "top_p_use",
            "type": "spin",
            "min": 0,
            "max": 1,
            "step": 0.01,
        },
        "frequency_penalty": {
            "type": "spin",
            "refswitch": "frequency_penalty_use",
            "min": -2,
            "max": 2,
            "step": 0.01,
        },
        "reasoning_effort": {
            "type": "combo",
            "refswitch": "reasoning_effort_use",
            "internal": ["none", "minimal", "low", "medium", "high", "xhigh"],
            "list": ["none", "minimal", "low", "medium", "high", "xhigh"],
        },
        "thinking.type": {
            "type": "combo",
            "refswitch": "thinking.type.use",
            "internal": ["disabled", "enabled"],
            "list": ["disabled", "enabled"],
        },
        "customparams": {
            "name": "其他参数",
            "type": "custom",
            "function": "customparams",
            "rank": -1,
        },
    }


def _iter_llm_card_setting_groups():
    yield translatorsetting
    yield globalconfig.get("cishu", {})
    yield ocrsetting
    yield globalconfig.get("reader", {})


def _llm_card_usages(uid):
    usages = []
    for settings in _iter_llm_card_setting_groups():
        for name, setting in settings.items():
            if not isinstance(setting, dict):
                continue
            args = setting.get("args")
            if not isinstance(args, dict):
                continue
            if args.get("llm_model_card") == uid:
                usages.append(setting.get("name") or name)
    return usages


class LLMModelCardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ensure_llm_model_cards()
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.addWidget(getIconButton(self.add_card, icon="fa.plus", tips="添加"))
        toolbar.addStretch()
        layout.addLayout(toolbar)

        scroll = makescroll()
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(6)
        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)
        self.reload()

    def reload(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for uid in ordered_llm_model_card_ids():
            self.cards_layout.addWidget(self._card_widget(uid))
        self.cards_layout.addStretch()

    def _card_widget(self, uid):
        card = normalize_llm_model_card(globalconfig["llm_model_cards"].get(uid))
        box = LGroupBox(card.get("name") or card.get("model") or "大模型")
        grid = QGridLayout(box)
        grid.setColumnStretch(1, 1)
        grid.addWidget(getsmalllabel("模型")(), 0, 0)
        grid.addWidget(QLabel(card.get("model", "")), 0, 1)
        grid.addWidget(getsmalllabel("API")(), 1, 0)
        api = QLabel(card.get("API接口地址", ""))
        api.setWordWrap(True)
        grid.addWidget(api, 1, 1)
        grid.addWidget(getsmalllabel("能力")(), 2, 0)
        grid.addWidget(QLabel(" / ".join(card.get("capabilities", []))), 2, 1)
        grid.addWidget(getsmalllabel("Key")(), 3, 0)
        grid.addWidget(QLabel("已配置" if card.get("SECRET_KEY") else "未配置"), 3, 1)

        actions = QHBoxLayout()
        actions.addWidget(
            getIconButton(
                functools.partial(self.edit_card, uid),
                icon="fa.gear",
                tips="设置",
            )
        )
        actions.addWidget(
            getIconButton(
                functools.partial(self.copy_card, uid),
                icon="fa.copy",
                tips="复制",
            )
        )
        actions.addWidget(
            getIconButton(
                functools.partial(self.delete_card, uid),
                icon="fa.minus",
                tips="删除",
            )
        )
        actions.addStretch()
        grid.addLayout(actions, 0, 2, 4, 1)
        return box

    def _normalize_card(self, uid):
        globalconfig["llm_model_cards"][uid] = normalize_llm_model_card(
            globalconfig["llm_model_cards"].get(uid)
        )

    def edit_card(self, uid):
        self._normalize_card(uid)
        card = globalconfig["llm_model_cards"][uid]
        dialogconf = {"args": card, "argstype": _llm_model_card_argstype()}
        items = autoinitdialog_items(dialogconf)
        items[-1]["callback"] = functools.partial(self.after_edit, uid)
        autoinitdialog(
            self,
            card,
            card.get("name") or "大模型",
            800,
            items,
            "gui.setting.llmcard",
            uid,
        )

    def after_edit(self, uid):
        self._normalize_card(uid)
        self.reload()

    def add_card(self):
        uid = str(uuid.uuid4())
        card = copy.deepcopy(LLM_MODEL_CARD_DEFAULT)
        card["name"] = _TR("大模型")
        globalconfig["llm_model_cards"][uid] = card
        globalconfig["llm_model_cards_rank"].append(uid)
        self.reload()
        self.edit_card(uid)

    def copy_card(self, uid):
        newuid = str(uuid.uuid4())
        card = copy.deepcopy(
            normalize_llm_model_card(globalconfig["llm_model_cards"][uid])
        )
        card["name"] = "{}_copy".format(
            card.get("name") or card.get("model") or "大模型"
        )
        globalconfig["llm_model_cards"][newuid] = card
        globalconfig["llm_model_cards_rank"].append(newuid)
        self.reload()
        self.edit_card(newuid)

    def delete_card(self, uid):
        usages = _llm_card_usages(uid)
        if usages:
            QMessageBox.information(
                self,
                _TR("无法删除"),
                _TR("当前模型卡正在使用：") + "\n" + "\n".join(usages),
            )
            return
        if not request_delete_ok(self, "llm_model_card"):
            return
        globalconfig["llm_model_cards"].pop(uid, None)
        if uid in globalconfig["llm_model_cards_rank"]:
            globalconfig["llm_model_cards_rank"].remove(uid)
        self.reload()


def setTabllmcard(self, basel: QVBoxLayout):
    basel.addWidget(LLMModelCardPage(self))

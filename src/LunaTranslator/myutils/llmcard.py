import copy

from myutils.config import globalconfig


LLM_MODEL_CARD_KEYS = {
    "API接口地址",
    "apiurl",
    "SECRET_KEY",
    "model",
    "modellistcache",
    "Temperature",
    "max_tokens",
    "top_p",
    "top_p_use",
    "frequency_penalty",
    "frequency_penalty_use",
    "reasoning_effort",
    "reasoning_effort_use",
    "thinking.type",
    "thinking.type.use",
    "use_max_completion_tokens",
    "customparams",
}

LLM_MODEL_CARD_DEFAULT = {
    "name": "大模型",
    "API接口地址": "https://api.openai.com",
    "SECRET_KEY": "",
    "model": "gpt-4o-mini",
    "modellistcache": [],
    "Temperature": 0,
    "max_tokens": 1024,
    "top_p": 0.3,
    "top_p_use": True,
    "frequency_penalty": 0,
    "frequency_penalty_use": False,
    "reasoning_effort": "medium",
    "reasoning_effort_use": False,
    "thinking.type": "disabled",
    "thinking.type.use": False,
    "use_max_completion_tokens": False,
    "customparams": [],
    "capabilities": ["text"],
}


def ensure_llm_model_cards():
    globalconfig.setdefault("llm_model_cards", {})
    globalconfig.setdefault("llm_model_cards_rank", [])
    globalconfig.setdefault("llm_migration_version", 0)


def normalize_llm_model_card(card: dict):
    normal = copy.deepcopy(LLM_MODEL_CARD_DEFAULT)
    normal.update(copy.deepcopy(card or {}))
    if not isinstance(normal.get("capabilities"), list):
        normal["capabilities"] = ["text"]
    if not normal["capabilities"]:
        normal["capabilities"] = ["text"]
    return normal


def get_llm_model_card(uid):
    ensure_llm_model_cards()
    card = globalconfig["llm_model_cards"].get(uid)
    if not isinstance(card, dict):
        return None
    return normalize_llm_model_card(card)


def resolve_llm_config(config: dict, legacy_api_key="API接口地址"):
    ensure_llm_model_cards()
    resolved = copy.deepcopy(config or {})
    if legacy_api_key != "API接口地址" and "API接口地址" not in resolved:
        resolved["API接口地址"] = resolved.get(legacy_api_key, "")
    card = get_llm_model_card(resolved.get("llm_model_card"))
    if card:
        resolved.update(card)
    else:
        for key, value in LLM_MODEL_CARD_DEFAULT.items():
            if key not in resolved:
                resolved[key] = copy.deepcopy(value)
    if legacy_api_key != "API接口地址":
        resolved[legacy_api_key] = resolved.get("API接口地址", "")
    return resolved


def ordered_llm_model_card_ids():
    ensure_llm_model_cards()
    cards = globalconfig["llm_model_cards"]
    rank = globalconfig["llm_model_cards_rank"]
    ordered = [uid for uid in rank if uid in cards]
    ordered.extend(uid for uid in cards if uid not in ordered)
    globalconfig["llm_model_cards_rank"] = ordered
    return ordered


def llm_model_card_name(uid):
    card = get_llm_model_card(uid)
    if not card:
        return uid
    return card.get("name") or card.get("model") or uid


def llm_model_card_choices(capability=None):
    ids = ordered_llm_model_card_ids()

    def matched(uid):
        if not capability:
            return True
        caps = get_llm_model_card(uid).get("capabilities", [])
        return capability in caps

    filtered = [uid for uid in ids if matched(uid)]
    if capability and not filtered:
        filtered = ids
    return [llm_model_card_name(uid) for uid in filtered], filtered

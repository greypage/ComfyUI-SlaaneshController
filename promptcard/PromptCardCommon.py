import random
from typing import Dict, List, Tuple

from .PromptCardData import PROMPT_CARD_DATA


class SlaaneshPromptCardBase:
    """Prompt 抽卡节点公共逻辑。"""

    NODE_KEY = ""
    CATEGORY = "slaaneshcontroller/promptcard"
    FUNCTION = "draw_prompt"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词")

    _CACHED_CONFIG: Dict[str, object] = {}

    @classmethod
    def _build_config(cls) -> Dict[str, object]:
        node_data = PROMPT_CARD_DATA.get(cls.NODE_KEY, {})
        raw_categories = node_data.get("categories", [])

        categories = []
        for idx, cat in enumerate(raw_categories, start=1):
            items = cat.get("items", [])
            if not items:
                continue

            label = str(cat.get("label", f"分类{idx}"))
            safe_label = label.replace("/", "／").replace("\\", "＼")
            input_key = f"启用_{idx:03d}_{safe_label}"
            categories.append({"label": label, "input_key": input_key, "items": items})

        manual_options = ["(不指定)"] + [c["label"] for c in categories]
        label_map = {c["label"]: c for c in categories}

        return {
            "categories": categories,
            "manual_options": manual_options,
            "label_map": label_map,
        }

    @classmethod
    def _get_config(cls) -> Dict[str, object]:
        cache_key = cls.NODE_KEY
        if cache_key not in cls._CACHED_CONFIG:
            cls._CACHED_CONFIG[cache_key] = cls._build_config()
        return cls._CACHED_CONFIG[cache_key]

    @classmethod
    def INPUT_TYPES(cls):
        config = cls._get_config()
        manual_options: List[str] = config["manual_options"]
        categories: List[Dict[str, object]] = config["categories"]

        required_inputs = {
            "总开关": (
                "BOOLEAN",
                {
                    "default": True,
                    "label_on": "节点开启",
                    "label_off": "节点关闭",
                    "display": "toggle",
                },
            ),
            "模式选择": (
                ["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"],
                {"default": "🎲 部分随机(手动优先)"},
            ),
            "seed": (
                "INT",
                {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1},
            ),
            "手动分类": (manual_options, {"default": "(不指定)"}),
        }

        for category in categories:
            required_inputs[category["input_key"]] = (
                "BOOLEAN",
                {
                    "default": False,
                    "label_on": "开启",
                    "label_off": "关闭",
                },
            )

        return {"required": required_inputs}

    def draw_prompt(self, **kwargs) -> Tuple[str, str]:
        if not kwargs.get("总开关", True):
            return ("", "")

        config = self.__class__._get_config()
        categories: List[Dict[str, object]] = config["categories"]
        label_map: Dict[str, Dict[str, object]] = config["label_map"]

        mode = kwargs.get("模式选择", "🎲 部分随机(手动优先)")
        manual_label = kwargs.get("手动分类", "(不指定)")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)

        enabled_categories = [
            cat for cat in categories if kwargs.get(cat["input_key"], False)
        ]

        selected_items = []

        if mode == "🔒 手动指定":
            if manual_label == "(不指定)":
                return ("", "")
            manual_cat = label_map.get(manual_label)
            if not manual_cat:
                return ("", "")
            selected_items = list(manual_cat["items"])

        elif mode == "🎲 部分随机(手动优先)":
            if manual_label != "(不指定)" and manual_label in label_map:
                selected_items = list(label_map[manual_label]["items"])
            else:
                for cat in enabled_categories:
                    selected_items.extend(cat["items"])

        else:  # 🔓 完全随机
            for cat in enabled_categories:
                selected_items.extend(cat["items"])

        if not selected_items:
            return ("", "")

        chosen = rng.choice(selected_items)
        prompt_pos = chosen.get("prompt_pos", "")
        prompt_neg = chosen.get("prompt_neg", "")
        if not isinstance(prompt_pos, str):
            return ("", "")
        if not isinstance(prompt_neg, str):
            prompt_neg = ""
        return (prompt_pos, prompt_neg)

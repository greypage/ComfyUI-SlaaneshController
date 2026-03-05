from .PromptCardCommon import SlaaneshPromptCardBase


class SlaaneshPromptCardCostume(SlaaneshPromptCardBase):
    NODE_KEY = "costume"
    CATEGORY = "slaaneshcontroller/promptcard"


NODE_CLASS_MAPPINGS = {
    "SlaaneshPromptCardCostume": SlaaneshPromptCardCostume,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshPromptCardCostume": "灵のPrompt抽卡-服装",
}

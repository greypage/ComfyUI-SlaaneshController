from .PromptCardCommon import SlaaneshPromptCardBase


class SlaaneshPromptCardFraming(SlaaneshPromptCardBase):
    NODE_KEY = "framing"
    CATEGORY = "slaaneshcontroller/promptcard"


NODE_CLASS_MAPPINGS = {
    "SlaaneshPromptCardFraming": SlaaneshPromptCardFraming,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshPromptCardFraming": "灵のPrompt抽卡-构图",
}

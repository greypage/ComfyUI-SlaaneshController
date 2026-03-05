from .PromptCardCommon import SlaaneshPromptCardBase


class SlaaneshPromptCardR18Scene(SlaaneshPromptCardBase):
    NODE_KEY = "r18_scene"
    CATEGORY = "slaaneshcontroller/promptcard"


NODE_CLASS_MAPPINGS = {
    "SlaaneshPromptCardR18Scene": SlaaneshPromptCardR18Scene,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshPromptCardR18Scene": "灵のPrompt抽卡-R18情景",
}

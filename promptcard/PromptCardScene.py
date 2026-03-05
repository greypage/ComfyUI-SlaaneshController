from .PromptCardCommon import SlaaneshPromptCardBase


class SlaaneshPromptCardScene(SlaaneshPromptCardBase):
    NODE_KEY = "scene_hint"
    CATEGORY = "slaaneshcontroller/promptcard"


NODE_CLASS_MAPPINGS = {
    "SlaaneshPromptCardScene": SlaaneshPromptCardScene,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshPromptCardScene": "灵のPrompt抽卡-场景",
}

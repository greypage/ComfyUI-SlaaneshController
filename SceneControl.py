import random
import re

# ==========================================
# 色孽の地点场景控制 (SlaaneshSceneControl) V2.3
# 更新日志:
# 1. 新增 [模式选择] 功能 (手动/部分随机/完全随机)。
# 2. 实现了风格、地点、环境细节的随机生成逻辑。
# ==========================================

# ==============================================================================
# UI 映射辅助系统
# ==============================================================================
# 全局映射字典：存储 "中文短名" -> "完整数据字符串"
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    """
    解析并注册选项
    输入: "男厕所: [public restroom], {outdoors}"
    输出: "男厕所" (并将映射存入 GLOBAL_OPTS_MAP)
    """
    if not full_text or full_text == "(不指定)":
        return "(不指定)"
    
    # 策略：以冒号 ":" 分割，取前半部分作为短名
    if ":" in full_text:
        short_name = full_text.split(":", 1)[0].strip()
    # 备用：如果没有冒号，尝试用 "[" 分割
    elif "[" in full_text:
        short_name = full_text.split("[", 1)[0].strip()
    else:
        short_name = full_text
        
    # 存入映射表
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# --------------------------------------------------------------------------------
# 数据配置区域
# --------------------------------------------------------------------------------

SCENE_DATA = {
    # 0. 风格 (Style)
    "style": [
        "(不指定)",
        "中式: [chinese style, east asian architecture, traditional chinese interior]",
        "日式: [japanese style, east asian architecture]",
        "西式: [western style, european_architecture, intricate_details]",
        "哥特: [gothic style, dark fantasy, gloomy, intricate_details]",
        "赛博: [cyberpunk, sci-fi, neon lights, high tech]",
        "现代: [modern, modern_architecture, minimalism]",
    ],
    # 1.1 室内地点 (Indoor)
    "indoor": [
        "(不指定)", 
        "室内-男厕所小便池: [public restroom, tile wall, urinal, indoors]", 
        "室内-厕所马桶隔间: [public restroom, toilet stall, toilet, indoors]", 
        "室内-浴室: [bathroom, bathtub, tiles, indoors]",
        "室内-更衣室: [locker room, indoors]",
        "室内-办公室: [office, desk, indoors]",
        "室内-医务室: [infirmary, bed, indoors]",
        "室内-卧室: [bedroom, bed, indoors]",
        "室内-厨房: [kitchen, indoors]",
        "室内-教室: [classroom, indoors]",
        "室内-酒吧: [bar (place), indoors]",
        "室内-赌场: [casino, indoors]",
        "室内-电车车厢: [train interior, indoors, commuter train]",
        "室内-监狱: [prison, prison cell, indoors]",
        "室内-地牢: [cave, dungeon, darkness, stone wall, indoors]",
        "室内-教堂: [church, cathedral, indoors]",
        "室内-公共澡堂: [public bath, bathhouse, tiling, steam, indoors]",
        "室内-图书馆隔间: [library, bookshelf, indoors]",
        "室内-祭坛仪式间: [ritual room, magic circle, candles, darkness, indoors]",
        "室内-破旧仓库: [warehouse, abandoned, dust, debris, indoors]",
        "室内-空房间: [empty room, indoors, simple background]",
    ],
    # 1.2 室外地点 (Outdoor)
    "outdoor": [
        "(不指定)", 
        "室外-阳台: [balcony, outdoors, sky]",
        "室外-天台: [rooftop, skyscraper, outdoors, city]",
        "室外-电车站/巴士站: [train station, bus stop, platform, bench, outdoors]",
        "室外-街道: [street, outdoors, city]",
        "室外-繁华都市: [cityscape, building, outdoors, crowd]",
        "室外-贫民窟: [slums, dirty, outdoors]",
        "室外-小巷: [alley, darkness, outdoors]",
        "室外-寺庙神社: [temple, shrine, outdoors]",
        "室外-废墟: [ruins, outdoors, rubble]",
        "室外-露天温泉: [onsen, rock, steam, outdoors, nature]",
        "室外-山上: [mountain, cliff, outdoors, nature]",
        "室外-沙漠: [desert, outdoors, sand]",
        "室外-海滩: [beach, palm tree, ocean, outdoors]",
        "室外-海底: [underwater, ocean, outdoors, coral]",
        "室外-草原: [grass, field, in a meadow, outdoors]",
        "室外-花海: [flower field, flowers meadows, outdoors]",
        "室外-森林: [forest, tree shade, outdoors, nature]",
        "室外-游泳池边: [swimming pool, poolside, sun loungers, outdoors]",
        "室外-公园: [park, bench, lamp, tree, outdoors]"
    ],
    # 2. 季节 (Season)
    "season": [
        "(不指定)",
        "🌸 春季: [spring (season), cherry blossoms, petals]",
        "☀️ 夏季: [summer, strong sunlight]",
        "🍂 秋季: [autumn, autumn leaves, falling leaves]",
        "❄️ 冬季: [winter, snow, cold]"
    ],
    # 3. 天气 (Weather)
    "weather": [
        "(不指定)",
        "☀️ 万里无云: [clear sky, blue sky]",
        "☀️ 烈日当空: [sunlight, lens flare, bright]",
        "☁️ 多云阴天: [cloudy, cloudy sky, overcast]",
        "🌧️ 下雨: [overcast, rain, water drop, wet]",
        "🌩️ 雷雨: [overcast, rain, water drop, cloudy, lightning]",
        "🌨️ 下雪: [snowing, snowflakes]",
        "🌫️ 雾天: [fog, misty]"
    ],
    # 4. 时间 (Time)
    "time": [
        "(不指定)",
        "🌅 黎明: [dawn, sunrise, morning, morning glow]",
        "🏙️ 白天: [day, bright light, daylight]",
        "🌇 黄昏: [sunset, golden hour, orange sky, dusk]",
        "🌃 夜晚: [night, night sky, moonlight, starry sky]",
        "🌑 深夜: [midnight, dark]"
    ]
}

class SlaaneshSceneControl:
    @classmethod
    def INPUT_TYPES(s):
        # 注册并生成 UI 列表
        ui_style = [register_opt(x) for x in SCENE_DATA["style"]]
        
        # 将室内和室外合并到一个列表中供"具体地点"选择
        all_locations_raw = SCENE_DATA["indoor"] + SCENE_DATA["outdoor"][1:] # 去重(不指定)
        ui_location_specific = [register_opt(x) for x in all_locations_raw]

        ui_season = [register_opt(x) for x in SCENE_DATA["season"]]
        ui_weather = [register_opt(x) for x in SCENE_DATA["weather"]]
        ui_time = [register_opt(x) for x in SCENE_DATA["time"]]

        return {
            "required": {
                "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}),
                "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
                
                "地点类型(必选)": (["室内", "室外"], {"default": "室内"}),
                "风格": (ui_style, {"default": "(不指定)"}),
                "具体地点(可选)": (ui_location_specific, {"default": "(不指定)"}),
                
                "季节": (ui_season, {"default": "(不指定)"}),
                "天气": (ui_weather, {"default": "(不指定)"}),
                "时间": (ui_time, {"default": "(不指定)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词")
    FUNCTION = "slaanesh_scene"
    CATEGORY = "slaaneshcontroller/scene"

    def slaanesh_scene(self, **kwargs):
        if not kwargs.get("总开关", False):
            return ("", "")

        mode = kwargs.get("模式选择", "🔒 手动指定")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        
        pos_parts = []
        neg_parts = []

        def extract(text, target="pos"):
            if not text or "(不指定)" in text: return ""
            if target == "pos":
                match = re.search(r'\[(.*?)\]', text)
                return match.group(1).strip() if match else ""
            else:
                match = re.search(r'\{(.*?)\}', text)
                return match.group(1).strip() if match else ""

        # 通用选择辅助函数
        def get_final_choice(key_in_ui, data_pool):
            manual_short = kwargs.get(key_in_ui, "(不指定)")
            manual_full = GLOBAL_OPTS_MAP.get(manual_short, manual_short)
            
            # 手动模式：直接返回用户选择
            if mode == "🔒 手动指定":
                return manual_full
            
            # 部分随机：用户指定了则用用户的，否则随机
            elif mode == "🎲 部分随机(手动优先)":
                if manual_full != "(不指定)":
                    return manual_full
                else:
                    valid_opts = [x for x in data_pool if x != "(不指定)"]
                    return rng.choice(valid_opts) if valid_opts else "(不指定)"
            
            # 完全随机：忽略用户选择，完全随机
            else:
                valid_opts = [x for x in data_pool if x != "(不指定)"]
                return rng.choice(valid_opts) if valid_opts else "(不指定)"

        # --- 1. 处理风格 (Style) ---
        style_choice = get_final_choice("风格", SCENE_DATA["style"])
        if style_choice != "(不指定)":
            p = extract(style_choice, "pos")
            if p: pos_parts.append(p)

        # --- 2. 处理地点 (Location) ---
        # 准备所有具体地点的池子（合并室内室外）
        all_locs_pool = SCENE_DATA["indoor"] + SCENE_DATA["outdoor"]
        
        loc_choice = get_final_choice("具体地点(可选)", all_locs_pool)
        
        if loc_choice != "(不指定)":
            # 如果选出了具体地点（无论是手动还是随机），使用具体地点Tag
            p = extract(loc_choice, "pos")
            n = extract(loc_choice, "neg")
            if p: pos_parts.append(p)
            if n: neg_parts.append(n)
        else:
            # 如果没有选出具体地点（通常只在手动模式且未选择时发生），使用地点类型的通用Tag
            location_type = kwargs.get("地点类型(必选)")
            location_tag_base = "indoors" if location_type == "室内" else "outdoors"
            pos_parts.append(location_tag_base)

        # --- 3. 处理环境细节 (Season, Weather, Time) ---
        # 定义配置映射: (UI键名, 数据池键名)
        env_map = [
            ("季节", "season"), 
            ("天气", "weather"), 
            ("时间", "time")
        ]

        for ui_key, pool_key in env_map:
            choice = get_final_choice(ui_key, SCENE_DATA[pool_key])
            if choice != "(不指定)":
                p = extract(choice, "pos")
                n = extract(choice, "neg")
                if p: pos_parts.append(p)
                if n: neg_parts.append(n)

        # --- 4. 拼接输出 ---
        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "
            
        return (final_pos, final_neg)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "SlaaneshSceneControl": SlaaneshSceneControl
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshSceneControl": "色孽の地点场景控制"
}

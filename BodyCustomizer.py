import random
import re

# ==============================================================================
# 色孽の女角色外观定制器 (SlaaneshBodyCustomizer) V5.9
# 更新日志:
# 1. [构图提示词] 自动同步添加到 [正面提示词] 中。
# 2. 新增输出 [面部提示词]: 提取年龄/肤色/五官/眼色等Tag，方便FaceDetailer使用。
# 3. 新增输出 [头发提示词]: 提取主要发色Tag。
# ==============================================================================

# ==============================================================================
# UI 映射辅助系统
# ==============================================================================
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    if not full_text or full_text == "(不指定)":
        return "(不指定)"
    
    if ":" in full_text:
        short_name = full_text.split(":", 1)[0].strip()
    elif "[" in full_text:
        short_name = full_text.split("[", 1)[0].strip()
    else:
        short_name = full_text
        
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# ==============================================================================
# 数据字典配置 (Body 专用)
# ==============================================================================

FEMALE_CHARACTER_DATA = {
    # 1. 种族列表
    "race": [
        "(不指定)", 
        "人类: [1girl, solo], {pointy ears, elf ears, animal ears}",
        "精灵: [1girl, elf, pointy ears, solo]", 
        "鼠娘: [1girl, mouse girl, mouse ears, mouse tail, solo]", 
        "牛娘: [1girl, cow girl, cow ears, cow tail, cow horns, solo]", 
        "猫娘: [1girl, cat girl, cat ears, cat tail, solo]", 
        "狐娘: [1girl, fox girl, fox ears, fox tail, multiple tails, animal ear fluff, kyuubi, solo]", 
        "狼娘: [1girl, wolf girl, wolf ears, wolf tail, animal ear fluff, solo]", 
        "虎娘: [1girl, tiger girl, tiger ears, tiger tail, tiger print, solo]", 
        "兔娘: [1girl, rabbit girl, rabbit ears, rabbit tail, solo]", 
        "西方龙娘: [1girl, dragon girl, dragon tail, dragon horns, dragon wings, slit pupils, solo]", 
        "中国龙娘: [1girl, eastern dragon girl, eastern dragon horns, eastern dragon tail, fur-tipped tail, solo]", 
        "拉米亚: [1girl, monster girl, lamia, scales, slit pupils, solo]",
        "马娘: [1girl, horse girl, horse ears, horse tail, solo]", 
        "羊娘: [1girl, sheep girl, sheep ears, sheep horns, solo]",
        "哈比: [1girl, monster girl, harpy, feathered wings, winged arms, claws, talons, solo]", 
        "犬娘: [1girl, dog girl, dog ears, ears down, dog tail, solo]",
        "天使: [1girl, angel, angle wings, halo, feathered wings, solo]", 
        "堕天使: [1girl, angel, angle wings, black wings, red halo, feathered wings, solo]", 
        "魅魔: [1girl, succubus, goat horns, demon tail, demon wings, low wings, solo]",
        "吸血鬼: [1girl, vampire, fang, pointy ears, demon wings, low wings, solo]",
        "美人鱼: [1girl, monster girl, mermaid, fish tail, head fins, solo]",    
        "机娘: [1girl, android, mechanical arms, mechanical legs, robot joints, solo]",   
        "鬼娘: [1girl, oni, oni horns, solo]", 
    ],
    # 2. 年龄段
    "age": [
        "(不指定)", 
        "萝莉: [loli, oppai loli, aged down, petite, embedding:lazyloli]", 
        "少女: [bishoujo, curvy]", 
        "熟女: [mature female, aged up, curvy, plump], {embedding:lazyloli}"
    ],
    # 3. 主要发型
    "mainhairstyle": [
        "(不指定)", 
        "中式盘发髻: [long hair, hair up, updo]",
        "中式少女髻: [short hair, hair bun, double bun, hair rings]",
        "短发: [short hair]", 
        "短波浪: [short hair, wavy hair]", 
        "波波头: [medium hair, bob cut]", 
        "狼尾剪: [medium hair, wolf cut]", 
        "长直发: [long hair, straight hair]", 
        "长直半扎发: [long hair, half updo]", 
        "人妻发型: [medium hair, low-tied long hair]", 
        "长波浪: [long hair, wavy hair]", 
        "长高马尾: [long hair, high ponytail]",
        "短高马尾: [short hair, high ponytail]",
        "长侧马尾: [long hair, side ponytail]", 
        "短侧马尾: [short hair, side ponytail]", 
        "长低马尾: [long hair, low ponytail]", 
        "低马尾编发: [long hair, braided ponytail]", 
        "高双马尾: [twintails]", 
        "低双马尾: [low twintails]", 
        "低双马尾编发: [twin braids]"
    ],
    # 4. 刘海样式
    "bangs": [
        "(不指定)", 
        "齐刘海: [blunt bangs]",
        "中分刘海: [parted bangs]", 
        "双分齐刘海: [center-flap bangs]", 
        "双分散刘海: [double-parted bangs, asymmetric bangs]", 
        "侧分刘海: [swept bangs, asymmetric bangs]", 
        "交叉刘海: [crossed bangs, hair between eyes]", 
        "长刘海: [long bangs, hair between eyes]",
        "窗帘发: [asymmetric bangs, curtained hair]", 
        "单边窗帘发: [asymmetric bangs, curtained hair, widow's peak]", 
        "姬切: [hime cut]",     
        "碎刘海: [choppy bangs]",
        "斜刘海: [diagonal bangs]", 
        "弧线刘海: [arched bangs]",   
        "背头: [bangs pinned back, widow's peak]"
    ],
    # 5. 辅助发型特征1
    "subhairstyle1": [
        "(不指定)", 
        "进气口发型: [hair intakes]",
        "中式发冠: [topknot]", 
        "卷发梢: [curly hair]", 
        "单侧小马尾: [one side up]", 
        "双边小马尾: [two side up]", 
        "超长发: [very long hair]", 
        "及地长发: [absurdly long hair]", 
        "螺旋钻: [drill hair, drill sidelocks, curly hair]",
        "侧发髻: [hair bun, single hair bun]", 
        "丸子头: [hair bun, double bun]", 
        "法式编发: [french braid]",
        "编发发髻: [braided bun]", 
        "侧发: [sidelocks]",
        "长侧发: [long sidelocks]", 
        "低绑侧发: [low-tied sidelocks]", 
        "单边侧发: [single sidelocks]", 
        "编发侧发: [braided sidelocks]", 
        "呆毛: [ahoge]", 
        "长呆毛: [huge ahoge]", 
        "侧呆毛: [side ahoge]", 
        "蟑螂呆毛: [antenna hair]", 
        "发翼: [hair flaps]", 
        "遮住双眼: [hair over eyes, eyes visible through hair]", 
        "遮住单眼: [hair over one eye, eyes visible through hair]", 
        "耳后发: [hair behind ear]",
        "辫子刘海: [braided bangs]", 
        "凌乱头发: [messy hair]",
        "飘逸头发: [floating hair]",
    ],
    # 6. 辅助发型特征2
    "subhairstyle2": [
        "(不指定)", 
        "进气口发型: [hair intakes]",
        "中式发冠: [topknot]", 
        "卷发梢: [curly hair]", 
        "单侧小马尾: [one side up]", 
        "双边小马尾: [two side up]", 
        "超长发: [very long hair]", 
        "及地长发: [absurdly long hair]", 
        "螺旋钻: [drill hair, drill sidelocks, curly hair]",
        "侧发髻: [hair bun, single hair bun]", 
        "丸子头: [hair bun, double bun]", 
        "法式编发: [french braid]",
        "编发发髻: [braided bun]", 
        "侧发: [sidelocks]",
        "长侧发: [long sidelocks]", 
        "低绑侧发: [low-tied sidelocks]", 
        "单边侧发: [single sidelocks]", 
        "编发侧发: [braided sidelocks]", 
        "呆毛: [ahoge]", 
        "长呆毛: [huge ahoge]", 
        "侧呆毛: [side ahoge]", 
        "蟑螂呆毛: [antenna hair]", 
        "发翼: [hair flaps]", 
        "遮住双眼: [hair over eyes, eyes visible through hair]", 
        "遮住单眼: [hair over one eye, eyes visible through hair]", 
        "耳后发: [hair behind ear]",
        "辫子刘海: [braided bangs]", 
        "凌乱头发: [messy hair]",
        "飘逸头发: [floating hair]",
    ],  
    # 6.5. 辅助发型特征3
    "subhairstyle3": [
        "(不指定)", 
        "进气口发型: [hair intakes]",
        "中式发冠: [topknot]", 
        "卷发梢: [curly hair]", 
        "单侧小马尾: [one side up]", 
        "双边小马尾: [two side up]", 
        "超长发: [very long hair]", 
        "及地长发: [absurdly long hair]", 
        "螺旋钻: [drill hair, drill sidelocks, curly hair]",
        "侧发髻: [hair bun, single hair bun]", 
        "丸子头: [hair bun, double bun]", 
        "法式编发: [french braid]",
        "编发发髻: [braided bun]", 
        "侧发: [sidelocks]",
        "长侧发: [long sidelocks]", 
        "低绑侧发: [low-tied sidelocks]", 
        "单边侧发: [single sidelocks]", 
        "编发侧发: [braided sidelocks]", 
        "呆毛: [ahoge]", 
        "长呆毛: [huge ahoge]", 
        "侧呆毛: [side ahoge]", 
        "蟑螂呆毛: [antenna hair]", 
        "发翼: [hair flaps]", 
        "遮住双眼: [hair over eyes, eyes visible through hair]", 
        "遮住单眼: [hair over one eye, eyes visible through hair]", 
        "耳后发: [hair behind ear]",
        "辫子刘海: [braided bangs]", 
        "凌乱头发: [messy hair]",
        "飘逸头发: [floating hair]",
    ],           
    # 7. 特殊发色
    "hairspecial": [
        "(不指定)", 
        "渐变发色: [gradient hair]", 
        "五颜六色: [multicolored hair]",
        "挑染: [streaked hair]", 
        "内层染发: [colored inner hair]" 
    ],      
    # 7.5 眉毛特征
    "eyebrows": [
        "(不指定)", 
        "短眉: [short eyebrows]", 
        "微浓眉: [eyebrows]", 
        "浓眉: [thick eyebrows]",
        "分叉眉: [forked eyebrows]"
    ],      
    # 8.1 嘴唇特征
    "lips": [
        "(不指定)", 
        "性感唇: [lips]", 
        "厚唇: [thick lips]"
    ],
    # 8.2 痣的位置
    "mole": [
        "(不指定)", 
        "泪痣: [mole under eye]", 
        "美人痣: [mole under mouth]",
    ],
    # 12. 眼角形状
    "eyeshape": [
        "(不指定)", 
        "眼角下垂: [tareme]", 
        "眼角上翘: [tsurime]"
    ],   
    # 12.5 眼睛（基础标签）
    "eyes": [ 
        "眼睛: [eyes]", 
    ],
    # 13. 肤色
    "regularskin": [
        "(不指定)", 
        "雪白: [fair skin]", 
        "褐肤: [dark skin]"
    ],    
    # 15. 胸围大小
    "breast": [
        "(不指定)", 
        "贫乳A cup: [flat chest]", 
        "微乳B cup: [small breasts]", 
        "常乳D cup: [medium breasts]",
        "巨乳E cup: [large breasts]", 
        "爆乳G cup: [huge breasts]", 
        "超乳I cup: [gigantic breasts]"
    ],    
    # 15.1 乳头特征 (手动)
    "nipples": [
        "(不指定)",
        "不露出: {nipples, covered nipples}",
        "乳晕露出: [areola slip]",
        "正常乳头: [breasts out, nipples]",
        "衣服下乳头: [areola slip, covered nipples]",
        "巨大乳头: [breasts out, nipples, huge nipples, puffy nipples, large areolae]",
        "衣服大乳头: [areola slip, covered nipples, huge nipples, puffy nipples, large areolae]",
        "内陷乳头: [breasts out, nipples, inverted nipples, large areolae]",
        "深色乳头: [breasts out, nipples, huge nipples, puffy nipples, dark nipples, large areolae]"
    ],
    # 15.3 下垂特征 (手动)
    "breastsagging": [
        "(不指定)",
        "下垂: [sagging breasts, breasts apart]"
    ],
    # 15.4 腰部特征
    "waist": [
        "(不指定)",
        "纤腰: [narrow waist]"
    ],
    # 15.5 臀围特征
    "hips": [
        "(不指定)",
        "肥臀: [wide hips]"
    ],
    # 15.5.0 腿部特征
    "thighs": [
        "(不指定)",
        "肉腿: [thick thighs]"
    ],
    # 15.5.X 腿长特征
    "longlegs": [
        "(不指定)",
        "长腿: [long legs]",
    ],
    # 15.5.1 阴部特征 (手动)
    "vulva": [
        "(不指定)", 
        "一线天: [cleft of venus]",
        "馒头屄: [cleft of venus, puffy vulva]",
        "石榴屄: [puffy vulva, labia, clitoris]",
        "蝴蝶屄: [puffy vulva, long labia, clitoris]",
        "黑木耳: [puffy vulva, long labia, dark labia, clitoris]",
    ],
    # 15.5.2 阴毛特征 (手动)
    "pubichair": [
        "(不指定)", 
        "无毛白虎: {(female pubic hair:1.2)}",
        "稀疏阴毛: [female pubic hair, sparse pubic hair]",
        "浓密阴毛: [female pubic hair, excessive pubic hair]",
    ],
    # 15.6 怀孕特征 (手动)
    "pregnancy": [
        "(不指定)", 
        "怀孕: [pregnant]"
    ],
}

# 颜色数据拆分
COLOR_DATA = {
    # 头发专用
    "haircolor": [
        "(不指定)", 
        "🔴红色: [red]", "🔴深红色: [darkred]", "🔴绯红色: [crimson]",
        "🟠橙色: [orange]", "🟡金色: [blonde]", 
        "🟢淡绿色: [lightgreen]", "🟢墨绿色: [darkgreen]", "🟢🔵青色: [aqua]", 
        "🔵淡蓝色: [lightblue]", "🔵深蓝色: [darkblue]", "🔵🟣靛蓝色: [indigo]",
        "🟣淡紫色: [lightpurple]", "🟣深紫色: [darkpurple]", 
        "🩷淡粉色: [lightpink]", "🩷深粉色: [dark pink]", 
        "🟤深棕色: [brown]", "🟤⚪浅棕色: [light brown]", "🟤⚪⚪米色: [beige]", "🟤🔴栗色: [maroon]", 
        "⚪🟡白金色: [platinum blonde]", "⚪🩶银色: [silver]", "🩶灰色: [grey]", 
        "⚪白色: [white]", "⚫黑色: [black]", 
    ],
    # 眼睛专用
    "eyecolor": [
        "(不指定)", 
        "🔴红色: [red]", "🔴绯红色: [crimson]",
        "🟠橙色: [orange]", "🟠琥珀色: [amber]", "🟡黄色: [yellow]", 
        "🟢绿色: [green]", "🟢🔵青色: [aqua]", "🔵蓝色: [blue]", 
        "🟣紫色: [purple]", "🩷粉色: [pink]", 
        "🟤棕色: [brown]", "🩶灰色: [grey]", 
        "⚪白色: [white]", "⚫黑色: [black]", 
    ]
}

# 数据合并
CONSOLIDATED_DATA = {
    "FEMALE_CHARACTER_DATA": FEMALE_CHARACTER_DATA,
    "haircolor": COLOR_DATA["haircolor"],
    "eyecolor": COLOR_DATA["eyecolor"]
}

# ==============================================================================
# 配置列表
# ==============================================================================
APPEARANCE_CONFIG = [
    ("race", "种族", None, None, None, 1.0, 0.0),
    ("age", "年龄段", None, None, None, 0.75, 0.0),
    ("regularskin", "肤色", None, None, None, 0.15, 0.0),
    # 引用 haircolor 池
    ("mainhairstyle", "主要发型", "mainhaircolor", "主要发色", "haircolor", 1.0, 1.0),
    ("bangs", "刘海样式", None, None, None, 0.9, 0.0),
    ("subhairstyle1", "辅助发型1", None, None, None, 0.9, 0.0),
    ("subhairstyle2", "辅助发型2", None, None, None, 0.9, 0.0),
    ("subhairstyle3", "辅助发型3", None, None, None, 0.9, 0.0),
    ("hairspecial", "特殊发色", None, None, None, 0.8, 0.0),
    ("eyebrows", "眉毛特征", None, None, None, 0.8, 0.0),
    ("eyeshape", "眼角形状", None, None, None, 0.6, 0.0),
    # 引用 eyecolor 池
    ("eyes", "眼睛", "eyecolor", "眼睛颜色", "eyecolor", 1.0, 1.0),
    ("lips", "嘴唇特征", None, None, None, 0.3, 0.0),
    ("mole", "痣", None, None, None, 0.6, 0.0),
    ("breast", "胸围", None, None, None, 0.8, 0.0),
    ("waist", "腰围", None, None, None, 0.5, 0.0),
    ("hips", "臀围", None, None, None, 0.5, 0.0),
    ("thighs", "肉腿", None, None, None, 0.5, 0.0),
    ("longlegs", "长腿", None, None, None, 0.5, 0.0),
    ("breastsagging", "胸部状态(手动)", None, None, None, 0.0, 0.0),
    ("nipples", "乳头特征(手动)", None, None, None, 0.0, 0.0),
    ("vulva", "阴部特征(手动)", None, None, None, 0.0, 0.0),
    ("pubichair", "阴毛特征(手动)", None, None, None, 0.0, 0.0),
    ("pregnancy", "怀孕(手动)", None, None, None, 0.0, 0.0),
]

# ==============================================================================
# 通用辅助函数
# ==============================================================================
def extract_tag(text, target="pos"):
    if not text or "(不指定)" in text: return ""
    if target == "pos":
        match = re.search(r'\[(.*?)\]', text)
        return match.group(1).strip() if match else ""
    else:
        match = re.search(r'\{(.*?)\}', text)
        return match.group(1).strip() if match else ""

def enforce_str(tag):
    return tag if tag else ""

def filter_content(text, banned_list):
    """
    过滤掉包含屏蔽词的Tag，同时防止误杀 (如屏蔽 tail 误杀 ponytail)
    """
    if not text or not banned_list:
        return text
    
    tags = [t.strip() for t in text.split(',')]
    filtered_tags = []
    
    for t in tags:
        should_block = False
        t_lower = t.lower()
        for banned in banned_list:
            if banned in t_lower:
                # --- 防误杀白名单逻辑 ---
                if banned == "tail" and ("ponytail" in t_lower or "twintails" in t_lower):
                    continue # 豁免马尾辫
                
                if banned == "ear" or banned == "ears":
                    if "earrings" in t_lower or "heart" in t_lower or "pearl" in t_lower or "wear" in t_lower:
                        continue # 豁免耳环、心形、珍珠、穿着
                
                # 如果没被豁免，且包含了屏蔽词，则标记为屏蔽
                should_block = True
                break
        
        if not should_block:
            filtered_tags.append(t)
            
    return ", ".join(filtered_tags)

# ==============================================================================
# 节点类: 外观定制器
# ==============================================================================
class SlaaneshBodyCustomizer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        required_inputs = {
            "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
            "18x模式": ("BOOLEAN", {"default": True, "label_on": "开启", "label_off": "关闭", "display": "toggle"}),
            "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
            "出图模式": (["头像 (Portrait)", "上半身 (Upper Body)", "胸像 (Breast Focus)", "中景 (Cowboy Shot)", "下半身 (Lower Body)", "全身 (Full Body)"], {"default": "全身 (Full Body)"}),
        }

        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source, _, _ in APPEARANCE_CONFIG:
            if item_en_key != "eyes":
                raw_list = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
                ui_list = [register_opt(x) for x in raw_list]
                required_inputs[item_cn_key] = (ui_list,)
            
            if color_cn_key:
                raw_color_list = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                ui_color_list = [register_opt(x) for x in raw_color_list]
                required_inputs[color_cn_key] = (ui_color_list,)

        return {"required": required_inputs}

    # [修改] 增加了第6个输出类型
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    # [修改] 调整了顺序并增加了第6个输出名称
    RETURN_NAMES = ("正面提示词", "负面提示词", "构图提示词", "头发提示词", "面部提示词", "眼睛提示词")
    FUNCTION = "process_body"
    CATEGORY = "slaaneshcontroller/character"

    def process_body(self, **kwargs):
        # [修改] 返回值增加了一个空字符串占位
        if not kwargs.get("总开关", False): return ("", "", "", "", "", "")
        
        pos_parts = []
        neg_parts = []
        face_parts = [] 
        hair_parts = [] # 用于存储头发相关的提示词
        eye_parts = []  # [新增] 用于存储眼睛相关的提示词
        
        mode = kwargs.get("模式选择", "🔒 手动指定")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        shot_mode = kwargs.get("出图模式", "全身 (Full Body)")
        enable_18x = kwargs.get("18x模式", True)
        
        # 1. 生成构图提示词 Tag
        shot_tag = ""
        if "头像" in shot_mode:
            shot_tag = "(face focus, close-up_face:1.2)"
        elif "上半身" in shot_mode:
            shot_tag = "(upper body:1.1)"
        elif "胸像" in shot_mode:
            shot_tag = "(breast focus:1.1)"
        elif "中景" in shot_mode:
            shot_tag = "(cowboy shot:1.1)"
        elif "下半身" in shot_mode:
            shot_tag = "(lower body:1.1)"
        else: # 全身
            shot_tag = "(full body:1.2)"
        
        comp_prompt = shot_tag + ", "
        pos_parts.append(shot_tag)

        # 2. 定义身体屏蔽列表
        blocked_items = []
        if "头像" in shot_mode:
            blocked_items = ["longlegs", "thighs", "vulva", "pubichair", "hips", "waist"]
        elif "上半身" in shot_mode:
            blocked_items = ["longlegs", "thighs", "vulva", "pubichair", "hips"]
        elif "胸像" in shot_mode:
            blocked_items = ["longlegs", "bangs", "subhairstyle1", "subhairstyle2", "subhairstyle3", "hairspecial", "eyebrows", "eyeshape", "eyes", "lips", "mole"]
        elif "下半身" in shot_mode:
            blocked_items = ["bangs", "subhairstyle1", "subhairstyle2", "subhairstyle3", "hairspecial", "eyebrows", "eyeshape", "eyes", "lips", "mole"]
        elif "中景" in shot_mode:
            blocked_items = ["longlegs"]

        # 3. 定义内容屏蔽列表
        content_mask_list = []
        if "胸像" in shot_mode or "下半身" in shot_mode:
            content_mask_list.extend(["ears", "ear fluff", "horns", "halo", "pupils", "fins"])
        
        if "头像" in shot_mode:
            content_mask_list.append("tail")

        # 4. 18x
        if enable_18x:
            pos_parts.append("embedding:lazynsfw")
        else:
            neg_parts.append("embedding:lazynsfw")

        # 5. 定义面部特征 Key 列表
        face_feature_keys = ["regularskin", "eyebrows", "eyeshape", "lips", "mole"]

        # 6. 遍历配置
        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source, item_prob, color_prob in APPEARANCE_CONFIG:
            
            if item_en_key in blocked_items:
                continue

            item_manual_choice_short = kwargs.get(item_cn_key, "(不指定)")
            item_manual_choice = GLOBAL_OPTS_MAP.get(item_manual_choice_short, item_manual_choice_short)

            if item_prob == 0.0:
                if item_manual_choice != "(不指定)":
                    p = extract_tag(item_manual_choice, "pos")
                    n = extract_tag(item_manual_choice, "neg")
                    if p: 
                        p_filtered = filter_content(p, content_mask_list)
                        pos_parts.append(p_filtered)
                        if item_en_key in face_feature_keys:
                            face_parts.append(p_filtered)
                    if n: neg_parts.append(n)
                continue

            item_data_list = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
            raw_item_text = ""
            is_manual = item_manual_choice != "(不指定)"

            if item_en_key != "eyes": 
                if mode == "🔒 手动指定" or (mode == "🎲 部分随机(手动优先)" and is_manual):
                    raw_item_text = item_manual_choice
                elif mode != "🔒 手动指定" and not is_manual:
                    if rng.random() < item_prob and len(item_data_list) > 1:
                        raw_item_text = rng.choice(item_data_list[1:])
            
            raw_color_text = ""
            if color_en_key:
                color_data_list = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                color_manual_choice_short = kwargs.get(color_cn_key, "(不指定)")
                color_manual_choice = GLOBAL_OPTS_MAP.get(color_manual_choice_short, color_manual_choice_short)
                
                if mode == "🔒 手动指定" or (mode == "🎲 部分随机(手动优先)" and color_manual_choice != "(不指定)"):
                    raw_color_text = color_manual_choice
                elif mode != "🔒 手动指定" and (raw_item_text or item_en_key == "eyes") and rng.random() < color_prob:
                    raw_color_text = rng.choice(color_data_list[1:])

            p_item = extract_tag(raw_item_text, "pos")
            p_color = extract_tag(raw_color_text, "pos")

            if content_mask_list:
                p_item = filter_content(p_item, content_mask_list)

            if item_en_key == "eyes" and (p_color or is_manual):
                p_item = "eyes"

            combined_pos = ""
            if color_en_key == 'mainhaircolor' and p_color:
                # 头发逻辑
                hair_tag = enforce_str(f"{p_color} hair")
                pos_parts.append(hair_tag)
                # 将生成的发色Tag加入专门的列表
                hair_parts.append(hair_tag) 
                combined_pos = p_item
            else:
                if p_color and p_item:
                    combined_pos = f"{p_color} {p_item}"
                else:
                    combined_pos = p_color or p_item
            
            if combined_pos: 
                pos_parts.append(enforce_str(combined_pos))
                if item_en_key in face_feature_keys or item_en_key == "eyes":
                    face_parts.append(enforce_str(combined_pos))
                
                # [新增] 眼睛单独输出逻辑
                if item_en_key == "eyes":
                    eye_parts.append(enforce_str(combined_pos))

            n_item = extract_tag(raw_item_text, "neg")
            n_color = extract_tag(raw_color_text, "neg")
            if n_item: neg_parts.append(n_item)
            if n_color: neg_parts.append(n_color)

        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        final_face = ", ".join(filter(None, face_parts))
        final_hair = ", ".join(filter(None, hair_parts))
        final_eyes = ", ".join(filter(None, eye_parts)) # [新增]
        
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "
        if final_face: final_face += ", "
        if final_hair: final_hair += ", "
        if final_eyes: final_eyes += ", " # [新增]

        # [修改] 更新返回顺序：头发 -> 面部 -> 眼睛
        return (final_pos, final_neg, comp_prompt, final_hair, final_face, final_eyes)

NODE_CLASS_MAPPINGS = { "SlaaneshBodyCustomizer": SlaaneshBodyCustomizer }
NODE_DISPLAY_NAME_MAPPINGS = { "SlaaneshBodyCustomizer": "色孽の女角色外观定制器" }

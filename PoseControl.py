import random
import re

# ==========================================
# 色孽の常规姿势控制 (SlaaneshPoseControl) V4.6
# 1. UI优化：下拉菜单只显示中文，后台自动映射完整Prompt
# 2. 数据清洗：移除了键名中的冒号 (例如 "站立[standing]")
# 3. 逻辑适配：支持短名输入->长名解析
# ==========================================

# ==============================================================================
# UI 映射辅助系统 (新增)
# ==============================================================================
# 全局映射字典：存储 "中文短名" -> "完整数据字符串"
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    """
    解析并注册选项
    输入: "站立[standing]"
    输出: "站立" (并将映射存入 GLOBAL_OPTS_MAP)
    """
    if not full_text or full_text == "(不指定)":
        return "(不指定)"
    
    # 截取 [ 之前的内容作为短名
    short_name = full_text.split('[')[0].strip()
    
    # 如果没有 [，说明本身就是短名或者格式不对，直接存
    if short_name == full_text:
        GLOBAL_OPTS_MAP[full_text] = full_text
        return full_text
        
    # 存入映射表
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# --------------------------------------------------------------------------------
# 数据配置区域 (已去除冒号)
# --------------------------------------------------------------------------------

POSE_DATA = {
    # 统一使用 group0_basic 和 group1_suit 键名
    "group0_basic": [
        "(不指定)", 
        "站立[standing]", 
        "正常坐[sitting]", 
        "斜躺[reclining]", 
        "仰卧[lying, on back]", 
        "侧卧[lying, on side]", 
        "趴着[lying, on stomach]", 
    ],
    "group1_suit": [
        "(不指定)", 
        "站立一字马[standing split, leg up]", #锁腿
        "地板一字马[sitting, split, spread legs]", #锁腿
        "分开腿站立[standing, legs apart, contrapposto]", #锁腿
        "性感站立[standing, legs apart, contrapposto, arched back]", #锁腿
        "交叉腿站立[standing, crossed legs]", #锁腿
        "并拢腿站立[standing, legs together]", #锁腿
        "抱膝坐[sitting, hugging own legs, knees to chest]", #锁腿
        "单腿抬起坐[sitting, leg up]", #锁腿
        "鸭子坐[sitting, wariza]", #锁腿
        "盘腿坐[sitting, indian style]", #锁腿
        "二郎腿[sitting, crossed legs]", #锁腿
        "正坐[kneeling, legs together]", #锁腿
        "跪坐[kneeling, legs apart]", #锁腿
        "单膝跪地[on one knee]", #锁腿
        "开腿半蹲[bowlegged pose, legs apart]", #锁腿
        "并拢腿蹲[squatting, legs together]", #锁腿
        "分开腿蹲[squatting, legs apart]", #锁腿
        "等待种付[lying, on back, legs up, folded]", #锁腿
        "四肢着地[all fours]", #锁腿
        "走路[walking, crossed legs]", #锁腿
        "奔跑[running, dynamic pose]", #锁腿
    ],
    "body": [
        "(不指定)", 
        "前倾[leaning forward, bent over]", 
        "后仰[leaning back]", 
        "靠一边[leaning to the side, reclining]",
        "靠墙[against wall]"
    ],
    "face_direction": [
        "(不指定)", 
        "正脸[portrait]", 
        "侧脸[profile]",
        "歪头[head tilt]",
    ],
    "eye1": [
        "(不指定)", 
        "看观众[looking at viewer]", 
        "向下看[looking down]", 
        "向上看[looking up]",
        "看别处[looking away]", 
        "回眸[looking back]", 
        "翻白眼[rolling eyes]", 
        "瞳孔收缩[wide-eyed]", 
        "轻蔑半月眼[jitome]", 
        "眯眼[narrowed eyes]",
        "半闭眼眼[half-closed eyes]", 
        "闭眼[closed eyes]", 
        "闭一只眼[one eye closed]",
        "空洞双眼[empty eyes]",
        "斗鸡眼[cross eyed]"
    ],
    "eye2": [
        "(不指定)", 
        "看观众[looking at viewer]", 
        "向下看[looking down]", 
        "向上看[looking up]",
        "看别处[looking away]", 
        "回眸[looking back]", 
        "翻白眼[rolling eyes]", 
        "瞳孔收缩[wide-eyed]", 
        "轻蔑半月眼[jitome]", 
        "眯眼[narrowed eyes]",
        "半闭眼眼[half-closed eyes]", 
        "闭眼[closed eyes]", 
        "闭一只眼[one eye closed]",
        "空洞双眼[empty eyes]",
        "斗鸡眼[cross eyed]"
    ],
    "eyebrow": [
        "(不指定)", 
        "V字眉[v-shaped eyebrows]", 
        "八字眉[raised eyebrows]", 
        "皱眉[frown]",
        "微微皱眉[light frown]", 
        "皱眉蹙额[wince]"
    ],
    "expressions": [
        "(不指定)", 
        "😑 面无表情[expressionless]", 
        "😑 惊讶[:o]", 
        "😑 点嘴[dot mouth]", 
        "😑 栗子嘴[chestnut mouth]", 
        "😑 撅嘴[puckered lips]", 
        "😊 微笑[smile, closed mouth]", 
        "😊 大笑[smile, :d]", 
        "😊 魅惑笑[seductive smile, parted lips]", 
        "😊 咧嘴笑[grin]", 
        "😊 冷笑[evil smile]", 
        "😊 狂笑[evil smile, laughing]", 
        "😊 猫嘴[smug, :3]", 
        "😊 舌头舔上唇[:q]", 
        "😊 吐舌[:p]", 
        "😊 张嘴伸舌头[tongue out, :o]", 
        "🥰 害羞脸红[shy, embarrased, closed mouth, blush]", 
        "🥰 慌张[shy, flustered, open mouth, blush]", 
        "🥰 飞吻媚眼[one eye closed, parted lips, blowing kiss]", 
        "🥰 傲娇嘟嘴[tsundere, pout]", 
        "😍 花痴脸[heart-shaped mouth, smile, mouth drool, blush, nose blush]", 
        "😭 哭泣[crying, tear, sad]", 
        "😭 绝望[despair, empty eyes, expressionless, shaded face]", 
        "😠 不开心[:<]", 
        "😠 负面: 严肃皱眉[angry, frown, closed mouth]", 
        "😠 负面: 严肃怒吼[angry, frown, open mouth]", 
        "😠 负面: 咬牙切齿[angry, frown, clenched teeth]", 
    ],
    "hands1": [
        "(不指定)", 
        "手指比心[finger heart, hand up]", 
        "小腹双手比心[heart hands, 4-finger heart hands, hands on own stomach]", 
        "胸前双手比心[heart hands, 4-finger heart hands, hands on own chest]",  
        "双臂头顶比心[heart arms, arms up]", 
        "竖中指[middle finger]", 
        "双手竖中指[double middle finger]",  
        "比耶[v, hand up]", 
        "双手比耶[double v, hands up]",   
        "点赞[thumbs up, hand up]", 
        "双手点赞[thumbs up, hands up]", 
        "OK手势[ok sign, hand up]", 
        "嘘[shushing, finger to mouth]", 
        "手指贴脸颊[finger to cheek]", 
        "手指抵下巴[finger to own chin]", 
        "敬礼[salute, arm up]", 
        "祈祷[praying, interlocked fingers]", 
        "双手交叠[own hands together, hands on own stomach]", 
        "双手交叠[own hands together, hands on own chest]", 
        "小腹指尖抵着指尖[steepled fingers, hands on own stomach]", 
        "胸前指尖抵着指尖[steepled fingers, hands on own chest]", 
        "双手爪子手势[claw pose, hands up]", 
        "爪子手势[claw pose, hand up]", 
        "双手招财猫手[paw pose, hands up]", 
        "招财猫手[paw pose, hand up]", 
        "兔耳朵手[rabbit pose, hands up]", 
        "手枪手势[finger gun, index finger raised, hand up]", 
        "手放嘴边[hand to mouth]", 
        "摸下巴[hand on own chin]", 
        "捧脸颊[hand on own cheek]", 
        "双手捧脸颊[hands on own cheeks]", 
        "捂嘴[hand over own mouth, covered mouth]", 
        "双手捂嘴[hands over own mouth, covered mouth]", 
        "双手放胸上[hands on own chest]", 
        "手放胸上[hand on own chest]", 
        "双手放小腹[hands on own stomach]", 
        "手放小腹[hand on own stomach]", 
        "双手放膝盖[hands on own knees]", 
        "手放膝盖[hand on own knee]", 
        "双手叉腰[hands on own hips]", 
        "单手叉腰[hand on own hip]", 
        "双手放大腿[hands on own thighs]", 
        "手放大腿[hand on own thigh]", 
        "双手放肩膀[hands on own shoulders]", 
        "摸肩膀[hand on own shoulder]", 
        "双手摸屁股[hands on own ass]", 
        "摸屁股[hand on own ass]", 
        "双腿之间的双手[hands between legs]", 
        "双腿之间的手[hand between legs]", 
        "双手抱胸[crossed arms]",  
        "张开双臂[outstretched arms]", 
        "双手放在脑后[arms behind head]", 
        "双手放在身后[arms behind back]", 
        "拉伸[stretching]", 
        "双手插兜[hands in pockets]", 
        "手插兜[hand in pocket]", 
        "双臂自然下垂[arms at side]", 
        "手臂自然下垂[arm at side]", 
        "双手抬起[hands up, w arms]", 
        "单手抬起[hand up]", 
        "单臂抬起[arm up]", 
        "招手[waving]", 
        "双手撩头发[arms behind head, hands in own hair, tucking hair]", 
        "单手撩头发[hand in own hair, tucking hair]", 
        "卷头发[twirling hair]", 
        "掀裙子[skirt lift, lifting own clothes]", 
        "揉自己胸[grabbing own breast]", 
        "调整眼镜[adjusting eyewear]", 
        "伸手/邀请[reaching towards viewer]", 
        "指着观众[pointing at viewer]", 
    ],
    "hands2": [
        "(不指定)", 
        "手指比心[finger heart, hand up]", 
        "竖中指[middle finger]", 
        "比耶[v, hand up]", 
        "点赞[thumbs up, hand up]", 
        "OK手势[ok sign, hand up]", 
        "嘘[shushing, finger to mouth]", 
        "手指贴脸颊[finger to cheek]", 
        "手指抵下巴[finger to own chin]", 
        "敬礼[salute, arm up]", 
        "爪子手势[claw pose, hand up]", 
        "招财猫手[paw pose, hand up]", 
        "手枪手势[finger gun, index finger raised, hand up]", 
        "手放嘴边[hand to mouth]", 
        "摸下巴[hand on own chin]", 
        "捧脸颊[hand on own cheek]", 
        "捂嘴[hand over own mouth, covered mouth]", 
        "手放胸上[hand on own chest]", 
        "手放小腹[hand on own stomach]", 
        "手放膝盖[hand on own knee]", 
        "单手叉腰[hand on own hip]", 
        "手放大腿[hand on own thigh]", 
        "摸肩膀[hand on own shoulder]", 
        "摸屁股[hand on own ass]", 
        "双腿之间的手[hand between legs]", 
        "手插兜[hand in pocket]", 
        "手臂自然下垂[arm at side]", 
        "单手抬起[hand up]", 
        "单臂抬起[arm up]", 
        "招手[waving]", 
        "单手撩头发[hand in own hair, tucking hair]", 
        "卷头发[twirling hair]", 
        "掀裙子[skirt lift, lifting own clothes]", 
        "揉自己胸[grabbing own breast]", 
        "调整眼镜[adjusting eyewear]", 
        "伸手/邀请[reaching towards viewer]", 
        "指着观众[pointing at viewer]", 
    ],
    "legs": [
        "(不指定)", 
        "腿并拢[legs together]", 
        "腿分开[legs apart]", 
        "腿交叉[crossed legs]", 
        "膝盖合并两脚分开[knees together feet apart]", 
        "单腿抬起[leg up]", 
        "膝盖顶到胸[knees to chest]", 
        "膝盖抬起[knee up]", 
        "单脚抬起[foot up]", 
        "内八字[pigeon-toed]", 
        "M字腿[m legs]", 
        "腿岔开[spread legs]"
    ],
    "wet": [
        "(不指定)", 
        "还没出汗{embedding:lazywet, sweat, sweat drop}", 
        "微微出汗[sweat, sweat drop]", 
        "香汗淋漓[(very sweaty:1.2), (shiny skin:1.2), (steaming body:1.2), wet, sweat, sweat drop]"
    ],
    "view": [
        "(不指定)", 
        "正面镜头[straight-on]", 
        "镜头在侧[from side]", 
        "镜头在后[from behind]", 
        "镜头在上[from above]", 
        "镜头在下[from below]"
    ],
    "dutchangle": [
        "(不指定)", 
        "镜头倾斜[dutch angle]"
    ],
    "focus": [
        "(不指定)", 
        "全身[full body]", 
        "中景[cowboy shot]", 
        "面部特写[close-up face, portrait]", 
        "上身特写[breast focus, upper body]", 
        "足部特写[foot focus]"
    ],
}

class SlaaneshPoseControl:
    @classmethod
    def INPUT_TYPES(s):
        required_inputs = {
            "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
            "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
        }
        
        # --- 动态加载 UI (应用 register_opt) ---
        group0 = [register_opt(x) for x in POSE_DATA["group0_basic"]]
        group1 = [register_opt(x) for x in POSE_DATA["group1_suit"]]
        body = [register_opt(x) for x in POSE_DATA["body"]]
        face_dir = [register_opt(x) for x in POSE_DATA["face_direction"]]
        eye1 = [register_opt(x) for x in POSE_DATA["eye1"]]
        eye2 = [register_opt(x) for x in POSE_DATA["eye2"]]
        eyebrow = [register_opt(x) for x in POSE_DATA["eyebrow"]]
        expr = [register_opt(x) for x in POSE_DATA["expressions"]]
        hands1 = [register_opt(x) for x in POSE_DATA["hands1"]]
        hands2 = [register_opt(x) for x in POSE_DATA["hands2"]]
        legs = [register_opt(x) for x in POSE_DATA["legs"]]
        wet = [register_opt(x) for x in POSE_DATA["wet"]]
        view = [register_opt(x) for x in POSE_DATA["view"]]
        dutch = [register_opt(x) for x in POSE_DATA["dutchangle"]]
        focus = [register_opt(x) for x in POSE_DATA["focus"]]

        required_inputs.update({
            "基本动作": (group0,),
            "动作套装": (group1,),
            "躯干体态": (body,),
            "面部朝向": (face_dir,),
            "眼神1": (eye1,),
            "眼神2": (eye2,),
            "眉毛细节": (eyebrow,),
            "综合表情": (expr,),
            "手部动作1": (hands1,),
            "手部动作2": (hands2,),
            "腿部动作": (legs,),
            "是否湿身": (wet,),
            "镜头视角": (view,),
            "倾斜镜头": (dutch,),
            "构图特写": (focus,),
        })

        return {"required": required_inputs}

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词", "面部提示词")
    FUNCTION = "slaaneshpose"
    CATEGORY = "slaaneshcontroller/pose"

    def slaaneshpose(self, **kwargs):
        if not kwargs.get("总开关", False): return ("", "", "") 

        mode = kwargs["模式选择"]
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        
        def extract(text, target="pos"):
            if not text or "(不指定)" in text: return ""
            if target == "pos":
                match = re.search(r'\[(.*?)\]', text)
                return match.group(1).strip() if match else ""
            else:
                match = re.search(r'\{(.*?)\}', text)
                return match.group(1).strip() if match else ""

        def enforce(tag):
            return tag if tag else ""

        pos_parts = []
        neg_parts = []
        face_parts = [] # 存储面部相关提示词
        
        lock_legs = False
        lock_hands2 = False

        # --- 1. 处理主姿势 ---
        # [关键修改] 获取中文短名 -> 映射回完整字符串
        base_choice_short = kwargs.get("基本动作", "(不指定)")
        suit_choice_short = kwargs.get("动作套装", "(不指定)")
        
        base_choice = GLOBAL_OPTS_MAP.get(base_choice_short, base_choice_short)
        suit_choice = GLOBAL_OPTS_MAP.get(suit_choice_short, suit_choice_short)
        
        final_main_pose = ""

        if mode == "🔒 手动指定":
            if suit_choice != "(不指定)":
                final_main_pose = suit_choice
                lock_legs = True
            else:
                final_main_pose = base_choice
        elif mode == "🎲 部分随机(手动优先)":
            if suit_choice != "(不指定)":
                final_main_pose = suit_choice
                lock_legs = True
            elif base_choice != "(不指定)":
                final_main_pose = base_choice
            else:
                if rng.random() < 0.5:
                    final_main_pose = rng.choice(POSE_DATA["group1_suit"][1:])
                    lock_legs = True
                else:
                    final_main_pose = rng.choice(POSE_DATA["group0_basic"][1:])
        else: # 完全随机
            if rng.random() < 0.5:
                final_main_pose = rng.choice(POSE_DATA["group1_suit"][1:])
                lock_legs = True
            else:
                final_main_pose = rng.choice(POSE_DATA["group0_basic"][1:])
        
        if final_main_pose and final_main_pose != "(不指定)":
            p = extract(final_main_pose, "pos")
            n = extract(final_main_pose, "neg")
            if p: pos_parts.append(enforce(p))
            if n: neg_parts.append(n)

        # --- 2. 处理手部动作 1 ---
        def check_hand_lock(text):
            double_keywords = ["双手", "双臂", "交叠", "祈祷", "双手保持", "抱胸", "脑后", "身后", "插兜"]
            return any(k in text for k in double_keywords)

        h1_choice_short = kwargs.get("手部动作1", "(不指定)")
        h1_choice = GLOBAL_OPTS_MAP.get(h1_choice_short, h1_choice_short)
        
        selected_h1 = ""
        if mode == "🔒 手动指定":
            selected_h1 = h1_choice
        elif mode == "🎲 部分随机(手动优先)" and h1_choice != "(不指定)":
            selected_h1 = h1_choice
        elif rng.random() < 0.8:
            selected_h1 = rng.choice(POSE_DATA["hands1"][1:])
        
        if selected_h1 and selected_h1 != "(不指定)":
            p = extract(selected_h1, "pos")
            n = extract(selected_h1, "neg")
            if p: pos_parts.append(enforce(p))
            if n: neg_parts.append(n)
            
            if check_hand_lock(selected_h1):
                lock_hands2 = True

        # --- 2.5 处理湿身 (仅手动) ---
        wet_choice_short = kwargs.get("是否湿身", "(不指定)")
        wet_choice = GLOBAL_OPTS_MAP.get(wet_choice_short, wet_choice_short)
        
        if wet_choice != "(不指定)":
             p = extract(wet_choice, "pos")
             n = extract(wet_choice, "neg")
             if p: pos_parts.append(enforce(p))
             if n: neg_parts.append(n)

        # --- 3. 循环处理其他组 ---
        remaining_groups = [
            ("躯干体态", "body"),
            ("面部朝向", "face_direction"),
            ("眼神1", "eye1"),
            ("眼神2", "eye2"),
            ("眉毛细节", "eyebrow"),
            ("综合表情", "expressions"),
            ("手部动作2", "hands2"),
            ("腿部动作", "legs"),
            ("镜头视角", "view"),
            ("倾斜镜头", "dutchangle"),
            ("构图特写", "focus")
        ]
        
        # 定义属于面部的分类key
        face_categories = ["face_direction", "eye1", "eye2", "eyebrow", "expressions"]

        for k_key, d_key in remaining_groups:
            if d_key == "legs" and lock_legs: continue
            if d_key == "hands2" and lock_hands2: continue
            
            choice_short = kwargs.get(k_key, "(不指定)")
            choice = GLOBAL_OPTS_MAP.get(choice_short, choice_short)
            
            selected_tag = ""
            
            if mode == "🔒 手动指定":
                selected_tag = choice
            elif mode == "🎲 部分随机(手动优先)" and choice != "(不指定)":
                selected_tag = choice
            elif rng.random() < 0.8:
                selected_tag = rng.choice(POSE_DATA[d_key][1:])
            
            if selected_tag and selected_tag != "(不指定)":
                p = extract(selected_tag, "pos")
                n = extract(selected_tag, "neg")
                if p: 
                    pos_parts.append(enforce(p))
                    # [关键修改] 如果该类别属于面部特征，则添加到面部提示词列表
                    if d_key in face_categories:
                        face_parts.append(enforce(p))
                        
                if n: neg_parts.append(n)

        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        final_face = ", ".join(filter(None, face_parts))
        
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "
        if final_face: final_face += ", "

        return (final_pos, final_neg, final_face)

NODE_CLASS_MAPPINGS = {"SlaaneshPoseControl": SlaaneshPoseControl}
NODE_DISPLAY_NAME_MAPPINGS = {"SlaaneshPoseControl": "色孽の常规姿势控制 V4.7"}

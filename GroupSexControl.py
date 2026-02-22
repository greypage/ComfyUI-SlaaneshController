import random
import re

# ==========================================
# 色孽の群交轮奸控制 (SlaaneshGroupSexControl) V5.1 Fix
# 1. 修复 KeyError: 补全了 COMMON_TAGS 中缺失的 H14-H27 和 L08-L19
# 2. 修复 SyntaxError: 修正了部分提示词中的中文标点符号
# ==========================================

# 【新增】全局 UI 映射字典：存储 "中文短名" -> "完整数据字符串" 的对应关系
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    """
    辅助函数：将完整字符串注册到映射表，并返回简洁的中文名
    输入: "01.大腿分开[legs_apart],{m_legs}"
    输出: "01.大腿分开" (同时将映射存入 GLOBAL_OPTS_MAP)
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

# 1. 通用资源池 (Common Tags)
# 包含：H(手部), L(腿部), F(面部-新增)
COMMON_TAGS = {
    # --- 手部资源池 ---
    "H01": "01.放奶子上[hands on own chest]", 
    "H02": "02.抬起手臂[arms up, armpits]", 
    "H03": "03.双手抬起[w arms, hands up]", 
    "H04": "04.放肚子上[hands on own stomach]", 
    "H05": "05.手放两侧[arms at side]", 
    "H06": "06.自己开阴[(female masturbation:1.3), (spreading own pussy:1.2)]", 
    "H07": "07.被抓手腕[wrist grab, arms at side]", 
    "H08": "08.撸动肉棒[handjob]",
    "H09": "09.双手撸动[double handjob]", 
    "H10": "10.撸管开阴[handjob, (female masturbation:1.3), (spreading own pussy:1.2)]", 
    "H11": "11.手臂支撑[arm support]",
    "H12": "12.被向后拉[arm held back]",
    "H13": "13.双手捧碗[cupping hands, hand to mouth]",

    
    # --- 腿部资源池 ---
    "L01": "01.罗圈开腿[bowlegged pose, legs apart]", 
    "L02": "02.M字开腿[m legs, spread legs]",
    "L03": "03.种付开腿[(folded:1.1), spread legs, knees to chest, legs up]", 
    "L04": "04.单腿抬高[leg up, spread legs]",
    "L05": "05.大腿并拢[legs together]",
    "L06": "06.大腿分开[legs apart]",
    "L07": "07.内八姿势[knees together feet apart]",


    # --- F. 面部表情资源池 (新增 T3 级控制) ---
    "F01": "01.舔鸡鸡[licking penis]",
    "F02": "02.口交含弄[oral, fellatio]",
    "F03": "03.鼓嘴口交[cheek bulge, oral, fellatio]",
    "F04": "04.强力口交[:>=, oral, fellatio]",
    "F05": "05.深喉口交[deepthroat, irrumatio, oral, fellatio]",
    "F06": "06.魅惑微笑[seductive smile, parted lips]", 
    "F07": "07.张嘴娇喘[moaning, gasping, open mouth]", 
    "F08": "08.张嘴吐舌娇喘[moaning, gasping, open mouth, tongue out, uvula]", 
    "F09": "09.o型嘴娇喘[:o]", 
    "F10": "10.o型嘴吐舌娇喘[:o, tongue out]",  # 修复中文逗号
    "F11": "11.嘟嘴[puckered lips, :o]", 
    "F12": "12.栗子嘴[chestnut mouth]", 
    "F13": "13.被操傻笑[(fucked silly:1.2), open mouth, crazy smile]", 
    "F14": "14.傻笑吐舌[(fucked silly:1.2), open mouth, crazy smile, tongue out, uvula]", 
    "F15": "15.毫无感觉[expressionless, parted lips]", 
    "F16": "16.闭嘴忍耐[closed mouth, homu]", 
    "F17": "17.微微忍耐[parted lips, teeth]", 
    "F18": "18.强行忍耐[parted lips, teeth, clenched teeth]", 
    "F19": "19.咬牙切齿[disgust, clenched teeth]"
}

# 2. 自动细节资源池 (Auto Details)
AUTO_DETAILS = {
    # --- 1. 插入位置(必须手动) ---
    "INSERTION_POS": {
        "双插小穴": "[spitroast, vaginal],{anal}", 
        "双插菊穴": "[spitroast, anal],{vaginal}",
        "双穴贯通": "[double penetration]",
        "未插入": "[imminent penetration]", 
    },
    # --- 2. 插入深度（必须手动） ---
    "DEPTH": {
        "宫颈穿透": "[stomach bulge]",
        "最深部射精": "[cum in womb]", 
    },
    # --- 3. 眼神1 (All Groups) ---
    "EYES_1": {
        "看向观众": "[looking at viewer]", 
        "向下看": "[looking down]", 
        "向上看": "[looking up]", 
        "看向别处": "[looking away]", 
        "回眸": "[looking back]", 
        "啊嘿颜": "[ahegao]",
        "哦齁颜": "[ohogao]", 
        "瞳孔缩小": "[wide-eyed]", 
        "翻白眼": "[rolling eyes]", 
        "空洞双眼": "[empty eyes]", 
        "半闭眼": "[half-closed eyes]",
        "半眯眼": "[narrowed eyes]", 
        "斗鸡眼": "[cross-eyed]", 
        "爱心眼": "[heart-shaped pupils]", 
        "闭一只眼": "[one eye closed]",
        "闭眼": "[(closed eyes:1.1)]"
    },
    # --- 4. 眼神2 (All Groups) ---
    "EYES_2": {
        "看向观众": "[looking at viewer]", 
        "向下看": "[looking down]", 
        "向上看": "[looking up]", 
        "看向别处": "[looking away]", 
        "回眸": "[looking back]", 
        "啊嘿颜": "[ahegao]",
        "哦齁颜": "[ohogao]", 
        "瞳孔缩小": "[wide-eyed]", 
        "翻白眼": "[rolling eyes]", 
        "空洞双眼": "[empty eyes]", 
        "半闭眼": "[half-closed eyes]",
        "半眯眼": "[narrowed eyes]", 
        "斗鸡眼": "[cross-eyed]", 
        "爱心眼": "[heart-shaped pupils]", 
        "闭一只眼": "[one eye closed]",
        "闭眼": "[(closed eyes:1.1)]"
    },
    # --- 5. 眉毛 (All Groups) ---
    "EYEBROWS": {
        "V字眉": "[v-shaped eyebrows]", 
        "八字眉": "[raised eyebrows]", 
    },
    # --- 6. 乳摇 (All Groups) ---
    "BREAST_SHAKE": {
        "乳摇": "[bouncing breasts]", 
    },
    # --- 8. 脸红 (All Groups) ---
    "BLUSH": {
        "一点脸红": "[light blush]", 
        "脸红": "[blush]", 
        "更加脸红": "[blush, nose blush]", 
        "满脸红晕": "[full-face blush, nose blush, ear blush]",
    },
    # --- 9. 眼泪口水 (All Groups) ---
    "FLUIDS_FACE": {
        "眼泪": "[tears, teardrop]",
        "口水": "[saliva, drooling]", # 修复中文逗号
        "眼泪口水": "[tears, teardrop, saliva, drooling]", # 修复中文逗号
    },
    # --- 10. 性交射精(必须手动) (Group 1 & 4) ---
    "EJAC_SEX": {
        "小穴射精": "[cum in pussy]", 
        "小穴小嘴射精": "[cum in pussy, cum in mouth]", 
        "菊穴射精": "[cum in ass]", 
        "菊穴小嘴射精": "[cum in ass, cum in mouth]", 
        "三穴射精": "[cum in pussy, cum in ass, cum in mouth]", 
        "体外射精": "[(projectile cum:1.1), cum on body]", 
        "口内射精": "[cum in mouth]", 
        "口内强力射精": "[cum in mouth, cheek bulge]", 
        "体外颜射": "[facial, bukkake, cum on hair, cum on breasts]", 
    },
    # --- 12. 过量射精(必须手动) (Group 1, 2, 4 - 连锁触发) ---
    "EJAC_EXCESS": {
        "巨量射精": "[excessive cum]", 
    },
    # --- 13. 汗水 (All Groups) ---
    "SWEAT": {
        "还没出汗": "{embedding:lazywet, sweat, sweat drop}", 
        "微微出汗": "[sweat, sweat drop]", 
        "香汗淋漓": "[(very sweaty:1.2), (shiny skin:1.2), (steaming body:1.2), wet, sweat, sweat drop]", 
    },
    # --- 14. 淫水 (All Groups) ---
    "JUICES": {
        "丝丝缕缕": "[pussy juice]", 
        "淫水汩汩": "[pussy juice, (pussy juice trail:1.2), (pussy juice stain:1.1), pussy juice puddle]", # 修复中文冒号
    },
    # --- 15. 潮吹(必须手动) (All Groups) ---
    "SQUIRT": {
        "盛大潮吹(必须手动)": "[female ejaculation, female orgasm]", 
    },
    # --- 16. 娇颤 (All Groups) ---
    "TWITCH": {
        "娇颤不止": "[twitching, trembling]", 
    },
    # --- 17. 螓首(必须手动) (All Groups) ---
    "HEAD": {
        "歪头": "[head tilt]", 
        "侧头": "[profile]", 
        "仰头": "[(head back:1.2)]", 
    },
    # --- 18. 画面 (All Groups) ---
    "EFFECT": {
        "运动线": "[motion lines, speed lines]", 
        "运动模糊": "[motion blur]",
        "拟声词": "[(sound effects:1.2)]", 
        "特效全家桶": "[(sound effects only:1.2), motion lines, speed lines, motion blur]", 
    },
}

# 3. 核心逻辑树 (Logic Tree)
# 结构：Group -> Pose -> View -> {allow_hands, allow_legs, allow_face}
GROUP_LOGIC_TREE = {
    # ================= Group 1: 多人乱交 (示例) =================
    "Group1": {
        "name": "🍢前后双插",
        "poses": {
            "前后双插-正常位1234[gangbang, group sex, (missionary:1.2), lying, on back, leaning back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L01","L02","L04"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H10","H11"], 
                        "allow_legs": ["L01","L02","L03"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H01","H03","H05","H07","H08","H09"], 
                        "allow_legs": ["L01","L02","L03"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H10","H11"], 
                        "allow_legs": ["L01","L02","L03"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "前后双插-侧面位15[gangbang, group sex, lying, on side, leaning, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H03","H05","H06","H08"], 
                        "allow_legs": ["L01","L02","L04","L05"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H01","H03","H05","H06","H08"], 
                        "allow_legs": ["L01","L02","L03","L05"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "前后双插-俯卧位126[gangbang, group sex, (prone bone:1.1), on stomach, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H03"], 
                        "allow_legs": ["L05"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H03"], 
                        "allow_legs": ["L05"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H01","H03"], 
                        "allow_legs": ["L05"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "前后双插-后入式12678[gangbang, group sex, (sex from behind:1.2), doggystyle, kneeling, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H08","H09","H11","H12"], 
                        "allow_legs": ["L05","L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H08","H09","H11","H12"], 
                        "allow_legs": ["L05","L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H08","H09","H11","H12"], 
                        "allow_legs": ["L05","L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H08","H09","H11","H12"], 
                        "allow_legs": ["L05","L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H08","H09","H11","H12"], 
                        "allow_legs": ["L05","L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "前后双插-正面骑乘位后仰19[gangbang, group sex, (cowgirl position:1.2), girl on top, leaning back, arched back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H08","H09","H10","H11"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H11","H12"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "前后双插-站立后背位1278[gangbang, group sex, (standing sex:1.2), sex from behind, standing, leaning forward, arched back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H08","H09","H11","H12"], 
                        "allow_legs": ["L01","L05","L06","L07"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H08","H09","H11","H12"], 
                        "allow_legs": ["L01","L05","L06","L07"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H02","H08","H09","H11","H12"], 
                        "allow_legs": ["L01","L05","L06","L07"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H02","H08","H09","H11","H12"], 
                        "allow_legs": ["L01","L05","L06","L07"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"]  
                    },
                }
            },
        }
    },

    "Group2": {
        "name": "🌭双穴体位",
        "poses": {
            "双穴体位-躺姿双插127[gangbang, group sex, (reverse suspended congress:1.3), (reverse upright straddle:1.1), sitting, leaning back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L02"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L02"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L02"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "双穴体位-站立双插12[gangbang, group sex, (suspended congress:1.3), standing sex, face-to-face, (arms around neck:1.1), (leg lock:1.1), (knees up:1.1), sex, hetero],{fellatio, paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "双穴体位-纳尔逊锁12[gangbang, group sex, (full nelson:1.2), reverse suspended congress, standing sex, sex from behind, (folded:1.1), spread legs, knees to chest, legs up, sex, hetero],{fellatio, paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "双穴体位-正面骑乘位前倾1259[gangbang, group sex, (cowgirl position:1.2), girl on top, leaning forward, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H11"], 
                        "allow_legs": ["L06"], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
        }
    }, 
    "Group3": {
        "name": "🔗拘束捆绑",
        "poses": {
            # --- 示例体位 1: 轮奸正常位 ---
            "🪢捆绑绳缚-正常位1234[gangbang, groupsex, (shibari:1.1), breast bondage, bound arms, bound legs, frogtie, arm behind back, missionary, metal collar, bound wrists, lying, on back, leaning back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "⛓️捆绑锁链-正常位1234[gangbang, groupsex, (chain, chained:1.1), breast bondage, bound arms, bound legs, frogtie, arm behind back, missionary, metal collar, bound wrists, lying, on back, leaning back, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "🪢捆绑绳缚-后入式1257[gangbang, groupsex, (shibari:1.1), breast bondage, bound wrists, bound arms, arm behind back, sex from behind, doggystyle, kneeling, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "⛓️捆绑锁链-首枷固定后入式1257[gangbang, groupsex, (pillory:1.2), stationary restraints, sex from behind, doggystyle, kneeling, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "🪢捆绑绳缚-绳缚悬空后入式1257[gangbang, groupsex, (shibari:1.1), (suspension:1.1), stationary restraints, arm behind back, breast bondage, bound arms, bound legs, frogtie, sex from behind, metal collar, bound wrists, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
            "⛓️捆绑锁链-绳缚悬空后入式1257[gangbang, groupsex, (chain, chained:1.1), (suspension:1.1), stationary restraints, arm behind back, breast bondage, bound arms, bound legs, frogtie, sex from behind, metal collar, bound wrists, sex, hetero, surrounded by penises],{paizuri}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": [], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
        }
    },
    "Group4": {
        "name": "🫦多人口交",
        "poses": {
            # --- 示例体位 1: 轮奸正常位 ---
            "多重口交24[gangbang, groupsex, sex, hetero, surrounded by penises, kneeling, upper_body],{paizuri}": {
                "views": {
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H09","H13"], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H09","H13"], 
                        "allow_legs": [], 
                        "allow_face": ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19"] 
                    },
                }
            },
        }
    },
}

# ==============================================================================
# 辅助函数：UI 选项生成 (更新版，支持 Face)
# ==============================================================================
def get_all_options(tree):
    groups = [data["name"] for key, data in tree.items()]
    poses = ["(不指定)"]
    views = ["(不指定)"]
    hands_keys = set()
    legs_keys = set()
    face_keys = set()  # 新增
    
    for g_data in tree.values():
        for p_key, p_data in g_data["poses"].items():
            poses.append(register_opt(p_key)) 
            for v_key, v_data in p_data["views"].items():
                views.append(register_opt(v_key))
                for h in v_data.get("allow_hands", []): hands_keys.add(h)
                for l in v_data.get("allow_legs", []): legs_keys.add(l)
                for f in v_data.get("allow_face", []): face_keys.add(f) # 新增
    
    # 注册并生成短名列表
    hands_list = ["(不指定)"] + [register_opt(COMMON_TAGS[k]) for k in hands_keys if k in COMMON_TAGS]
    legs_list = ["(不指定)"] + [register_opt(COMMON_TAGS[k]) for k in legs_keys if k in COMMON_TAGS]
    face_list = ["(不指定)"] + [register_opt(COMMON_TAGS[k]) for k in face_keys if k in COMMON_TAGS] # 新增
    
    return sorted(list(set(groups))), list(dict.fromkeys(poses)), list(dict.fromkeys(views)), sorted(hands_list), sorted(legs_list), sorted(face_list)

def get_detail_options(key):
    pool = AUTO_DETAILS.get(key, {})
    return ["(不指定)"] + sorted(list(pool.keys()))

UI_GROUPS, UI_POSES, UI_VIEWS, UI_HANDS, UI_LEGS, UI_FACES = get_all_options(GROUP_LOGIC_TREE)

# ==============================================================================
# 核心节点类定义：SlaaneshGroupSexControl
# ==============================================================================
class SlaaneshGroupSexControl:
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
                "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
                "玩法选择(必选)": (UI_GROUPS, {"default": UI_GROUPS[0] if UI_GROUPS else ""}),
                
                # --- 级联菜单 ---
                "体位(可选)": (UI_POSES,),
                "视角(不可单选)": (UI_VIEWS,),
                "手部(不可单选)": (UI_HANDS,),
                "腿部(不可单选)": (UI_LEGS,),
                "面部(不可单选)": (UI_FACES,), # 新增 T3 选项
                
                # --- 随机细节 (手动可覆盖) ---
                "插入位置(必须手动)": (get_detail_options("INSERTION_POS"),),
                "插入深度(必须手动)": (get_detail_options("DEPTH"),),
                "眼神1": (get_detail_options("EYES_1"),),
                "眼神2": (get_detail_options("EYES_2"),),
                "眉毛": (get_detail_options("EYEBROWS"),),
                "乳摇(必须手动)": (get_detail_options("BREAST_SHAKE"),),
                "脸红": (get_detail_options("BLUSH"),),
                "眼泪口水": (get_detail_options("FLUIDS_FACE"),),
                "性交射精(必须手动)": (get_detail_options("EJAC_SEX"),),
                "过量射精(必须手动)": (get_detail_options("EJAC_EXCESS"),),
                "汗水": (get_detail_options("SWEAT"),),
                "淫水": (get_detail_options("JUICES"),),
                "潮吹(必须手动)": (get_detail_options("SQUIRT"),),
                "娇颤": (get_detail_options("TWITCH"),),
                "螓首(必须手动)": (get_detail_options("HEAD"),),
                "画面(必须手动)": (get_detail_options("EFFECT"),),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词", "面部提示词")
    FUNCTION = "generate" 
    CATEGORY = "slaaneshcontroller/sex"

    # ==============================================================================
    # 核心生成逻辑函数
    # ==============================================================================
    def generate(self, **kwargs):
        
        # --- 工具函数 ---
        def parse_tag(text):
            if not text or text == "(不指定)": return "", ""
            pos_match = re.search(r'\[(.*?)\]', text)
            pos = pos_match.group(1).strip() if pos_match else ""
            neg_match = re.search(r'\{(.*?)\}', text) 
            neg = neg_match.group(1).strip() if neg_match else ""
            if not pos and not neg and ":" not in text: pos = text
            return pos, neg

        if not kwargs.get("总开关", True): return ("", "", "")

        mode = kwargs.get("模式选择")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        selected_group_name = kwargs.get("玩法选择(必选)")
        final_pos_list = []
        final_neg_list = []
        face_pos_list = [] # [新增] 用于存储面部相关的提示词

        # --- 基础逻辑: 确定 Group ---
        current_group_key = None
        for k, v in GROUP_LOGIC_TREE.items():
            if v["name"] == selected_group_name:
                current_group_key = k
                break
        
        if not current_group_key:
            return ("Error: Group Not Found", "", "")
            
        group_data = GROUP_LOGIC_TREE[current_group_key]
        poses_pool = group_data["poses"]

        # === Step 1: 确定体位 (Pose) ===
        if not poses_pool:
            return ("Error: Pose Pool is empty for this group!", "", "")

        selected_pose_key = None
        manual_pose_short = kwargs.get("体位(可选)", "(不指定)")
        # 查回完整 Key
        manual_pose_full = GLOBAL_OPTS_MAP.get(manual_pose_short, manual_pose_short)
        
        is_manual_pose_valid = manual_pose_full in poses_pool

        if mode == "🔒 手动指定":
            if is_manual_pose_valid: selected_pose_key = manual_pose_full
        elif mode == "🎲 部分随机(手动优先)":
            if is_manual_pose_valid: selected_pose_key = manual_pose_full
            else: selected_pose_key = rng.choice(list(poses_pool.keys()))
        else: # "💀 完全随机"
            selected_pose_key = rng.choice(list(poses_pool.keys()))

        if not selected_pose_key:
            return ("", "", "")

        p, n = parse_tag(selected_pose_key)
        if p: final_pos_list.append(p)
        if n: final_neg_list.append(n)

        pose_node = poses_pool[selected_pose_key]
        views_pool = pose_node.get("views", {})

        # === Step 2: 确定视角 (View) ===
        if not views_pool:
             selected_view_key = None
        else:
            selected_view_key = None
            manual_view_short = kwargs.get("视角(不可单选)", "(不指定)")
            # 查回完整 Key
            manual_view_full = GLOBAL_OPTS_MAP.get(manual_view_short, manual_view_short)
            
            is_manual_view_valid = manual_view_full in views_pool
            
            if mode == "🔒 手动指定":
                if is_manual_view_valid: selected_view_key = manual_view_full
            elif mode == "🎲 部分随机(手动优先)":
                if is_manual_view_valid: selected_view_key = manual_view_full
                elif views_pool: selected_view_key = rng.choice(list(views_pool.keys()))
            else:
                if views_pool: selected_view_key = rng.choice(list(views_pool.keys()))

        view_node = None
        if selected_view_key:
            p, n = parse_tag(selected_view_key)
            if p: final_pos_list.append(p)
            if n: final_neg_list.append(n)
            view_node = views_pool[selected_view_key]

        # === Step 3: 确定细节 (Hands/Legs/Face) ===
        skip_legs = False 

        if view_node:
            allowed_hands_keys = view_node.get("allow_hands", [])
            allowed_legs_keys = view_node.get("allow_legs", [])
            allowed_face_keys = view_node.get("allow_face", []) # 新增

            # --------- 3.1 处理手部 (Hands) ---------
            manual_hand_short = kwargs.get("手部(不可单选)", "(不指定)")
            manual_hand_full = GLOBAL_OPTS_MAP.get(manual_hand_short, manual_hand_short)
            
            manual_hand_key = None
            for k, v in COMMON_TAGS.items():
                if v == manual_hand_full:
                    manual_hand_key = k
                    break
            
            is_hand_valid = manual_hand_key in allowed_hands_keys
            final_hand_str = ""

            if mode == "🔒 手动指定":
                if is_hand_valid: final_hand_str = manual_hand_full
            elif mode == "🎲 部分随机(手动优先)":
                if is_hand_valid: final_hand_str = manual_hand_full
                elif allowed_hands_keys and rng.random() < 1: 
                    k = rng.choice(allowed_hands_keys)
                    final_hand_str = COMMON_TAGS[k]
            else: 
                if allowed_hands_keys and rng.random() < 1:
                    k = rng.choice(allowed_hands_keys)
                    final_hand_str = COMMON_TAGS[k]
            
            p, n = parse_tag(final_hand_str)
            if p: final_pos_list.append(p)
            if n: final_neg_list.append(n)

            if p and ("leg_lock" in p or "knees_to_chest" in p or "grabbing_own_thigh" in p):
                skip_legs = True

            # --------- 3.2 处理腿部 (Legs) ---------
            if not skip_legs:
                manual_leg_short = kwargs.get("腿部(不可单选)", "(不指定)")
                manual_leg_full = GLOBAL_OPTS_MAP.get(manual_leg_short, manual_leg_short)
            
                manual_leg_key = None
                for k, v in COMMON_TAGS.items():
                    if v == manual_leg_full:
                        manual_leg_key = k
                        break
                
                is_leg_valid = manual_leg_key in allowed_legs_keys
                final_leg_str = ""

                if mode == "🔒 手动指定":
                    if is_leg_valid: final_leg_str = manual_leg_full 
                elif mode == "🎲 部分随机(手动优先)":
                    if is_leg_valid: final_leg_str = manual_leg_full
                    elif allowed_legs_keys and rng.random() < 1:
                        k = rng.choice(allowed_legs_keys)
                        final_leg_str = COMMON_TAGS[k]
                else:
                    if allowed_legs_keys and rng.random() < 1:
                        k = rng.choice(allowed_legs_keys)
                        final_leg_str = COMMON_TAGS[k]

                p, n = parse_tag(final_leg_str)
                if p: final_pos_list.append(p)
                if n: final_neg_list.append(n)

            # --------- 3.3 处理面部 (Face) [新增逻辑] ---------
            manual_face_short = kwargs.get("面部(不可单选)", "(不指定)")
            manual_face_full = GLOBAL_OPTS_MAP.get(manual_face_short, manual_face_short)
            
            manual_face_key = None
            for k, v in COMMON_TAGS.items():
                if v == manual_face_full:
                    manual_face_key = k
                    break
            
            is_face_valid = manual_face_key in allowed_face_keys
            final_face_str = ""

            if mode == "🔒 手动指定":
                if is_face_valid: final_face_str = manual_face_full
            elif mode == "🎲 部分随机(手动优先)":
                if is_face_valid: final_face_str = manual_face_full
                elif allowed_face_keys and rng.random() < 1:
                    k = rng.choice(allowed_face_keys)
                    final_face_str = COMMON_TAGS[k]
            else:
                if allowed_face_keys and rng.random() < 1:
                    k = rng.choice(allowed_face_keys)
                    final_face_str = COMMON_TAGS[k]

            p, n = parse_tag(final_face_str)
            if p: 
                final_pos_list.append(p)
                face_pos_list.append(p) # [新增] 同步收集到面部列表
            if n: final_neg_list.append(n)

        # ----------------------------------------------------------------
        # 4. 增强逻辑: 细节随机 (Auto Details)
        # ----------------------------------------------------------------
        # (key_in_kwargs, pool_key, prob, forbidden_words)
        # 概率为 0 表示必须手动指定，不参与随机
        DETAILS_CONFIG = [
            ("插入位置(必须手动)", "INSERTION_POS", 0, []),
            ("插入深度(必须手动)", "DEPTH", 0, []),
            ("眼神1", "EYES_1", 0.75, []),
            ("眼神2", "EYES_2", 0.75, []),
            ("眉毛", "EYEBROWS", 0.5, []),
            ("乳摇(必须手动)", "BREAST_SHAKE", 0, []),
            ("脸红", "BLUSH", 0.3, []),
            ("眼泪口水", "FLUIDS_FACE", 0.3, []),
            ("性交射精(必须手动)", "EJAC_SEX", 0, []),
            ("过量射精(必须手动)", "EJAC_EXCESS", 0, []),
            ("汗水", "SWEAT", 0.3, []),
            ("淫水", "JUICES", 0.3, []),
            ("潮吹(必须手动)", "SQUIRT", 0, []),
            ("娇颤", "TWITCH", 0.3, []),
            ("螓首(必须手动)", "HEAD", 0, []),
            ("画面(必须手动)", "EFFECT", 0, []),
        ]
        
        # 定义需要提取到面部提示词的 Pool Key
        FACE_KEYS = ["EYES_1", "EYES_2", "EYEBROWS", "BLUSH", "FLUIDS_FACE"]

        current_pos_str = ",".join(final_pos_list)
        
        for ui_key, pool_key, prob, forbidden in DETAILS_CONFIG:
            manual_val = kwargs.get(ui_key, "(不指定)")
            pool = AUTO_DETAILS.get(pool_key, {})
            
            found_val = None
            
            # 手动优先
            if manual_val != "(不指定)" and manual_val in pool:
                found_val = pool[manual_val]
            
            # 随机触发
            elif mode != "🔒 手动指定":
                if not (forbidden and any(w in current_pos_str for w in forbidden)):
                    if rng.random() < prob and pool:
                        keys = list(pool.keys())
                        if keys:
                            rand_key = rng.choice(keys)
                            found_val = pool[rand_key]
                            
            if found_val:
                p, n = parse_tag(found_val)
                if p: 
                    final_pos_list.append(p)
                    # [新增] 如果属于面部特征，添加到面部提示词列表
                    if pool_key in FACE_KEYS:
                        face_pos_list.append(p)
                if n: final_neg_list.append(n)

        # --- 最终组合 ---
        pos_str = ", ".join(filter(None, final_pos_list))
        neg_str = ", ".join(filter(None, final_neg_list))
        face_str = ", ".join(filter(None, face_pos_list)) # [新增]

        if pos_str: pos_str += ", "
        if neg_str: neg_str += ", "
        if face_str: face_str += ", " # [新增]

        return (pos_str, neg_str, face_str)

# 注册节点类映射
NODE_CLASS_MAPPINGS = {"SlaaneshGroupSexControl": SlaaneshGroupSexControl}
# 注册节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {"SlaaneshGroupSexControl": "色孽の群交轮奸控制 V5.2"}

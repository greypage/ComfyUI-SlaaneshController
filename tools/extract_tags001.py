#!/usr/bin/env python3
"""从 tags001.docx 提取指定章节的 tag 数据，生成 PromptCardData.py。"""

from __future__ import annotations

import hashlib
import re
import zipfile
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

SCOPE_TO_NODE_KEY = {
    "涩涩服装": "costume",
    "涩涩构图-擦边涩涩类": "framing",
    "涩涩构图-露点涩涩类": "framing",
    "R18+": "r18_scene",
}

NODE_META = {
    "costume": {"title": "服装抽卡", "section": ["涩涩服装"]},
    "framing": {
        "title": "构图抽卡",
        "section": ["涩涩构图-擦边涩涩类", "涩涩构图-露点涩涩类"],
    },
    "r18_scene": {"title": "R18情景抽卡", "section": ["R18+"]},
    "scene_hint": {
        "title": "场景抽卡",
        "section": ["涩涩服装", "涩涩构图-擦边涩涩类", "涩涩构图-露点涩涩类", "R18+"],
    },
}

HEADING_STYLES = {"2", "3", "4"}
TITLE_STYLES = {"5", "6", "7", "8", "9", "afe", "aff1", "aff3", "TOC"}

SCENE_HINT_KEYWORDS = (
    "适配场景",
    "场景背景参考",
    "背景参考",
    "测试背景参考",
    "服装适配场景参考",
    "万圣节适配场景参考",
    "测试展示动作场景参考",
)

NEG_HINT_KEYWORDS = ("反向", "negative", "neg")
HAN_RE = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class ParserState:
    h2: str = ""
    h3: str = ""
    h4: str = ""
    major_title: str = ""
    anchor_title: str = ""
    variant_title: str = ""
    title: str = ""
    pos_tokens: List[str] = field(default_factory=list)
    neg_tokens: List[str] = field(default_factory=list)
    scene_tokens: List[str] = field(default_factory=list)
    raw_lines: List[str] = field(default_factory=list)
    neg_capture_open: bool = False


@dataclass
class ExtractReport:
    suspicious_lines: List[Tuple[str, str, str, str, str, str]] = field(default_factory=list)
    dropped_entries: List[Tuple[str, str, str, str, str]] = field(default_factory=list)


def get_paragraph_text(paragraph: ET.Element) -> str:
    text = "".join((t.text or "") for t in paragraph.findall(".//w:t", NS))
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    return text


def get_style(paragraph: ET.Element) -> str:
    style_el = paragraph.find("w:pPr/w:pStyle", NS)
    if style_el is None:
        return "Normal"
    return style_el.attrib.get(f"{{{NS['w']}}}val", "Normal")


def dedupe_keep_order(tokens: List[str]) -> List[str]:
    seen = set()
    out = []
    for token in tokens:
        key = token.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def normalize_join(tokens: List[str]) -> str:
    norm = dedupe_keep_order(tokens)
    if not norm:
        return ""
    return ", ".join(norm) + ", "


def make_entry_id(node_key: str, category: str, title: str, prompt_pos: str, prompt_neg: str) -> str:
    raw = f"{node_key}|{category}|{title}|{prompt_pos}|{prompt_neg}".encode("utf-8")
    digest = hashlib.md5(raw).hexdigest()[:12]
    return f"{node_key}_{digest}"


def strip_chinese(text: str) -> str:
    return HAN_RE.sub(" ", text)


def normalize_token(token: str) -> str:
    token = token.strip()
    token = token.replace("\\(", "(").replace("\\)", ")")
    token = token.replace("：", ":")
    token = re.sub(r"^\d+\s*:\s*", "", token)
    token = re.sub(r"^[\s\[\]:;，。—\-·]+", "", token)
    token = re.sub(r"[\s\]:;，。—\-·]+$", "", token)
    return token.strip()


def english_tokens_from_text(text: str) -> List[str]:
    text = text.replace("，", ",")
    text = strip_chinese(text)
    tokens = []
    for part in text.split(","):
        token = normalize_token(part)
        if not token:
            continue
        if HAN_RE.search(token):
            continue
        if not re.search(r"[A-Za-z0-9]", token):
            continue
        if re.fullmatch(r"\d+", token):
            continue
        if re.fullmatch(r"[A-Za-z]\)", token):
            continue
        tokens.append(token)
    return tokens


def extract_negative_tokens(line: str) -> Tuple[List[str], str]:
    neg_tokens: List[str] = []

    def repl(match: re.Match[str]) -> str:
        content = match.group(1)
        if any(key in content.lower() for key in NEG_HINT_KEYWORDS):
            neg_tokens.extend(english_tokens_from_text(content))
            return " "
        return match.group(0)

    cleaned = re.sub(r"\[([^\]]+)\]", repl, line)
    return neg_tokens, cleaned


def extract_negative_tokens_by_stream(line: str, capture_open: bool) -> Tuple[List[str], str, bool]:
    """
    处理跨段/跨行的负向备注块，例如：
    [反向添加aaa, bbb,
    ccc提升稳定性]
    """
    neg_tokens: List[str] = []
    cleaned_tokens: List[str] = []
    in_neg = capture_open

    raw_parts = line.replace("，", ",").split(",")
    for part in raw_parts:
        token = part.strip()
        if not token:
            continue

        if not in_neg and ("[" in token and any(k in token for k in NEG_HINT_KEYWORDS)):
            in_neg = True

        if in_neg:
            neg_tokens.extend(english_tokens_from_text(token))
            if "]" in token:
                in_neg = False
            continue

        cleaned_tokens.append(token)

    cleaned_line = ", ".join(cleaned_tokens)
    return neg_tokens, cleaned_line, in_neg


def extract_scene_tokens(line: str) -> Tuple[List[str], bool]:
    if any(key in line for key in SCENE_HINT_KEYWORDS):
        return english_tokens_from_text(line), True
    return [], False


def line_looks_like_title(style: str, text: str, pos_token_count: int, is_scene_line: bool) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if style in TITLE_STYLES:
        return True
    if style == "af7" and not is_scene_line:
        return True
    has_han = HAN_RE.search(stripped) is not None
    if not has_han:
        return False
    if is_scene_line:
        return False
    comma_count = stripped.count(",") + stripped.count("，")
    if comma_count == 0:
        return True
    if pos_token_count <= 1:
        return True
    return False


def dump_data_py(out_path: Path, datasets: Dict[str, OrderedDict]) -> None:
    lines: List[str] = []
    lines.append("# -*- coding: utf-8 -*-")
    lines.append('"""自动生成文件：由 tools/extract_tags001.py 生成，请勿手改。"""')
    lines.append("")
    lines.append("PROMPT_CARD_DATA = {")

    for node_key, node in datasets.items():
        lines.append(f"    {node_key!r}: {{")
        lines.append(f"        'title': {NODE_META[node_key]['title']!r},")
        lines.append(f"        'sections': {NODE_META[node_key]['section']!r},")
        lines.append("        'categories': [")
        for category_label, items in node["categories"].items():
            lines.append("            {")
            lines.append(f"                'label': {category_label!r},")
            lines.append("                'items': [")
            for item in items:
                lines.append("                    {")
                lines.append(f"                        'id': {item['id']!r},")
                lines.append(f"                        'title': {item['title']!r},")
                lines.append(f"                        'group_title': {item['group_title']!r},")
                lines.append(f"                        'group_path': {item['group_path']!r},")
                lines.append(f"                        'prompt_pos': {item['prompt_pos']!r},")
                lines.append(f"                        'prompt_neg': {item['prompt_neg']!r},")
                lines.append("                    },")
            lines.append("                ],")
            lines.append("            },")
        lines.append("        ],")
        lines.append("    },")

    lines.append("}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_reports(repo_root: Path, report: ExtractReport) -> None:
    suspicious_path = repo_root / "tools" / "prompt_pos_mostly_zh_lines.txt"
    dropped_path = repo_root / "tools" / "prompt_pos_dropped_entries.txt"

    s_lines: List[str] = []
    s_lines.append("几乎全中文说明行（供人工复核）")
    s_lines.append("")
    s_lines.append(f"总数: {len(report.suspicious_lines)}")
    s_lines.append("")

    for idx, (h2, h3, h4, style, title, line) in enumerate(report.suspicious_lines, 1):
        s_lines.append(f"[{idx}] {h2} / {h3} / {h4} | style={style} | title={title}")
        s_lines.append(f"line: {line}")
        s_lines.append("")

    suspicious_path.write_text("\n".join(s_lines), encoding="utf-8")

    d_lines: List[str] = []
    d_lines.append("清洗后无有效英文 token 的条目（已跳过主输出）")
    d_lines.append("")
    d_lines.append(f"总数: {len(report.dropped_entries)}")
    d_lines.append("")

    for idx, (node_key, category, title, pos_raw, neg_raw) in enumerate(report.dropped_entries, 1):
        d_lines.append(f"[{idx}] {node_key} | {category} | {title}")
        d_lines.append(f"pos_raw: {pos_raw}")
        d_lines.append(f"neg_raw: {neg_raw}")
        d_lines.append("")

    dropped_path.write_text("\n".join(d_lines), encoding="utf-8")


def build_datasets(docx_path: Path) -> Tuple[Dict[str, OrderedDict], ExtractReport]:
    datasets: Dict[str, OrderedDict] = {
        "costume": OrderedDict(categories=OrderedDict()),
        "framing": OrderedDict(categories=OrderedDict()),
        "r18_scene": OrderedDict(categories=OrderedDict()),
        "scene_hint": OrderedDict(categories=OrderedDict()),
    }
    report = ExtractReport()

    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    body = root.find("w:body", NS)
    if body is None:
        return datasets, report

    state = ParserState()

    def current_category_label() -> str:
        if state.h3 and state.h4:
            return f"{state.h3} / {state.h4}"
        if state.h3:
            return state.h3
        return "(未分类)"

    def ensure_category(node_key: str, category_label: str) -> List[Dict[str, str]]:
        cats = datasets[node_key]["categories"]
        if category_label not in cats:
            cats[category_label] = []
        return cats[category_label]

    def resolve_group_titles() -> Tuple[str, str]:
        group_title = state.anchor_title.strip()
        subgroup = state.variant_title.strip()
        return group_title, subgroup

    def flush_entry() -> None:
        if not (state.pos_tokens or state.neg_tokens or state.scene_tokens):
            state.raw_lines.clear()
            return

        node_key = SCOPE_TO_NODE_KEY.get(state.h2)
        if not node_key:
            state.pos_tokens.clear()
            state.neg_tokens.clear()
            state.scene_tokens.clear()
            state.raw_lines.clear()
            return

        category_label = current_category_label()
        entry_title = state.title.strip() if state.title.strip() else category_label
        group_title, subgroup_title = resolve_group_titles()
        if not group_title:
            group_title = state.major_title.strip()
        group_path = f"{group_title} / {subgroup_title}".strip(" /") if subgroup_title else group_title

        prompt_pos = normalize_join(state.pos_tokens)
        prompt_neg = normalize_join(state.neg_tokens)
        scene_pos = normalize_join(state.scene_tokens)

        if prompt_pos or prompt_neg:
            entry_id = make_entry_id(node_key, category_label, entry_title, prompt_pos, prompt_neg)
            ensure_category(node_key, category_label).append(
                {
                    "id": entry_id,
                    "title": entry_title,
                    "group_title": group_title,
                    "group_path": group_path,
                    "prompt_pos": prompt_pos,
                    "prompt_neg": prompt_neg,
                }
            )
        elif not scene_pos:
            report.dropped_entries.append(
                (
                    node_key,
                    category_label,
                    entry_title,
                    " | ".join(state.raw_lines),
                    prompt_neg,
                )
            )

        if scene_pos:
            scene_base = entry_title if entry_title != category_label else (group_title or entry_title)
            scene_title = f"{scene_base}-场景"
            scene_id = make_entry_id("scene_hint", category_label, scene_title, scene_pos, "")
            ensure_category("scene_hint", category_label).append(
                {
                    "id": scene_id,
                    "title": scene_title,
                    "group_title": group_title,
                    "group_path": group_path,
                    "prompt_pos": scene_pos,
                    "prompt_neg": "",
                }
            )

        state.pos_tokens.clear()
        state.neg_tokens.clear()
        state.scene_tokens.clear()
        state.raw_lines.clear()
        state.neg_capture_open = False

    for paragraph in body.findall("w:p", NS):
        raw = get_paragraph_text(paragraph)
        text = raw.strip()
        style = get_style(paragraph)

        if not text:
            flush_entry()
            continue

        if style in HEADING_STYLES:
            flush_entry()
            if style == "2":
                state.h2 = text
                state.h3 = ""
                state.h4 = ""
                state.major_title = ""
                state.anchor_title = ""
                state.variant_title = ""
            elif style == "3":
                state.h3 = text
                state.h4 = ""
                state.major_title = ""
                state.anchor_title = ""
                state.variant_title = ""
            elif style == "4":
                state.h4 = text
                state.major_title = ""
                state.anchor_title = ""
                state.variant_title = ""
            state.title = ""
            continue

        if state.h2 not in SCOPE_TO_NODE_KEY:
            continue

        line_neg, line_without_neg = extract_negative_tokens(text)
        stream_neg, line_without_neg_stream, neg_capture_open = extract_negative_tokens_by_stream(
            line_without_neg, state.neg_capture_open
        )
        state.neg_capture_open = neg_capture_open
        if stream_neg:
            line_neg.extend(stream_neg)
        line_without_neg = line_without_neg_stream
        line_scene, is_scene_line = extract_scene_tokens(line_without_neg)
        line_pos = english_tokens_from_text(line_without_neg)

        # 场景说明行单独抽走，不进入主 prompt。
        if is_scene_line:
            flush_entry()
            if not state.title:
                state.title = text
            state.scene_tokens.extend(line_scene)
            state.raw_lines.append(text)
            flush_entry()
            continue

        # 独立的反向备注行，直接并入当前条目负向词，不作为标题。
        if line_neg and not line_pos:
            state.neg_tokens.extend(line_neg)
            state.raw_lines.append(text)
            continue

        if line_looks_like_title(style, text, len(line_pos), is_scene_line):
            flush_entry()
            if style in TITLE_STYLES:
                state.major_title = text
                if style in {"5", "6", "7"}:
                    state.anchor_title = text
                    state.variant_title = ""
                elif style in {"8", "9", "aff1", "afe", "aff3"}:
                    state.variant_title = text
                state.title = ""
            else:
                prev_title = state.title.strip()
                if (
                    prev_title
                    and ("," not in prev_title and "，" not in prev_title)
                    and ("," in text or "，" in text)
                ):
                    state.anchor_title = prev_title
                    state.major_title = prev_title
                state.title = text
            # 标题行若含足够英文 tag，则作为该标题下第一段 prompt
            if len(line_pos) >= 3:
                state.pos_tokens.extend(line_pos)
                state.neg_tokens.extend(line_neg)
                state.raw_lines.append(text)
            continue

        if (
            HAN_RE.search(text)
            and (text.count(",") + text.count("，") > 0)
            and len(line_pos) <= 1
            and not line_neg
        ):
            report.suspicious_lines.append((state.h2, state.h3, state.h4, style, state.title, text))

        # 普通内容行
        state.pos_tokens.extend(line_pos)
        state.neg_tokens.extend(line_neg)
        state.raw_lines.append(text)

    flush_entry()
    return datasets, report


def print_stats(datasets: Dict[str, OrderedDict], report: ExtractReport) -> None:
    print("生成统计:")
    for key, value in datasets.items():
        categories = value["categories"]
        total_items = sum(len(items) for items in categories.values())
        print(f"- {key}: 分类 {len(categories)} 个, 条目 {total_items} 条")
    print(f"- mostly_zh_lines: {len(report.suspicious_lines)}")
    print(f"- dropped_entries: {len(report.dropped_entries)}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    docx_path = repo_root / "tags001.docx"
    out_path = repo_root / "promptcard" / "PromptCardData.py"

    if not docx_path.exists():
        raise FileNotFoundError(f"未找到文档: {docx_path}")

    datasets, report = build_datasets(docx_path)
    dump_data_py(out_path, datasets)
    write_reports(repo_root, report)
    print_stats(datasets, report)
    print(f"已生成: {out_path}")


if __name__ == "__main__":
    main()

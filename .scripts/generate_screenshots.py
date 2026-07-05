from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
WIDTH = 1600
HEIGHT = 900

COLORS = {
    "bg": "#edf4ff",
    "surface": "#ffffff",
    "soft": "#f5f9ff",
    "line": "#cfe0f5",
    "line_soft": "#e4eefb",
    "text": "#10233f",
    "muted": "#5f7088",
    "accent": "#2563eb",
    "accent_dark": "#1d4ed8",
    "accent_soft": "#eaf2ff",
    "sky": "#0ea5e9",
}


def _font_path(bold: bool = False) -> Path | None:
    names = ["msyhbd.ttc", "msyh.ttc", "simhei.ttf", "simsun.ttc"] if bold else [
        "msyh.ttc",
        "simhei.ttf",
        "simsun.ttc",
    ]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return path
    return None


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _font_path(bold)
    if path:
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int = 24,
         fill: str = COLORS["text"], bold: bool = False) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill)


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int],
            fill: str = COLORS["surface"], outline: str = COLORS["line"],
            radius: int = 20, width: int = 2) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def line(draw: ImageDraw.ImageDraw, y: int, x1: int = 64, x2: int = 1536) -> None:
    draw.line((x1, y, x2, y), fill=COLORS["line_soft"], width=2)


def button(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], label: str,
           active: bool = False) -> None:
    fill = COLORS["accent"] if active else "#fbfdff"
    outline = COLORS["accent"] if active else COLORS["line"]
    fg = "#ffffff" if active else COLORS["text"]
    rounded(draw, xy, fill=fill, outline=outline, radius=14, width=2)
    bbox = draw.textbbox((0, 0), label, font=font(19, True))
    x = xy[0] + (xy[2] - xy[0] - (bbox[2] - bbox[0])) // 2
    y = xy[1] + (xy[3] - xy[1] - (bbox[3] - bbox[1])) // 2 - 2
    text(draw, (x, y), label, 19, fg, True)


def input_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], label: str,
              value: str, optional: str = "") -> None:
    lx, ly = xy[0], xy[1] - 34
    text(draw, (lx, ly), label, 18, COLORS["text"], True)
    if optional:
        text(draw, (lx + 84, ly + 2), optional, 15, COLORS["sky"], True)
    rounded(draw, xy, fill="#fbfdff", outline=COLORS["line"], radius=12, width=2)
    text(draw, (xy[0] + 20, xy[1] + 20), value, 20, COLORS["muted"] if value.startswith("例如") else COLORS["text"], True)


def textarea(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], label: str,
             lines: Iterable[str], action: str | None = None) -> None:
    text(draw, (xy[0], xy[1] - 34), label, 18, COLORS["text"], True)
    if action:
        button(draw, (xy[2] - 150, xy[1] - 48, xy[2], xy[1] - 8), action)
    rounded(draw, xy, fill="#fbfdff", outline=COLORS["line"], radius=12, width=2)
    y = xy[1] + 18
    for item in lines:
        text(draw, (xy[0] + 20, y), item, 19, COLORS["muted"])
        y += 34


def paste_logo(image: Image.Image, x: int, y: int, size: int) -> None:
    icon_path = ROOT / "src" / "weekflow_logo.ico"
    if not icon_path.exists():
        return
    try:
        icon = Image.open(icon_path).convert("RGBA")
        icon.thumbnail((size, size), Image.Resampling.LANCZOS)
        image.alpha_composite(icon, (x, y))
    except Exception:
        return


def base_canvas(active: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    rounded(draw, (28, 22, 1572, 106), fill="#fbfdff", outline=COLORS["line"], radius=22, width=2)
    paste_logo(image, 52, 42, 42)
    text(draw, (108, 48), "WeekFlow", 26, "#123b73", True)
    nav = ["基本信息", "成果感受", "项目进展", "待跟进", "预览"]
    x = 430
    for item in nav:
        w = 128 if item != "项目进展" else 138
        button(draw, (x, 42, x + w, 86), item, active == item)
        x += w + 12
    action_x = 1180
    for label, is_primary in [("新建", False), ("打开", False), ("保存", True), ("独立预览", False)]:
        w = 72 if len(label) == 2 else 112
        button(draw, (action_x, 42, action_x + w, 86), label, is_primary)
        action_x += w + 10
    return image, draw


def save(image: Image.Image, name: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(SCREENSHOT_DIR / name, quality=96)


def screenshot_home() -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    rounded(draw, (34, 28, 1566, 872), fill="#fbfdff", outline=COLORS["line"], radius=24, width=2)
    paste_logo(image, 690, 112, 92)
    text(draw, (666, 224), "WeekFlow", 48, "#123b73", True)
    text(draw, (540, 298), "选择 data 里的文件，或新建一份周报。", 26, COLORS["muted"])

    rounded(draw, (118, 390, 920, 760), fill="#ffffff", outline=COLORS["line"], radius=22, width=2)
    text(draw, (160, 430), "选择 data 里的文件", 30, "#123b73", True)
    button(draw, (662, 428, 806, 478), "打开文件", True)
    button(draw, (820, 428, 884, 478), "刷新")
    rounded(draw, (160, 518, 880, 640), fill=COLORS["accent_soft"], outline="#b7ccec", radius=16, width=2)
    text(draw, (190, 545), "demo-community", 24, COLORS["text"], True)
    text(draw, (190, 588), "data/demo-community/demo-community.json", 18, COLORS["muted"])
    text(draw, (190, 618), "含 Markdown 与 figs 图片目录", 18, COLORS["muted"])

    rounded(draw, (980, 390, 1482, 760), fill="#ffffff", outline=COLORS["line"], radius=22, width=2)
    text(draw, (1022, 430), "新建数据文件", 30, "#123b73", True)
    input_box(draw, (1022, 520, 1440, 574), "文件名", "例如：2026-week-01")
    input_box(draw, (1022, 642, 1440, 696), "项目名称", "例如：社区活动筹备")
    button(draw, (1264, 716, 1440, 766), "新建文件", True)
    save(image, "01-home.png")


def screenshot_basic() -> None:
    image, draw = base_canvas("基本信息")
    rounded(draw, (40, 130, 1560, 858), fill=COLORS["surface"], outline=COLORS["line"], radius=22, width=2)
    text(draw, (76, 176), "基本信息", 34, "#123b73", True)
    text(draw, (76, 224), "标题、AI 接入和总结放在一个页面里。", 20, COLORS["muted"])
    line(draw, 262, 76, 1524)

    input_box(draw, (76, 338, 730, 392), "标题", "社区活动筹备与资料整理")
    input_box(draw, (774, 338, 1160, 392), "Model / Endpoint", "qwen3.7-plus")
    button(draw, (1200, 338, 1350, 392), "测试 AI")
    text(draw, (1372, 352), "AI 请求成功", 19, COLORS["sky"], True)
    input_box(draw, (76, 480, 1000, 534), "Base URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    input_box(draw, (1040, 480, 1508, 534), "API Key", "不会出现在预览和导出内容中", "可选")

    textarea(draw, (76, 640, 1508, 812), "总结", [
        "完成社区活动资料整理和报名协调，活动物资清单已进入最终核对。",
        "下周重点是现场签到、物资验收和结果沉淀。"
    ], "AI 润色总结")
    save(image, "04-basic-ai.png")
    save(image, "04-ai-config.png")


def screenshot_results() -> None:
    image, draw = base_canvas("成果感受")
    rounded(draw, (40, 130, 1560, 858), fill=COLORS["surface"], outline=COLORS["line"], radius=22, width=2)
    text(draw, (76, 176), "成果 / 感受", 34, "#123b73", True)
    line(draw, 238, 76, 1524)

    rounded(draw, (76, 284, 754, 802), fill="#fbfdff", outline=COLORS["line"], radius=18, width=2)
    text(draw, (112, 326), "本周成果", 28, "#123b73", True)
    input_box(draw, (112, 420, 606, 474), "新增成果", "完成资料模板统一")
    button(draw, (624, 420, 716, 474), "添加")
    for y, label in [(536, "完成周报桌面端打包流程"), (604, "项目进展拆分成多个子页面"), (672, "修复 AI 链接识别与请求逻辑")]:
        rounded(draw, (112, y, 716, y + 48), fill="#ffffff", outline=COLORS["line_soft"], radius=10, width=1)
        text(draw, (132, y + 11), label, 20, COLORS["text"])

    rounded(draw, (846, 284, 1524, 802), fill="#fbfdff", outline=COLORS["line"], radius=18, width=2)
    text(draw, (882, 326), "本周感受", 28, "#123b73", True)
    textarea(draw, (882, 420, 1488, 714), "感受内容", [
        "这周最大的变化是把工作流从零散记录变成可以复用的结构。",
        "后续需要继续压缩填写成本，让周报像顺手记录一样自然。"
    ], "AI 润色")
    save(image, "02-results.png")


def screenshot_projects() -> None:
    image, draw = base_canvas("项目进展")
    rounded(draw, (40, 130, 1560, 858), fill=COLORS["surface"], outline=COLORS["line"], radius=22, width=2)
    text(draw, (76, 174), "项目进展", 34, "#123b73", True)
    text(draw, (76, 220), "先选项目，再进入查看、填写进展、记录结果或时间流水。", 20, COLORS["muted"])
    line(draw, 260, 76, 1524)

    rounded(draw, (76, 300, 420, 812), fill="#fbfdff", outline=COLORS["line"], radius=18, width=2)
    text(draw, (108, 336), "项目列表", 26, "#123b73", True)
    for i, (name, desc, active) in enumerate([
        ("场地与物资确认", "2 条流水 · 1 张图片", True),
        ("宣传与报名协调", "2 条流水 · 0 张图片", False),
        ("志愿者排班", "待补充", False),
    ]):
        y = 398 + i * 96
        fill = COLORS["accent_soft"] if active else "#ffffff"
        rounded(draw, (108, y, 388, y + 74), fill=fill, outline=COLORS["line_soft"], radius=12, width=1)
        text(draw, (130, y + 14), name, 20, COLORS["text"], True)
        text(draw, (130, y + 42), desc, 17, COLORS["muted"])
    button(draw, (108, 724, 228, 770), "新增")
    button(draw, (244, 724, 364, 770), "删除")

    text(draw, (472, 330), "场地与物资确认", 30, "#123b73", True)
    tab_x = 1010
    for label, active in [("查看项目", True), ("填写进展", False), ("记录结果", False), ("时间流水", False)]:
        button(draw, (tab_x, 322, tab_x + 114, 368), label, active)
        tab_x += 124
    line(draw, 394, 472, 1524)
    rounded(draw, (472, 436, 1494, 596), fill=COLORS["soft"], outline=COLORS["line"], radius=16, width=1)
    for x, title, body in [
        (506, "名称", "场地与物资确认"),
        (842, "本周推进", "已核对场地预约、桌椅摆放和基础物资清单。"),
        (1190, "下一步", "按最终报名人数补齐指引牌和签到用品。"),
    ]:
        text(draw, (x, 468), title, 20, COLORS["text"], True)
        text(draw, (x, 510), body, 18, COLORS["muted"])
    rounded(draw, (472, 638, 1494, 812), fill="#fffdf8", outline="#cfe0f5", radius=16, width=1)
    text(draw, (506, 672), "结果说明", 22, COLORS["text"], True)
    text(draw, (506, 710), "场地动线和物资摆放已整理成可执行版本。", 19, COLORS["muted"])
    text(draw, (1040, 672), "结果图片", 22, COLORS["text"], True)
    rounded(draw, (1040, 714, 1456, 766), fill="#ffffff", outline=COLORS["line_soft"], radius=10, width=1)
    text(draw, (1060, 728), "figs/demo-result-01.png", 18, COLORS["muted"])
    save(image, "03-projects.png")


def screenshot_preview() -> None:
    image, draw = base_canvas("预览")
    rounded(draw, (40, 130, 1560, 858), fill=COLORS["surface"], outline=COLORS["line"], radius=22, width=2)
    text(draw, (76, 176), "Markdown", 32, "#123b73", True)
    rounded(draw, (650, 170, 812, 220), fill="#fbfdff", outline=COLORS["line"], radius=12, width=2)
    text(draw, (684, 184), "报告蓝", 20, COLORS["text"], True)
    text(draw, (860, 176), "渲染预览", 32, "#123b73", True)
    line(draw, 246, 76, 1524)

    rounded(draw, (76, 286, 760, 812), fill="#fbfdff", outline=COLORS["line"], radius=16, width=2)
    md = [
        "# Week 01",
        "",
        "## 总结",
        "完成社区活动资料整理和报名协调。",
        "",
        "## 本周成果",
        "- 完成资料模板统一",
        "- 修复 AI 请求逻辑",
        "",
        "## 项目进展",
        "| 名称 | 内容 | 预计 |",
    ]
    y = 316
    for item in md:
        text(draw, (108, y), item, 19, COLORS["text"] if item.startswith("#") else COLORS["muted"], True if item.startswith("#") else False)
        y += 34

    rounded(draw, (830, 286, 1524, 812), fill="#ffffff", outline=COLORS["line"], radius=16, width=2)
    text(draw, (1098, 330), "Week 01", 28, "#123b73", True)
    text(draw, (1104, 402), "总结", 22, "#123b73", True)
    rounded(draw, (890, 450, 1464, 528), fill="#fbfdff", outline=COLORS["line_soft"], radius=12, width=1)
    text(draw, (918, 478), "完成社区活动资料整理和报名协调。", 20, COLORS["muted"])
    text(draw, (1086, 594), "项目进展", 22, "#123b73", True)
    draw.rectangle((890, 640, 1464, 704), fill=COLORS["soft"], outline=COLORS["line"])
    text(draw, (950, 660), "名称", 19, COLORS["text"], True)
    text(draw, (1140, 660), "内容", 19, COLORS["text"], True)
    text(draw, (1340, 660), "预计", 19, COLORS["text"], True)
    save(image, "05-preview.png")


def main() -> int:
    screenshot_home()
    screenshot_basic()
    screenshot_results()
    screenshot_projects()
    screenshot_preview()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

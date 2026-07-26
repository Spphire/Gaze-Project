from __future__ import annotations

import math
import re
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "patent_figures"
FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")

INK = "#17202A"
MUTED = "#53606B"
LINE = "#28323C"
FILL = "#F6F7F8"
FILL_DARK = "#E6EAED"
FILL_BLUE = "#EAF2F8"
FILL_GREEN = "#EAF5EF"
FILL_ORANGE = "#FBF1E8"
FILL_PURPLE = "#F3EEF8"
WHITE = "#FFFFFF"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def wrap_for_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        tokens = re.findall(r"[A-Za-z0-9_\[\]/+.^~=<>-]+|[ \t]+|.", paragraph)
        current = ""
        for token in tokens:
            candidate = current + token
            if current and draw.textlength(candidate, font=fnt) > width:
                lines.append(current.rstrip())
                current = token.lstrip()
            else:
                current = candidate
            if current and draw.textlength(current, font=fnt) > width:
                remainder = current
                current = ""
                while remainder:
                    split_at = len(remainder)
                    while split_at > 1 and draw.textlength(remainder[:split_at], font=fnt) > width:
                        split_at -= 1
                    lines.append(remainder[:split_at])
                    remainder = remainder[split_at:]
        if current:
            lines.append(current.rstrip())
    return lines


@dataclass
class Box:
    xy: tuple[int, int, int, int]
    title: str
    body: str = ""
    fill: str = FILL
    stroke: str = LINE
    title_size: int = 25
    body_size: int = 20
    dashed: bool = False


class Figure:
    def __init__(self, title: str, subtitle: str, size: tuple[int, int] = (2400, 1400)) -> None:
        self.image = Image.new("RGB", size, WHITE)
        self.draw = ImageDraw.Draw(self.image)
        self.width, self.height = size
        self.draw.text((70, 42), title, font=font(42, True), fill=INK)
        self.draw.text((72, 103), subtitle, font=font(21), fill=MUTED)
        self.draw.line((70, 145, self.width - 70, 145), fill=LINE, width=3)

    def label(self, xy: tuple[int, int], text: str, size: int = 22, bold: bool = False, fill: str = INK) -> None:
        self.draw.text(xy, text, font=font(size, bold), fill=fill)

    def box(self, spec: Box) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = spec.xy
        if spec.dashed:
            self._dashed_rect(spec.xy, spec.stroke, 3, 14)
            self.draw.rounded_rectangle(spec.xy, radius=8, fill=spec.fill, outline=None)
            self._dashed_rect(spec.xy, spec.stroke, 3, 14)
        else:
            self.draw.rounded_rectangle(spec.xy, radius=8, fill=spec.fill, outline=spec.stroke, width=3)
        title_font = font(spec.title_size, True)
        body_font = font(spec.body_size)
        pad = 20
        title_lines = wrap_for_width(self.draw, spec.title, title_font, x2 - x1 - pad * 2)
        y = y1 + 18
        for line in title_lines:
            self.draw.text((x1 + pad, y), line, font=title_font, fill=INK)
            y += spec.title_size + 9
        if spec.body:
            y += 4
            for line in wrap_for_width(self.draw, spec.body, body_font, x2 - x1 - pad * 2):
                self.draw.text((x1 + pad, y), line, font=body_font, fill=MUTED)
                y += spec.body_size + 8
        return spec.xy

    def arrow(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        label: str = "",
        dashed: bool = False,
        width: int = 4,
    ) -> None:
        if dashed:
            self._dashed_line(start, end, LINE, width, 18)
        else:
            self.draw.line((start, end), fill=LINE, width=width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        length = 18
        spread = 0.55
        p1 = (end[0] - length * math.cos(angle - spread), end[1] - length * math.sin(angle - spread))
        p2 = (end[0] - length * math.cos(angle + spread), end[1] - length * math.sin(angle + spread))
        self.draw.polygon([end, p1, p2], fill=LINE)
        if label:
            mx = (start[0] + end[0]) // 2
            my = (start[1] + end[1]) // 2
            fnt = font(18)
            bbox = self.draw.textbbox((0, 0), label, font=fnt)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            self.draw.rounded_rectangle((mx - tw // 2 - 8, my - th - 8, mx + tw // 2 + 8, my + 5), radius=4, fill=WHITE)
            self.draw.text((mx - tw // 2, my - th - 4), label, font=fnt, fill=MUTED)

    def diamond(self, center: tuple[int, int], size: tuple[int, int], title: str) -> tuple[int, int, int, int]:
        cx, cy = center
        w, h = size
        points = [(cx, cy - h // 2), (cx + w // 2, cy), (cx, cy + h // 2), (cx - w // 2, cy)]
        self.draw.polygon(points, fill=FILL_DARK, outline=LINE)
        self.draw.line(points + [points[0]], fill=LINE, width=3)
        fnt = font(23, True)
        lines = wrap_for_width(self.draw, title, fnt, int(w * 0.62))
        total = len(lines) * 31
        y = cy - total // 2
        for line in lines:
            tw = self.draw.textlength(line, font=fnt)
            self.draw.text((cx - tw / 2, y), line, font=fnt, fill=INK)
            y += 31
        return (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)

    def footer(self, text: str) -> None:
        self.draw.line((70, self.height - 78, self.width - 70, self.height - 78), fill="#A8B0B7", width=2)
        self.draw.text((72, self.height - 61), text, font=font(16), fill=MUTED)

    def save(self, name: str) -> Path:
        path = OUT / name
        self.image.save(path, format="PNG", dpi=(180, 180))
        return path

    def _dashed_rect(self, xy: tuple[int, int, int, int], color: str, width: int, dash: int) -> None:
        x1, y1, x2, y2 = xy
        for a, b in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
            self._dashed_line(a, b, color, width, dash)

    def _dashed_line(self, start: tuple[int, int], end: tuple[int, int], color: str, width: int, dash: int) -> None:
        x1, y1 = start
        x2, y2 = end
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return
        ux = (x2 - x1) / dist
        uy = (y2 - y1) / dist
        pos = 0.0
        draw_segment = True
        while pos < dist:
            nxt = min(dist, pos + dash)
            if draw_segment:
                self.draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * nxt, y1 + uy * nxt), fill=color, width=width)
            draw_segment = not draw_segment
            pos = nxt


def figure_1() -> Path:
    f = Figure(
        "图1  异构注视-动作数据逐样本监督路由的总体训练架构",
        "代码对应：gaze_wam_mixing.py、gaze_encoder.py、gaze_wam_policy.py、cached_dual_stream_transformer.py",
    )
    f.label((90, 178), "数据源", 25, True)
    f.box(Box((80, 225, 390, 390), "机器人示范数据", "图像、动作块、可选注视标签\n动作表示：[16,10]", FILL_ORANGE))
    f.box(Box((80, 475, 390, 640), "开放第一视角数据", "图像、注视标签\n无机器人动作标签", FILL_GREEN))
    f.box(Box((470, 300, 850, 565), "混合批次与显式路由标记", "is_open\nhas_action / has_heatmap\nhas_gaze_label\nuse_gaze_condition\nis_gaze_condition_dropped", FILL_DARK))
    f.label((955, 178), "三类样本状态", 25, True)
    f.box(Box((920, 220, 1270, 390), "机器人真实注视行", "真实注视作为条件\n动作监督：开\n热图监督：关", FILL_BLUE))
    f.box(Box((920, 455, 1270, 645), "机器人注视丢弃行", "可训练 [MASK] 作为条件\n动作监督：开\n热图监督：开", FILL_PURPLE))
    f.box(Box((920, 710, 1270, 880), "开放注视行", "可训练 [MASK] 作为条件\n动作监督：关\n热图监督：开", FILL_GREEN))
    f.box(Box((1370, 285, 1660, 440), "图像编码器", "DINOv3 patch tokens\n2 帧 x 256 tokens", FILL_BLUE))
    f.box(Box((1370, 535, 1660, 690), "注视编码器", "真实注视高斯基\n或 learned [MASK]", FILL_GREEN))
    f.box(Box((1750, 390, 2030, 585), "共享世界上下文塔", "image + gaze/[MASK]\n7 层 context blocks\n预填充逐层 K/V", FILL_DARK))
    f.box(Box((2110, 255, 2320, 430), "动作扩散流", "查询 world K/V\n输出动作噪声预测", FILL_ORANGE, title_size=23, body_size=18))
    f.box(Box((2110, 610, 2320, 785), "热图扩散流", "查询同一 world K/V\n输出 256x16 latent", FILL_PURPLE, title_size=23, body_size=18))
    f.box(Box((1735, 865, 2050, 1035), "逐样本掩码损失", "动作：(~is_open) & has_action\n热图：has_heatmap & has_gaze_label", WHITE))
    f.box(Box((2085, 925, 2335, 1095), "联合更新", "共享图像/世界表征\n目标流彼此隔离", FILL_DARK, title_size=23, body_size=18))

    f.arrow((390, 305), (470, 355))
    f.arrow((390, 555), (470, 510))
    f.arrow((850, 360), (920, 305))
    f.arrow((850, 430), (920, 550))
    f.arrow((850, 500), (920, 795))
    for y in (305, 550, 795):
        f.arrow((1270, y), (1370, 360 if y < 430 else 610))
    f.arrow((1660, 360), (1750, 445))
    f.arrow((1660, 610), (1750, 535))
    f.arrow((2030, 445), (2110, 340))
    f.arrow((2030, 535), (2110, 695))
    f.arrow((2215, 430), (1960, 865), "动作损失")
    f.arrow((2215, 785), (1985, 865), "热图损失")
    f.arrow((2050, 950), (2085, 1010))
    f.footer("关键约束：同一真实注视标签作为动作条件时，不同时作为热图监督目标；只有 [MASK] 条件行才可启用热图监督。")
    return f.save("figure_01_overall_training.png")


def figure_2() -> Path:
    f = Figure(
        "图2  单一样本的监督状态判定与防标签泄漏流程",
        "代码对应：build_gaze_wam_mixed_batch() 与 _validate_loss_batch_contract()",
    )
    start = f.box(Box((80, 225, 360, 355), "输入样本 i", "图像 I_i、可选动作 a_i、可选注视 q_i", WHITE))
    d1 = f.diamond((590, 290), (300, 175), "是否开放数据？")
    open_state = f.box(Box((870, 190, 1260, 385), "状态 O：开放注视行", "s_i=1, a_i=0, h_i=1\nc_i=0，使用 [MASK]\n只计入热图损失", FILL_GREEN))
    d2 = f.diamond((590, 565), (300, 175), "机器人行是否有注视标签？")
    no_gaze = f.box(Box((870, 485, 1260, 655), "状态 R0：机器人无注视", "动作监督保持开启\n注视条件强制 [MASK]\n无有效注视时热图损失关闭", FILL_ORANGE))
    d3 = f.diamond((590, 830), (320, 185), "是否触发注视条件丢弃？")
    real_gaze = f.box(Box((870, 745, 1260, 925), "状态 R1：机器人真实注视", "c_i=1，真实注视作条件\n动作损失开启\n热图损失关闭，避免复制标签", FILL_BLUE))
    dropped = f.box(Box((870, 1005, 1260, 1195), "状态 R2：机器人注视丢弃", "c_i=0，使用 [MASK]\n动作损失保持开启\n有效注视转为热图监督", FILL_PURPLE))
    contract = f.box(Box((1440, 225, 2250, 645), "统一张量契约与运行时校验", "1. 所有路由标记均为 [B] BoolTensor\n2. 无动作行的 action 为同形状零占位\n3. 无热图行的 heatmap 为零占位\n4. 无注视行的 gaze_xy 为零占位\n5. use_gaze_condition 不能在 has_gaze_label=False 时为真\n6. 开放行禁止动作监督且必须使用 [MASK]\n7. 机器人真实注视行禁止热图监督\n8. is_gaze_condition_dropped = NOT use_gaze_condition", FILL_DARK, title_size=27, body_size=21))
    formula = f.box(Box((1440, 750, 2250, 1080), "对应的样本级门控", "动作门控：m_i^a = (1-s_i) a_i\n热图门控：m_i^h = h_i g_i\n条件门控：c_i = (1-s_i) g_i (1-d_i)\n\n其中 s_i 为开放数据标记，a_i/h_i/g_i 为动作、热图、注视标签可用性，d_i 为机器人注视丢弃标记。", WHITE, title_size=27, body_size=22))

    f.arrow((360, 290), (440, 290))
    f.arrow((740, 290), (870, 290), "是")
    f.arrow((590, 378), (590, 478), "否")
    f.arrow((740, 565), (870, 565), "否")
    f.arrow((590, 652), (590, 738), "是")
    f.arrow((750, 830), (870, 835), "否")
    f.arrow((590, 923), (590, 1005), "是")
    for y in (290, 565, 835, 1100):
        f.arrow((1260, y), (1440, 430 if y < 700 else 900), dashed=True)
    f.footer("默认配置：robot_gaze_dropout_prob=0.2；robot_heatmap_on_gaze_dropout=True。缺失字段不通过隐式猜测，而由显式 presence mask 决定。")
    return f.save("figure_02_sample_routing.png")


def figure_3() -> Path:
    f = Figure(
        "图3  共享世界 K/V 缓存的动作-注视热图双流扩散网络",
        "代码对应：CachedDualStreamGazeWamTransformer.prefill_world_cache() 与 forward()",
    )
    f.label((90, 180), "稳定条件流", 25, True)
    f.box(Box((75, 230, 365, 370), "视觉 tokens", "[B, N_v, 768]", FILL_BLUE))
    f.box(Box((75, 455, 365, 595), "注视 / [MASK] token", "[B, 1, 768]", FILL_GREEN))
    f.box(Box((470, 310, 785, 520), "条件拼接与嵌入", "图像帧嵌入\n模态嵌入\n上下文位置嵌入", FILL_DARK))
    f.box(Box((895, 260, 1225, 565), "世界上下文塔", "7 个 ContextSelfBlock\n每层：自注意力 + MLP\n每层导出 K_l^w, V_l^w\n条件 token 不读取目标 token", FILL_DARK))
    f.box(Box((1330, 300, 1620, 525), "逐层 world cache", "{(K_l^w,V_l^w)}\nl=1,...,7\n同一条件只预填充一次", WHITE))

    f.label((90, 720), "目标流 A：动作", 25, True)
    f.box(Box((75, 770, 365, 930), "noisy action + t", "[B,16,10]\n动作位置/模态/时间嵌入", FILL_ORANGE))
    f.box(Box((500, 750, 900, 965), "7 个动作 TargetDecoderBlock", "Q 来自动作 token\nK/V = [world cache；动作自身 K/V]\n不读取 heatmap token", FILL_ORANGE))
    f.box(Box((1010, 790, 1285, 920), "动作噪声预测", "[B,16,10]", FILL_ORANGE))

    f.label((1390, 720), "目标流 H：注视热图", 25, True)
    f.box(Box((1360, 770, 1655, 930), "noisy heatmap + t", "[B,256,16]\n热图位置/模态/时间嵌入", FILL_PURPLE))
    f.box(Box((1755, 750, 2165, 965), "7 个热图 TargetDecoderBlock", "Q 来自热图 token\nK/V = [world cache；热图自身 K/V]\n不读取 action token", FILL_PURPLE))
    f.box(Box((2190, 790, 2360, 920), "热图 latent", "[B,256,16]", FILL_PURPLE, title_size=22, body_size=18))

    f.arrow((365, 300), (470, 365))
    f.arrow((365, 525), (470, 465))
    f.arrow((785, 410), (895, 410))
    f.arrow((1225, 410), (1330, 410), "逐层 K/V")
    f.arrow((365, 850), (500, 850))
    f.arrow((900, 850), (1010, 850))
    f.arrow((1655, 850), (1755, 850))
    f.arrow((2165, 850), (2190, 850))
    f.arrow((1475, 525), (700, 750), "每层复用", dashed=True)
    f.arrow((1475, 525), (1960, 750), "每层复用", dashed=True)
    f.box(Box((475, 1060, 2160, 1225), "混合注意力关系", "目标流 r 的查询只与共享世界 K/V 及该目标流自身 K/V 拼接计算；动作流与热图流之间不存在目标 token 的交叉读取。正式动作推理时 noisy_heatmap=None，热图解码器完全跳过。", WHITE, title_size=25, body_size=21))
    f.footer("代码契约：shared_world_kv_cache=True；action_reads_heatmap=False；heatmap_reads_action=False；action_inference_drops_heatmap=True。")
    return f.save("figure_03_dual_stream_cache.png")


def figure_4() -> Path:
    f = Figure(
        "图4  联合训练路径与正式动作推理路径",
        "代码对应：GazeWamPolicy.compute_loss_components()、conditional_sample() 与 predict_action()",
    )
    f.label((80, 180), "联合训练", 28, True)
    train_boxes = [
        Box((70, 235, 360, 415), "批次条件编码", "图像 + 真实注视/[MASK]\n生成 world cache", FILL_DARK),
        Box((455, 235, 760, 415), "共享 timestep", "t ~ Uniform{0,...,49}\n动作与热图分别加噪", FILL),
        Box((855, 205, 1190, 390), "动作扩散解码", "输出 epsilon_a\n动作行 masked mean", FILL_ORANGE),
        Box((855, 455, 1190, 640), "热图扩散解码", "输出 clean latent\nFrozen Cosmos 解码", FILL_PURPLE),
        Box((1310, 205, 1650, 390), "动作损失", "mask=(~is_open)&has_action\n逐样本 MSE", FILL_ORANGE),
        Box((1310, 455, 1650, 640), "热图损失", "mask=has_heatmap&has_gaze_label\nDSNT XY + spatial JS", FILL_PURPLE),
        Box((1780, 315, 2240, 510), "总损失与参数更新", "L = lambda_a L_a + lambda_h L_h\n共同更新视觉编码器与世界塔\n分别更新动作头、热图头", FILL_DARK),
    ]
    for b in train_boxes:
        f.box(b)
    f.arrow((360, 325), (455, 325))
    f.arrow((760, 325), (855, 300))
    f.arrow((760, 355), (855, 545))
    f.arrow((1190, 300), (1310, 300))
    f.arrow((1190, 545), (1310, 545))
    f.arrow((1650, 300), (1780, 385))
    f.arrow((1650, 545), (1780, 440))

    f.draw.line((70, 700, 2330, 700), fill="#A8B0B7", width=3)
    f.label((80, 745), "正式动作推理", 28, True)
    f.box(Box((70, 810, 400, 995), "当前观测与可选注视", "图像 + 真实注视或 [MASK]\n不需要热图目标", FILL_BLUE))
    f.box(Box((510, 810, 850, 995), "world cache 预填充一次", "稳定条件通过 7 层上下文塔\n保存逐层 K/V", FILL_DARK))
    f.box(Box((970, 790, 1370, 1015), "8 步 DDIM 动作去噪", "初始化 x_T^a ~ N(0,I)\n每一步仅运行动作解码器\n重复读取同一 world cache", FILL_ORANGE))
    f.box(Box((1490, 810, 1810, 995), "动作块输出", "反归一化相对动作\n可选恢复绝对 TCP 位姿", FILL_ORANGE))
    f.box(Box((1925, 805, 2300, 1005), "热图流在正式推理中省略", "noisy_heatmap=None\nheatmap output=None\n不承担视频/热图生成延迟", WHITE, dashed=True))
    f.arrow((400, 900), (510, 900))
    f.arrow((850, 900), (970, 900))
    f.arrow((1370, 900), (1490, 900))
    f.arrow((1810, 900), (1925, 900), "明确省略", dashed=True)
    f.box(Box((430, 1115, 1960, 1235), "推理技术效果", "共享世界表征只计算一次；热图辅助任务只在训练期塑造世界表征，不进入正式动作生成路径，从而保持动作策略的实时性。", FILL_DARK, title_size=24, body_size=20))
    f.footer("主配置：50 个训练扩散步、8 个推理步、action_horizon=16、action_dim=10、heatmap latent=256x16、cfg_scale=1.0。")
    return f.save("figure_04_train_inference.png")


@dataclass
class DrawioNode:
    node_id: str
    label: str
    x: int
    y: int
    width: int = 210
    height: int = 80
    fill: str = "#FFFFFF"
    dashed: bool = False


@dataclass
class DrawioEdge:
    edge_id: str
    source: str
    target: str
    label: str = ""
    dashed: bool = False


def drawio_page(name: str, nodes: Iterable[DrawioNode], edges: Iterable[DrawioEdge]) -> ET.Element:
    diagram = ET.Element("diagram", {"id": name.replace(" ", "_"), "name": name})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1800",
            "dy": "1100",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "1900",
            "pageHeight": "1100",
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    title = ET.SubElement(
        root,
        "mxCell",
        {
            "id": f"{name}_title",
            "value": name,
            "style": "text;html=1;align=left;verticalAlign=middle;fontFamily=Microsoft YaHei;fontSize=26;fontStyle=1;fontColor=#17202A;strokeColor=none;fillColor=none;",
            "vertex": "1",
            "parent": "1",
        },
    )
    ET.SubElement(title, "mxGeometry", {"x": "40", "y": "20", "width": "1600", "height": "45", "as": "geometry"})
    for n in nodes:
        style = (
            "rounded=1;whiteSpace=wrap;html=1;arcSize=8;strokeWidth=1.5;"
            "fontFamily=Microsoft YaHei;fontSize=13;align=center;verticalAlign=middle;spacing=8;"
            f"fillColor={n.fill};strokeColor=#28323C;fontColor=#17202A;"
        )
        if n.dashed:
            style += "dashed=1;"
        cell = ET.SubElement(
            root,
            "mxCell",
            {"id": n.node_id, "value": n.label, "style": style, "vertex": "1", "parent": "1"},
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {"x": str(n.x), "y": str(n.y), "width": str(n.width), "height": str(n.height), "as": "geometry"},
        )
    for e in edges:
        style = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#28323C;strokeWidth=1.7;endArrow=classic;"
        if e.dashed:
            style += "dashed=1;"
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": e.edge_id,
                "value": e.label,
                "style": style,
                "edge": "1",
                "source": e.source,
                "target": e.target,
                "parent": "1",
            },
        )
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    return diagram


def write_drawio() -> Path:
    mxfile = ET.Element(
        "mxfile",
        {"host": "app.diagrams.net", "modified": "2026-07-27T00:00:00.000Z", "agent": "Codex", "version": "26.0.4", "compressed": "false"},
    )

    pages: list[ET.Element] = []
    pages.append(
        drawio_page(
            "图1 总体训练架构",
            [
                DrawioNode("f1_robot", "机器人示范<br>图像 + 动作 + 可选注视", 40, 160, 250, 100, "#FBF1E8"),
                DrawioNode("f1_open", "开放第一视角<br>图像 + 注视，无动作", 40, 350, 250, 100, "#EAF5EF"),
                DrawioNode("f1_route", "逐样本路由标记<br>is_open / has_action / has_heatmap<br>has_gaze_label / use_gaze_condition", 380, 245, 330, 140, "#E6EAED"),
                DrawioNode("f1_r1", "机器人真实注视行<br>真实注视作条件<br>仅动作监督", 800, 100, 280, 110, "#EAF2F8"),
                DrawioNode("f1_r2", "机器人注视丢弃行<br>[MASK] 作条件<br>动作 + 热图监督", 800, 285, 280, 110, "#F3EEF8"),
                DrawioNode("f1_o", "开放注视行<br>[MASK] 作条件<br>仅热图监督", 800, 470, 280, 110, "#EAF5EF"),
                DrawioNode("f1_enc", "图像编码 + 注视编码<br>真实注视或 learned [MASK]", 1180, 245, 300, 130, "#EAF2F8"),
                DrawioNode("f1_world", "世界上下文塔<br>逐层 K/V cache", 1570, 245, 250, 130, "#E6EAED"),
                DrawioNode("f1_action", "动作扩散解码器<br>[B,16,10]", 1180, 670, 280, 100, "#FBF1E8"),
                DrawioNode("f1_heat", "热图扩散解码器<br>[B,256,16]", 1570, 670, 280, 100, "#F3EEF8"),
                DrawioNode("f1_loss", "掩码损失并联合更新<br>动作门控 + 热图门控", 1370, 865, 300, 100, "#E6EAED"),
            ],
            [
                DrawioEdge("f1_e1", "f1_robot", "f1_route"),
                DrawioEdge("f1_e2", "f1_open", "f1_route"),
                DrawioEdge("f1_e3", "f1_route", "f1_r1"),
                DrawioEdge("f1_e4", "f1_route", "f1_r2"),
                DrawioEdge("f1_e5", "f1_route", "f1_o"),
                DrawioEdge("f1_e6", "f1_r1", "f1_enc"),
                DrawioEdge("f1_e7", "f1_r2", "f1_enc"),
                DrawioEdge("f1_e8", "f1_o", "f1_enc"),
                DrawioEdge("f1_e9", "f1_enc", "f1_world"),
                DrawioEdge("f1_e10", "f1_world", "f1_action", "共享 K/V", True),
                DrawioEdge("f1_e11", "f1_world", "f1_heat", "共享 K/V", True),
                DrawioEdge("f1_e12", "f1_action", "f1_loss"),
                DrawioEdge("f1_e13", "f1_heat", "f1_loss"),
            ],
        )
    )
    pages.append(
        drawio_page(
            "图2 样本路由与防泄漏",
            [
                DrawioNode("f2_in", "样本 i", 50, 220, 180, 80),
                DrawioNode("f2_source", "is_open?", 330, 220, 190, 80, "#E6EAED"),
                DrawioNode("f2_open", "开放行 O<br>[MASK] 条件<br>仅热图监督", 650, 90, 260, 110, "#EAF5EF"),
                DrawioNode("f2_label", "机器人行<br>has_gaze_label?", 650, 285, 260, 100, "#E6EAED"),
                DrawioNode("f2_r0", "机器人无注视 R0<br>动作监督<br>[MASK] 条件", 1030, 230, 280, 110, "#FBF1E8"),
                DrawioNode("f2_drop", "drop gaze condition?", 1030, 430, 280, 90, "#E6EAED"),
                DrawioNode("f2_r1", "真实注视 R1<br>真实注视作条件<br>仅动作监督", 1450, 345, 280, 115, "#EAF2F8"),
                DrawioNode("f2_r2", "注视丢弃 R2<br>[MASK] 条件<br>动作 + 热图监督", 1450, 530, 280, 115, "#F3EEF8"),
                DrawioNode("f2_guard", "统一校验<br>Bool [B] 路由 + 零占位<br>真实注视条件行禁止热图监督", 680, 740, 430, 150, "#E6EAED"),
                DrawioNode("f2_mask", "m_i^a=(1-s_i)a_i<br>m_i^h=h_i g_i<br>c_i=(1-s_i)g_i(1-d_i)", 1260, 750, 430, 130),
            ],
            [
                DrawioEdge("f2_e1", "f2_in", "f2_source"),
                DrawioEdge("f2_e2", "f2_source", "f2_open", "是"),
                DrawioEdge("f2_e3", "f2_source", "f2_label", "否"),
                DrawioEdge("f2_e4", "f2_label", "f2_r0", "否"),
                DrawioEdge("f2_e5", "f2_label", "f2_drop", "是"),
                DrawioEdge("f2_e6", "f2_drop", "f2_r1", "否"),
                DrawioEdge("f2_e7", "f2_drop", "f2_r2", "是"),
                DrawioEdge("f2_e8", "f2_open", "f2_guard", "", True),
                DrawioEdge("f2_e9", "f2_r0", "f2_guard", "", True),
                DrawioEdge("f2_e10", "f2_r1", "f2_guard", "", True),
                DrawioEdge("f2_e11", "f2_r2", "f2_guard", "", True),
                DrawioEdge("f2_e12", "f2_guard", "f2_mask"),
            ],
        )
    )
    pages.append(
        drawio_page(
            "图3 双流世界缓存",
            [
                DrawioNode("f3_img", "视觉 tokens<br>[B,N_v,768]", 40, 170, 230, 90, "#EAF2F8"),
                DrawioNode("f3_gaze", "注视/[MASK] token<br>[B,1,768]", 40, 340, 230, 90, "#EAF5EF"),
                DrawioNode("f3_cat", "拼接 + 模态/位置嵌入", 380, 250, 270, 100, "#E6EAED"),
                DrawioNode("f3_ctx", "7 层 ContextSelfBlock", 770, 250, 260, 100, "#E6EAED"),
                DrawioNode("f3_cache", "逐层 world cache<br>{K_l^w,V_l^w}", 1160, 250, 250, 100),
                DrawioNode("f3_ain", "noisy action + t", 360, 610, 250, 90, "#FBF1E8"),
                DrawioNode("f3_ab", "7 层 action blocks<br>world K/V + action K/V", 760, 590, 310, 130, "#FBF1E8"),
                DrawioNode("f3_aout", "动作噪声预测<br>[B,16,10]", 1190, 610, 250, 90, "#FBF1E8"),
                DrawioNode("f3_hin", "noisy heatmap + t", 360, 830, 250, 90, "#F3EEF8"),
                DrawioNode("f3_hb", "7 层 heatmap blocks<br>world K/V + heatmap K/V", 760, 810, 310, 130, "#F3EEF8"),
                DrawioNode("f3_hout", "热图 latent 预测<br>[B,256,16]", 1190, 830, 250, 90, "#F3EEF8"),
                DrawioNode("f3_iso", "目标流隔离<br>action 不读 heatmap<br>heatmap 不读 action", 1550, 640, 290, 150, "#E6EAED"),
            ],
            [
                DrawioEdge("f3_e1", "f3_img", "f3_cat"),
                DrawioEdge("f3_e2", "f3_gaze", "f3_cat"),
                DrawioEdge("f3_e3", "f3_cat", "f3_ctx"),
                DrawioEdge("f3_e4", "f3_ctx", "f3_cache"),
                DrawioEdge("f3_e5", "f3_ain", "f3_ab"),
                DrawioEdge("f3_e6", "f3_ab", "f3_aout"),
                DrawioEdge("f3_e7", "f3_hin", "f3_hb"),
                DrawioEdge("f3_e8", "f3_hb", "f3_hout"),
                DrawioEdge("f3_e9", "f3_cache", "f3_ab", "逐层复用", True),
                DrawioEdge("f3_e10", "f3_cache", "f3_hb", "逐层复用", True),
                DrawioEdge("f3_e11", "f3_aout", "f3_iso", "", True),
                DrawioEdge("f3_e12", "f3_hout", "f3_iso", "", True),
            ],
        )
    )
    pages.append(
        drawio_page(
            "图4 训练与正式推理",
            [
                DrawioNode("f4_batch", "训练批次条件编码", 40, 150, 240, 90, "#E6EAED"),
                DrawioNode("f4_noise", "共享 timestep<br>动作/热图分别加噪", 370, 150, 250, 90),
                DrawioNode("f4_ad", "动作解码器", 740, 90, 230, 80, "#FBF1E8"),
                DrawioNode("f4_hd", "热图解码器", 740, 240, 230, 80, "#F3EEF8"),
                DrawioNode("f4_al", "masked action MSE", 1090, 90, 250, 80, "#FBF1E8"),
                DrawioNode("f4_hl", "masked DSNT + JS", 1090, 240, 250, 80, "#F3EEF8"),
                DrawioNode("f4_total", "总损失<br>更新共享世界表征", 1480, 160, 280, 100, "#E6EAED"),
                DrawioNode("f4_obs", "正式推理观测<br>图像 + 注视/[MASK]", 40, 610, 260, 100, "#EAF2F8"),
                DrawioNode("f4_prefill", "world cache 预填充一次", 420, 610, 280, 100, "#E6EAED"),
                DrawioNode("f4_ddim", "8 步 DDIM<br>仅动作解码器", 830, 600, 280, 120, "#FBF1E8"),
                DrawioNode("f4_action", "动作块输出", 1240, 610, 240, 100, "#FBF1E8"),
                DrawioNode("f4_skip", "热图流省略<br>noisy_heatmap=None", 1600, 610, 250, 100, "#FFFFFF", True),
            ],
            [
                DrawioEdge("f4_e1", "f4_batch", "f4_noise"),
                DrawioEdge("f4_e2", "f4_noise", "f4_ad"),
                DrawioEdge("f4_e3", "f4_noise", "f4_hd"),
                DrawioEdge("f4_e4", "f4_ad", "f4_al"),
                DrawioEdge("f4_e5", "f4_hd", "f4_hl"),
                DrawioEdge("f4_e6", "f4_al", "f4_total"),
                DrawioEdge("f4_e7", "f4_hl", "f4_total"),
                DrawioEdge("f4_e8", "f4_obs", "f4_prefill"),
                DrawioEdge("f4_e9", "f4_prefill", "f4_ddim"),
                DrawioEdge("f4_e10", "f4_ddim", "f4_action"),
                DrawioEdge("f4_e11", "f4_action", "f4_skip", "明确不执行", True),
            ],
        )
    )
    mxfile.extend(pages)
    ET.indent(mxfile, space="  ")
    path = OUT / "gaze_wam_patent_figures.drawio"
    ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = [figure_1(), figure_2(), figure_3(), figure_4(), write_drawio()]
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()

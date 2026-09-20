# -*- coding: utf-8 -*-
"""按既有音频把 7 大类细分为 18 子类，导出「音频细分方案.txt」到 config 目录。
注意：本脚本只生成方案文档，不修改 categories.json。"""
import json, os, datetime

base = r"C:\project\miniprogram\BabyLearn\BabyLearnResources\config"
cfg = os.path.join(base, "categories.json")
out = os.path.join(base, "音频细分方案.txt")

with open(cfg, encoding="utf-8") as f:
    d = json.load(f)

# 细分映射：子类id -> (中文标签, 父分类id, [曲目标题列表])
PLAN = {
    # ---- 动物叫声(37) -> 3 ----
    "farm":      ("农场动物",   "dongwu", [
        "小狗的声音","小猫的声音","小鸭的声音","小牛的声音","小羊的声音","小鸡的声音",
        "大公鸡的声音","小猪的声音","小鹅的声音","小驴的声音","小马的声音","小仓鼠的声音"]),
    "wild":      ("野生动物",   "dongwu", [
        "小猴子的声音","大象的声音","大狮子的声音","大老虎的声音","海豚的声音","鹦鹉的声音",
        "猫头鹰的声音","松鼠的声音","火鸡的声音","恐龙的声音","海狮的声音","小熊的声音",
        "蛇的声音","大雁的声音","企鹅的声音","河马的声音","鳄鱼的声音"]),
    "other_ani": ("其他动物",   "dongwu", [
        "小青蛙的声音","小蜜蜂的声音","蝙蝠的声音","狐狸的声音","长颈鹿的声音","猎豹的声音",
        "大灰狼的声音","小老鼠的声音"]),
    # ---- 交通声音(27) -> 5 ----
    "road":      ("汽车与摩托", "jiaotong", [
        "汽车的声音","摩托车的声音","拖拉机的声音","公交车的声音","大卡车的声音","汽车喇叭声",
        "三轮车的声音","雪地摩托的声音","滑板车的声音","马蹄声"]),
    "rail":      ("轨道列车",   "jiaotong", [
        "火车的声音","地铁进站声","有轨电车的声音","火车轨道咣当声","高铁的声音","缆车的声音"]),
    "air":       ("飞机与飞行", "jiaotong", [
        "飞机的声音","直升机的声音","火箭发射的声音","热气球的声音"]),
    "water_veh": ("船舶水域",   "jiaotong", [
        "轮船的声音","快艇的声音","龙舟鼓声"]),
    "emergency": ("应急与警示", "jiaotong", [
        "救护车的声音","警车的声音","消防车的声音","铁路道口警报"]),
    # ---- 自然声音(33) -> 4 ----
    "weather":   ("风雨雷电",   "ziran", [
        "雨声","风声","雷声","暴风雨声","雨打屋檐","冰雹声","冰面开裂声","暴风雪","夏日雷阵雨"]),
    "water_nat": ("流水水体",   "ziran", [
        "流水声","海浪声","瀑布声","山洞滴水声","春溪解冻","深海之声","雨打帐篷","鲸鱼叫声"]),
    "birds":     ("鸟虫自然",   "ziran", [
        "鸟鸣声","虫鸣声","蝉鸣声","布谷鸟叫声","鸽子咕咕声","啄木鸟敲树声","海鸥鸣叫声","夜晚蛙鸣","夏夜合奏"]),
    "forest":    ("森林原野",   "ziran", [
        "森林之声","篝火声","树叶沙沙声","竹林风","松涛","清晨鸟语","山谷回声"]),
    # ---- 乐器声音(31) -> 3 ----
    "str_key":   ("弦乐与键盘", "yueqi", [
        "钢琴声","小提琴声","吉他声","大提琴声","竖琴声","尤克里里扫弦","二胡声","古筝声",
        "琵琶声","扬琴声","手风琴声"]),
    "wind_ins":  ("管乐",       "yueqi", [
        "小号声","笛子声","萨克斯声","口琴声","长号声","风笛声","卡林巴琴声","排箫声","唢呐声","葫芦丝声"]),
    "perc":      ("打击乐",     "yueqi", [
        "小鼓声","木琴声","铃鼓声","锣声","沙锤声","编钟声","木鱼声","钢鼓","颤音琴","响板"]),
    # ---- 保持 3 类 ----
    "douxiao":   ("逗你笑",     "douxiao", None),
    "lingsheng": ("铃声",       "lingsheng", None),
    "shengxiao": ("照相声效",   "shengxiao", None),
}

# 校验：按父分类聚合「方案子类曲目标题并集」应 == 父分类全部曲目，且子类间不重叠
cats = {c["id"]: c for c in d["categories"]}
errors = []
# 聚合每个父分类在方案中的曲目
parent_plan = {}
overlap_check = {}
for sub_id, (label, parent, titles) in PLAN.items():
    if titles is None:
        continue
    parent_plan.setdefault(parent, []).extend(titles)
    # 子类间重叠检测
    if parent in overlap_check and (set(titles) & overlap_check[parent]):
        errors.append(f"[{sub_id}] 与同父类其他子类重叠: {set(titles) & overlap_check[parent]}")
    overlap_check.setdefault(parent, set()).update(titles)

for parent, plan_titles in parent_plan.items():
    parent_titles = {t["title"] for t in cats[parent]["playlist"]}
    ps, pt = set(plan_titles), parent_titles
    if ps - pt:
        errors.append(f"[{parent}] 方案含父分类不存在的曲目: {ps - pt}")
    if pt - ps:
        errors.append(f"[{parent}] 父分类有未分配曲目({len(pt-ps)}条): {pt - ps}")

if errors:
    raise SystemExit("映射校验失败:\n" + "\n".join(errors))

# 汇总
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
subcats = [(sid, v[0], v[1], (len(v[2]) if v[2] else len(cats[v[1]]["playlist"]))) for sid, v in PLAN.items()]
by_parent = {}
for sid, label, parent, n in subcats:
    by_parent.setdefault(parent, []).append((label, n))

lines = []
lines.append("宝宝认知小乐园 · 音频细分方案（规划稿）")
lines.append("=" * 56)
lines.append("生成时间：%s" % now)
lines.append("数据来源：config/categories.json (version=%s，当前仍为 7 大类)" % d.get("version"))
lines.append("性质：本文件为「界面细分」规划文档，不修改 categories.json。")
lines.append("目标：首页网格由 7 个 tile 增至 18 个，消除界面太空；零新增音频、")
lines.append("      音频文件与总量（216 条）不变，仅做重归类。")
lines.append("原则：子类图标暂复用父分类现有图（如动物三子类共用 dongwu.jpg），")
lines.append("      后续可换独立图标；红线形态不变，不引入音乐/有声读物。")
lines.append("")
lines.append("总览：7 大类 → 18 子类（动物3 / 交通5 / 自然4 / 乐器3 / 逗你笑1 / 铃声1 / 照相1）")
lines.append("")

sep = "-" * 56
for c in sorted(d["categories"], key=lambda c: c["order"]):
    pid = c["id"]
    children = by_parent.get(pid, [])
    lines.append(sep)
    lines.append("大类 %d：%s  (%s)  —— 现有 %d 条 → 细分为 %d 子类"
                 % (c["order"], c["label"], pid, len(c["playlist"]), len(children)))
    lines.append("  " + sep)
    for label, n in children:
        lines.append("  ▸ %s   (%d 条)" % (label, n))
    lines.append("")

lines.append(sep)
lines.append("子类明细（标题 -> 归属子类）")
lines.append(sep)
for sid, (label, parent, titles) in PLAN.items():
    if titles is None:
        lines.append("%s：保持原大类（%d 条）" % (label, len(cats[parent]["playlist"])))
        continue
    lines.append("%s  [%s] 共 %d 条：" % (label, sid, len(titles)))
    for t in titles:
        lines.append("    - %s" % t)
    lines.append("")

lines.append(sep)
lines.append("落地步骤（后续执行，非本文件范围）：")
lines.append("  1. 将本方案写入 categories.json：每个父类拆为多个子类，order 连续编排。")
lines.append("  2. 为 15 个新子类补图片 images/<subid>.jpg（先复制父图或生成独立图标）。")
lines.append("  3. 重跑 gen_offline_pack.py 同步 BabyLearnLand/data/local-categories.js 离线兜底。")
lines.append("  4. 校验 JSON 合法、src 唯一、order 连续 1..18。")
lines.append("  5. 越线曲目（绕口令×12 / 约德尔 / 冰淇淋车音乐）保持 enabled:false。")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("已生成:", out)
print("子类总数:", len(PLAN), "（应为 18）")
print("映射校验: 通过" if not errors else "校验失败")

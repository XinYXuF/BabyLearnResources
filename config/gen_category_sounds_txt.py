# -*- coding: utf-8 -*-
"""读取 categories.json，导出一份「声音分类清单.txt」到同目录。"""
import json, os, datetime

base = r"C:\project\miniprogram\BabyLearn\BabyLearnResources\config"
cfg = os.path.join(base, "categories.json")
out = os.path.join(base, "声音分类清单.txt")

with open(cfg, encoding="utf-8") as f:
    d = json.load(f)

cats = sorted(d["categories"], key=lambda c: c["order"])
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

lines = []
lines.append("宝宝认知小乐园 · 声音分类清单")
lines.append("=" * 52)
lines.append("生成时间：%s" % now)
lines.append("数据来源：config/categories.json (version=%s)" % d.get("version"))
lines.append("说明：本文件为音频分类与曲目的纯文本快照，便于人工核对与审计。")
lines.append("")

total = sum(len(c["playlist"]) for c in cats)
enabled_total = sum(1 for c in cats for t in c["playlist"] if t.get("enabled", True))
disabled_total = total - enabled_total
lines.append("汇总：共 %d 个分类，%d 条曲目（启用 %d / 已下架 %d）"
             % (len(cats), total, enabled_total, disabled_total))
lines.append("")

sep = "-" * 52
for c in cats:
    cat_enabled = c.get("enabled", True)
    pl = sorted(c["playlist"], key=lambda t: t["order"])
    n_on = sum(1 for t in pl if t.get("enabled", True))
    n_off = len(pl) - n_on
    lines.append(sep)
    lines.append("分类 %d：%s  (%s)" % (c["order"], c["label"], c["id"]))
    lines.append("  图标：%s" % c.get("image", ""))
    lines.append("  状态：%s" % ("启用" if cat_enabled else "已下架"))
    lines.append("  曲目：%d 条（启用 %d / 下架 %d）" % (len(pl), n_on, n_off))
    lines.append("  " + "-" * 48)
    for t in pl:
        flag = "启用" if t.get("enabled", True) else "下架"
        lines.append("    %2d. %-18s %-42s [%s]"
                     % (t["order"], t["title"], t["src"], flag))
    lines.append("")

lines.append(sep)
lines.append("备注：")
lines.append("  - 已下架曲目仍保留文件，仅不进入线上包与网格。")
lines.append("  - 红线依据《内容红线.md》：音乐服务（含旋律/演唱/器乐曲）与")
lines.append("    有声读物（含朗读/绕口令/讲解）禁止提供。")
lines.append("  - 本清单为自动生成快照，categories.json 变更后请重新运行本脚本。")

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("已生成:", out)
print("分类数:", len(cats), "曲目数:", total, "启用:", enabled_total, "下架:", disabled_total)

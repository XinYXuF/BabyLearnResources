# -*- coding: utf-8 -*-
"""
音频路径迁移脚本：把 audio/ 目录结构与 config/categories.json 的分类 id 对齐。
1) 启用曲目的 src 从旧目录（如 audio/dongwu/）迁移到 audio/{分类id}/（磁盘移动 + 配置同步）；
2) 每条启用曲目显式写入 image 字段（images/{分类id}/{音频名}.jpg，文件已由 organize_assets.py 归位）；
3) JSON 用逐行文本处理保持原有缩进格式，写回前做 json.loads 校验；
4) 迁移后清理 audio 下的空目录。
用法：python scripts/migrate_audio_paths.py           # 预演：只打印计划
     python scripts/migrate_audio_paths.py --apply    # 执行
文件均在 git 仓库内，误操作可用 git restore 恢复。
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, 'config', 'categories.json')
AUDIO_DIR = os.path.join(ROOT, 'audio')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv


def main():
    with open(CFG, encoding='utf-8', newline='') as f:
        raw = f.read()
    cfg = json.loads(raw)
    # 换行风格保持：按文件实际使用的换行符切分
    sep = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(sep)

    # ---------- 收集映射：唯一 src -> 首个引用它的分类 id ----------
    src_cid = {}
    for cat in cfg.get('categories', []):
        cid = cat.get('id', '')
        for t in cat.get('playlist', []):
            src = t.get('src', '')
            if not src or not t.get('enabled', True):
                continue  # 下架曲目不迁移
            src_cid.setdefault(src, cid)

    # ---------- 生成迁移计划 ----------
    # {旧src: 新src}：分类 id 与旧目录相同时路径不变，无需迁移
    src_map = {}
    for src, cid in src_cid.items():
        fn = os.path.basename(src)
        new_src = 'audio/' + cid + '/' + fn
        if new_src != src:
            src_map[src] = new_src
    # 曲目图地址：images/{分类id}/{音频名}.jpg（按迁移后路径推导）
    img_map = {}
    missing_img = []
    for src, new_src in src_map.items():
        cid = src_cid[src]
        stem = os.path.splitext(os.path.basename(src))[0]
        img = 'images/' + cid + '/' + stem + '.jpg'
        img_map[new_src] = img
        if not os.path.exists(os.path.join(ROOT, img)):
            missing_img.append((new_src, img))

    # ---------- 磁盘移动计划 ----------
    move_plan = []
    for src, new_src in src_map.items():
        old_abs = os.path.join(ROOT, src)
        new_abs = os.path.join(ROOT, new_src)
        if os.path.exists(old_abs):
            move_plan.append((src, new_src))
        elif not os.path.exists(new_abs):
            print('[缺文件] 配置引用但磁盘不存在: %s' % src)

    # ---------- 输出计划 ----------
    print('=== 唯一启用音频 %d | 需迁移 %d | 显式写入 image %d 行 | 缺图 %d ==='
          % (len(src_cid), len(move_plan), len(img_map), len(missing_img)))
    for src, new_src in move_plan:
        print('[移动] %s -> %s' % (src, new_src))
    for src, img in missing_img:
        print('[缺图] %s (将写入 %s，客户端下载失败自动回退分类封面)' % (src, img))

    # ---------- JSON 文本改写（保格式） ----------
    src_re = re.compile(r'^(\s*)"src":\s*"([^"]+)"(\s*,?)\s*$')
    out_lines = []
    img_inserted = 0
    src_rewritten = 0
    for line in lines:
        m = src_re.match(line)
        if m:
            indent, src, comma = m.group(1), m.group(2), m.group(3)
            if src in src_map:
                # src 换成新路径；原行无逗号说明 src 是对象最后一个键，补逗号后插 image
                line = '%s"src": "%s"%s' % (indent, src_map[src], ',' if not comma else comma)
                src_rewritten += 1
                out_lines.append(line)
                img = img_map[src_map[src]]
                out_lines.append('%s"image": "%s"%s' % (indent, img, '' if not comma else ','))
                img_inserted += 1
                continue
            elif src in img_map:
                # 已在新路径（重复引用同文件的另一条曲目）：同样插入 image
                out_lines.append(line)
                img = img_map[src]
                out_lines.append('%s"image": "%s",' % (indent, img))
                img_inserted += 1
                continue
        out_lines.append(line)
    new_text = sep.join(out_lines)

    # ---------- 校验并输出 ----------
    try:
        parsed = json.loads(new_text)
        total_tracks = sum(len(c.get('playlist', [])) for c in parsed['categories'])
        with_img = sum(1 for c in parsed['categories'] for t in c.get('playlist', [])
                       if t.get('image'))
        print('JSON 校验通过：曲目 %d 条，其中带 image %d 条' % (total_tracks, with_img))
    except Exception as e:
        print('[中止] JSON 校验失败: %s' % e)
        return

    if not APPLY:
        print('（预演模式，未做任何改动；加 --apply 执行）')
        return

    # ---------- 执行 ----------
    for src, new_src in move_plan:
        dst = os.path.join(ROOT, new_src)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(os.path.join(ROOT, src), dst)
    with open(CFG, 'w', encoding='utf-8', newline='') as f:
        f.write(new_text)
    # 清理 audio 下的空目录
    for dirpath, dirs, files in os.walk(AUDIO_DIR, topdown=False):
        if not dirs and not files and dirpath != AUDIO_DIR:
            os.rmdir(dirpath)
    print('已执行：移动 %d 音频，src 改写 %d 行，image 写入 %d 行'
          % (len(move_plan), src_rewritten, img_inserted))


if __name__ == '__main__':
    main()

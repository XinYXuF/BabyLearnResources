# -*- coding: utf-8 -*-
"""
素材整理脚本：以 config/categories.json 为唯一基准，整理 audio/ 与 images/。
1) audio/：保留配置引用（enabled 分类与曲目）的音频并按配置路径归位；
   删除未被引用（含已下架分类/曲目）的音频；
2) images/：核对分类封面与曲目专属图（显式 image 或约定路径 images/{分类id}/{音频名}.jpg），
   删除已下架分类的遗留封面；设计源文件（clean_*.png、app_logo*）保留不动。
用法：python scripts/organize_assets.py          # 预演：只打印计划不落盘
     python scripts/organize_assets.py --apply   # 执行：删除 + 移动
文件均在 git 仓库内，误删可用 git restore 恢复。
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, 'config', 'categories.json')
AUDIO_DIR = os.path.join(ROOT, 'audio')
IMG_DIR = os.path.join(ROOT, 'images')
# 设计源文件白名单（不在配置引用中但必须保留）
IMG_KEEP = ('clean_', 'app_logo')

# 允许控制台输出 UTF-8（Windows 控制台默认 GBK，中文路径打印防乱码）
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv


def list_files(base_dir):
    """递归列出目录下全部文件的相对路径（正斜杠），目录不存在返回空表"""
    out = []
    if not os.path.isdir(base_dir):
        return out
    for dirpath, _dirs, files in os.walk(base_dir):
        for fn in files:
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            out.append(rel.replace('\\', '/'))
    return out


def main():
    with open(CFG, encoding='utf-8') as f:
        cfg = json.load(f)

    # ---------- 收集配置引用 ----------
    audio_refs = {}      # 配置音频路径 -> 分类 id
    track_img = {}       # 配置音频路径 -> 曲目图路径（显式 image 优先，否则约定路径）
    name_to_src = {}     # 音频文件名 -> 配置路径（同名冲突检测用）
    img_refs = set()     # 引用的图片路径（封面 + 曲目图 + 约定路径）
    for cat in cfg.get('categories', []):
        cid = cat.get('id', '')
        if not cat.get('enabled', True):
            continue  # 已下架分类：封面与曲目均不保留
        if cat.get('image'):
            img_refs.add(cat['image'])
        for t in cat.get('playlist', []):
            if not t.get('enabled', True):
                continue  # 已下架曲目不保留
            src = t.get('src', '')
            audio_refs[src] = cid
            name = os.path.basename(src)
            if name in name_to_src and name_to_src[name] != src:
                print('[冲突] 同名音频被多处引用: %s -> %s / %s' % (name, name_to_src[name], src))
            else:
                name_to_src.setdefault(name, src)
            # 曲目专属图：显式 image 优先，否则按约定路径 images/{分类id}/{音频名}.jpg
            img_path = t.get('image') or \
                'images/' + cid + '/' + os.path.splitext(name)[0] + '.jpg'
            track_img[src] = img_path
            img_refs.add(img_path)

    # ---------- audio 整理 ----------
    move_plan, del_plan, keep_audio = [], [], []
    for rel in list_files(AUDIO_DIR):
        if rel in audio_refs:
            keep_audio.append(rel)
            continue
        # 文件名命中某条配置引用：目标路径已有文件则为多余旧副本（删），
        # 目标缺失则为错位文件（移到配置路径归位）
        target = name_to_src.get(os.path.basename(rel))
        if target and not os.path.exists(os.path.join(ROOT, target)):
            move_plan.append((rel, target))
        else:
            del_plan.append(rel)

    # ---------- images 整理 ----------
    # tracks/ 平铺目录是批量生成的曲目图（{音频名}.jpg）：按配置映射的曲目图路径
    # （images/{分类id}/{音频名}.jpg）精确匹配后移动归位；未匹配的保留原地并报告
    # （运行时回退分类封面）。其余未引用图片 = 已下架分类的遗留封面，删除。
    move_img, img_del, img_keep = [], [], []
    unmatched_tracks = []
    tracks_dir = os.path.join(IMG_DIR, 'tracks')
    tracks = {}
    if os.path.isdir(tracks_dir):
        for fn in os.listdir(tracks_dir):
            stem, ext = os.path.splitext(fn)
            if ext.lower() == '.jpg':
                tracks[stem] = 'images/tracks/' + fn
    moved_targets = set()
    for src, img_path in track_img.items():
        stem = os.path.splitext(os.path.basename(src))[0]
        if stem in tracks and img_path not in moved_targets:
            moved_targets.add(img_path)
            move_img.append((tracks[stem], img_path))
    covered = {t for _s, t in move_img}
    unmatched_tracks = [p for p in tracks.values() if p not in
                        [m[0] for m in move_img]]
    for rel in list_files(IMG_DIR):
        if rel.startswith('images/tracks/'):
            continue  # tracks 目录文件已单独处理
        base = os.path.basename(rel)
        if rel in img_refs or base.startswith(IMG_KEEP):
            img_keep.append(rel)
        else:
            img_del.append(rel)

    # ---------- 输出计划 ----------
    print('=== audio 保留 %d | 移动 %d | 删除 %d ===' % (len(keep_audio), len(move_plan), len(del_plan)))
    # 高亮：启用引用所在目录下但配置未引用的音频（可能是旧版本文件或漏配，需人工确认）
    active_dirs = set(os.path.dirname(src) for src in audio_refs)
    flagged = [r for r in del_plan if os.path.dirname(r) in active_dirs]
    if flagged:
        print('--- 注意：以下属于启用分类但未被配置引用（请确认是否漏配） ---')
        for rel in flagged:
            print('[确认] %s' % rel)
    for rel, target in move_plan:
        print('[移动] %s -> %s' % (rel, target))
    for rel in del_plan:
        print('[删除] %s' % rel)
    print('=== images 保留 %d | 曲目图移动 %d | 删除 %d ===' % (len(img_keep), len(move_img), len(img_del)))
    for src, target in move_img:
        print('[图移动] %s -> %s' % (src, target))
    if unmatched_tracks:
        print('--- tracks/ 中未能与任何音频名匹配的图（保留原地） ---')
        for rel in unmatched_tracks:
            print('[未匹配] %s' % rel)
    for rel in img_del:
        print('[删除] %s' % rel)

    if not APPLY:
        print('（预演模式，未做任何改动；加 --apply 执行）')
        return

    # ---------- 执行 ----------
    for rel in del_plan:
        os.remove(os.path.join(ROOT, rel.split('  ')[0]))
    for src, target in move_plan:
        dst = os.path.join(ROOT, target)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(os.path.join(ROOT, src), dst)
    for src, target in move_img:
        dst = os.path.join(ROOT, target)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(os.path.join(ROOT, src), dst)
    for rel in img_del:
        os.remove(os.path.join(ROOT, rel))

    # 清理 audio 下的空目录
    for dirpath, dirs, files in os.walk(AUDIO_DIR, topdown=False):
        if not dirs and not files and dirpath != AUDIO_DIR:
            os.rmdir(dirpath)
    for dirpath, dirs, files in os.walk(IMG_DIR, topdown=False):
        if not dirs and not files and dirpath != IMG_DIR:
            os.rmdir(dirpath)

    print('已执行：删除 %d 音频 + %d 图片，移动 %d 音频' % (len(del_plan), len(img_del), len(move_plan)))


if __name__ == '__main__':
    main()

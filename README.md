# BabyLearnResources 资源仓库

「宝宝认知小乐园」微信小程序的**资源专用仓库**（只放资源，不放代码）。

## 目录结构

```
BabyLearnResources/
├── audio/                  # 音频资源（按分类分目录，433 个 mp3）
│   ├── erge/               # 儿歌
│   ├── gushi/              # 故事
│   ├── hudong/             # 互动
│   ├── english/            # 学英语
│   ├── number/             # 数字
│   ├── yaolanqu/           # 摇篮曲
│   ├── xiguan/             # 好习惯
│   ├── douxiao/            # 逗你笑
│   ├── lingsheng/          # 铃声
│   ├── shengxiao/          # 照相声效
│   ├── sanzijing/          # 三字经
│   ├── ziran/              # 自然声音
│   ├── renwu/              # 人物称谓
│   ├── jiaotong/           # 交通声音
│   ├── yueqi/              # 乐器声音
│   └── dongwu/             # 动物叫声
├── images/                 # 分类图片（16 张，文件名与分类 id 一致，如 erge.jpg）
└── config/
    └── categories.json     # 动态下发配置（分类名称、图片路径、播放列表）
```

## 资源访问地址（Gitee raw）

基地址：`https://gitee.com/envisionlove/BabyLearnResources/raw/master/`

- 音频示例：`https://gitee.com/envisionlove/BabyLearnResources/raw/master/audio/erge/star.mp3`
- 图片示例：`https://gitee.com/envisionlove/BabyLearnResources/raw/master/images/erge.jpg`
- 配置文件：`https://gitee.com/envisionlove/BabyLearnResources/raw/master/config/categories.json`

> 若仓库默认分支不是 `master`（如 `main`），请同步修改小程序端 `data/categories.js` 中的 `RES_BASE`。

## 如何新增资源（无需发版小程序）

1. 把新的 mp3 放入 `audio/` 下对应分类目录（新分类则新建目录，目录名用拼音/英文）；
2. 新分类需在 `images/` 放一张同名 jpg（如 `newcat.jpg`）；
3. 修改 `config/categories.json`：新增或追加 `categories` 条目（`image`、`src` 填相对本仓库根目录的路径）；
4. 提交并推送到 Gitee，小程序下次启动即自动生效（配置带本地缓存，断网时使用最近一次成功的配置）。

## 版权说明

全部选用公有领域内容（传统民谣 / 古典乐曲 / 古文经典 / 自然声 / 事实性认知内容），
音频文件须为自制录音（自己演唱演奏录制、AI 生成或 CC0 素材），不可使用他人商业唱片音源。

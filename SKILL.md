---
name: coze-podcast-generator
description: "把文章、笔记或任意文字变成一男一女双主播对话的播客音频，基于 Coze 语音播客插件。当用户想把文字转成播客、生成双主播播客、文字转播客、把文章做成播客、或文字生成播客音频时使用。它调用 Coze 工作流 run API，解析返回的音频地址，下载 MP3 到本地，按设计不含背景音乐。"
agent_created: true
---

# Coze 文字转双主播播客

把你写的文字（文章、笔记、Markdown）一键变成**一男一女双主播对话**的播客 MP3，基于 Coze 的「语音播客」插件生成。

本技能只生成正片单集——不含背景音乐、不含片头音乐、不含固定开场白/结束语（这些是有意排除的，详见下方「已知限制」）。

## 何时使用

- 用户说"把这段文字生成播客""文字转播客""生成双主播播客""把文章做成播客音频"，或丢来一篇文章 / Markdown 要求用播客方式朗读。
- 用户想用 Coze 把书面内容变成播客风格的音频。

## 前置准备（一次性）

1. 在 Coze 上搭建一个「语音播客」工作流，拿到三个值：`workflow_id`、`space_id`、个人访问令牌（`pat_...`）。详细步骤和坑见 `references/coze_setup.md`。
2. 用以下任意一种方式把凭证交给脚本：
   - 环境变量：`COZE_PAT`、`COZE_WORKFLOW_ID`、`COZE_SPACE_ID`
   - 脚本同目录放 `config.json`（复制 `config.json.example`）：
     ```json
     {"pat": "...", "workflow_id": "...", "space_id": "..."}
     ```
   - 不要把凭证硬编码进脚本——那是用户私有信息。

## 使用方法

运行自带脚本 `scripts/generate_podcast.py`：

```bash
# 直接给文字
python scripts/generate_podcast.py --text "今天咱们聊一聊……" --out episode.mp3

# 从文件 / 管道读取
cat article.md | python scripts/generate_podcast.py --out episode.mp3

# 交互式粘贴
python scripts/generate_podcast.py --out episode.mp3
```

脚本纯标准库实现（无需 `pip install`）。它会：

1. 从 `--text`、标准输入或交互输入读取文字。
2. 调用 `POST https://api.coze.cn/v1/workflow/run`，参数 `parameters.input = 文字`。
3. 从返回的 `data` JSON 中解析 `podcast_url`。
4. 把 MP3 下载到 `--out`（默认 `podcast.mp3`）。

## 已知限制（重要）

- Coze 插件只支持**长文 → 整集**。喂给它一段固定的开场白 / 结束语短文，它会把那当成话题自己扩写成跑题整集。因此本技能刻意只生成正片，不要试图往前后硬塞固定开场 / 结尾。
- `input_text` 单次上限约 15000 字。
- 音频直链约 3 天过期——务必下载保存到本地（脚本已自动做）。
- 按设计无 BGM。要加背景音乐请用 ffmpeg 另行混音。
- 生成较慢，单次最长可能等约 10 分钟，请耐心等待。

## 参考

- `references/coze_setup.md` —— 如何搭建 Coze 工作流、获取 PAT、以及排错（空数据、"input content can not be empty" 等）。

# Coze 文字转双主播播客

![封面](cover.png)

把你写的文章、笔记、文字稿，一键变成**一男一女双主播对谈**的播客 MP3。

> 本技能基于 [Coze](https://www.coze.cn) 的「语音播客」插件，由 AI 自动把正文改写成自然流畅的双人对话，无需你手动分角色。

---

## ✨ 它能做什么

- 输入：一段文字（文章 / Markdown / 笔记），最长约 15000 字
- 输出：一个 MP3 文件，一男一女双主播自然对谈的完整单集
- **不含 BGM、不含片头音乐、不含固定开场/结束语**（纯净版，按需自行后期处理）

---

## 📦 怎么安装

| 方式 | 适合谁 | 怎么做 |
|---|---|---|
| **SkillHub 一键装**（推荐） | 只想用、不想碰代码 | 打开 SkillHub → 搜索 **`coze-podcast-generator`** → 安装即可，无需 clone |
| **GitHub clone** | 想看源码 / 二次开发 | `git clone https://github.com/jondeng11-creator/coze-podcast-generator.git` |

> SkillHub 安装后，AI 助手会自动读取 `SKILL.md` 指令，你直接对它说"把这篇文章做成播客"就行。

---

## 📋 使用前准备（一次性）

使用本技能**必须**先在 Coze 上搭好一个「语音播客」工作流，并拿到 3 个凭证：

| 凭证 | 说明 | 获取位置 |
|---|---|---|
| `workflow_id` | 工作流 ID | 工作流 URL 中 `workflow_id=` 后的数字 |
| `space_id` | 空间 ID | 工作流 URL 中 `space_id=` 后的数字 |
| `pat_...` | 个人访问令牌 | Coze 网页 → 右上角头像 → API 管理 → 创建 PAT |

> ⚠️ **搭建工作流的关键坑**（详见 `references/coze_setup.md`）：
> 1. 工作流**不能包含「输出」节点**，否则 API 返回空数据；请用「结束」节点返回 `podcast_url`。
> 2. 插件的 `input_text` 必须连接到「开始」节点的输入。
> 3. **只支持长文 → 整集**。不要喂短文当"开场白/结束语"，插件会把短文当话题自己扩写成跑题整集。

---

## 🔧 配置凭证（二选一）

### 方式 A：环境变量（推荐）

```bash
export COZE_PAT="pat_你的令牌"
export COZE_WORKFLOW_ID="你的工作流ID"
export COZE_SPACE_ID="你的空间ID"
```

### 方式 B：config.json

复制 `config.json.example` 为 `config.json`，填入你的凭证：

```json
{
  "pat": "pat_你的令牌",
  "workflow_id": "你的工作流ID",
  "space_id": "你的空间ID"
}
```

> 🔒 凭证是私有的，**不要写进脚本或提交到公开仓库**。

---

## 🚀 怎么用

脚本 `scripts/generate_podcast.py` 是纯 Python 标准库实现，**无需 `pip install`**。

```bash
# 1) 直接给文字
python scripts/generate_podcast.py --text "今天咱们聊一聊……" --out episode.mp3

# 2) 从文件 / 管道读取
cat article.md | python scripts/generate_podcast.py --out episode.mp3

# 3) 交互式粘贴（运行时粘贴文字，回车生成）
python scripts/generate_podcast.py --out episode.mp3
```

生成较慢，**单集可能要 1~10 分钟**，请耐心等待。生成的 MP3 会自动下载保存到你指定的 `--out` 路径。

---

## ❓ 常见问题

**Q：报错 "工作流返回为空（usage 全 0）"？**
A：你的 Coze 工作流里含有「输出」节点，API 禁止。删掉「输出」节点、改用「结束」节点返回 `podcast_url`，重新发布工作流即可。

**Q：报错 "input content can not be empty"？**
A：工作流里 genPodcastURL 的 `input_text` 没有连到「开始」节点。把它引用改成 `开始.input` 再发布。

**Q：生成的播客和我想的主题不一致？**
A：Coze 插件会基于你的正文自由发挥对谈内容。给它一篇结构清晰、主题明确的文章，效果更好。

**Q：音频链接打不开？**
A：Coze 返回的音频直链约 **3 天后过期**，技能已自动下载到本地，直接用本地 MP3 即可。

**Q：能加 BGM / 片头吗？**
A：本技能定位"纯净版"，不含 BGM。如需，请用 ffmpeg 自行混音。

---

## 📁 文件结构

```
coze-podcast-generator/
├── SKILL.md                 # 技能指令（给 AI 看）
├── README.md                # 本文件（给你看）
├── config.json.example      # 凭证模板
├── scripts/
│   └── generate_podcast.py  # 核心脚本
└── references/
    └── coze_setup.md        # Coze 工作流搭建详细教程
```

---

## ⚠️ 已知限制

- **必须自备 Coze 账号与工作流**：本技能是 Coze 语音播客插件 API 的封装，不自带语音合成能力。没有 Coze 账号、或未搭建好对应工作流的用户无法使用（需自行在 Coze 创建 PAT、工作流 ID、空间 ID）。
- **无 BGM / 无片头 / 无固定开场结束语**：本版为纯净输出，仅生成双主播对谈单集。如需背景音乐或片头，请用 ffmpeg 自行混音。
- **短文会被当成话题扩写**：Coze 插件只支持「长文 → 整集」。不要喂 3 行短文当"开场白/结束语"，否则插件会把短文当成主题自行扩写成跑题整集。
- **音频直链约 3 天过期**：技能已自动把 MP3 下载到本地，请直接使用本地文件。
- **生成较慢**：单集通常需 1~10 分钟，请耐心等待。

---

## 📝 更新日志

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-08-26 | 首发：文字 → 双主播对谈 MP3（无 BGM 纯净版）；含 SKILL.md / README / 脚本 / Coze 搭建教程；支持环境变量与 config.json 两种凭证方式 |

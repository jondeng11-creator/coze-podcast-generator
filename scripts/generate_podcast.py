#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coze 文字转双主播播客（纯净版：无 BGM / 无片头 / 无固定开场结束语）

把一段文字稿（文章、笔记、脚本）交给 Coze 语音播客工作流，
生成一男一女双主播对谈的 MP3，并下载到本地。

前置条件（详见 references/coze_setup.md）：
  1. 在 Coze 搭好「语音播客」工作流，并发布拿到 workflow_id / space_id
  2. 准备一个 Coze 个人访问令牌（PAT，以 pat_ 开头）
  3. 提供凭证（二选一）：
     - 环境变量：COZE_PAT / COZE_WORKFLOW_ID / COZE_SPACE_ID
     - 同目录或上级目录的 config.json：
         {"pat": "...", "workflow_id": "...", "space_id": "..."}

用法：
  python generate_podcast.py --text "你的文字稿" --out episode.mp3
  cat article.md | python generate_podcast.py --out episode.mp3
  python generate_podcast.py            # 交互粘贴

依赖：仅 Python 标准库（无需 pip install）。
"""

import urllib.request
import json
import os
import sys
import time
import argparse


def load_config():
    """凭证优先级：环境变量 > 同目录 config.json > 上级目录 config.json。"""
    cfg = {}
    env = {
        "pat": os.environ.get("COZE_PAT"),
        "workflow_id": os.environ.get("COZE_WORKFLOW_ID"),
        "space_id": os.environ.get("COZE_SPACE_ID"),
    }
    if env["pat"] and env["workflow_id"]:
        return env

    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "config.json"),
        os.path.join(here, "..", "config.json"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            try:
                with open(c, encoding="utf-8") as f:
                    cj = json.load(f)
                cfg["pat"] = cj.get("pat")
                cfg["workflow_id"] = cj.get("workflow_id")
                cfg["space_id"] = cj.get("space_id")
                break
            except Exception:
                continue
    return cfg


def generate(text, cfg):
    """调用 Coze 工作流 run API，返回 {'url': MP3直链, 'dialog': 对话稿}。"""
    url = "https://api.coze.cn/v1/workflow/run"
    payload = {
        "workflow_id": cfg["workflow_id"],
        "parameters": {"input": text},
    }
    if cfg.get("space_id"):
        payload["space_id"] = cfg["space_id"]

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {cfg['pat']}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=600) as resp:
        j = json.loads(resp.read().decode("utf-8"))

    if j.get("code") != 0:
        raise RuntimeError(f"Coze API 报错: {j.get('msg')} (code={j.get('code')})")

    data_str = j.get("data") or ""
    usage = j.get("usage") or {}
    if not data_str and usage.get("input_count", 0) == 0 and usage.get("token_count", 0) == 0:
        raise RuntimeError(
            "工作流返回为空（usage 全 0）。最常见原因：工作流里包含『输出』节点，"
            "Coze 的 API 禁止使用输出节点。请删除『输出』节点、改用『结束』节点返回 "
            "podcast_url，并重新发布，再试。详见 references/coze_setup.md")

    try:
        data = json.loads(data_str)
    except Exception:
        data = {}

    link = None
    dialog = None
    if isinstance(data, dict):
        link = data.get("podcast_url") or data.get("output")
        dialog = data.get("text") or data.get("dialog")
    if not link:
        import re
        m = re.search(r'https?://[^\s"\\]+\.mp3', data_str)
        if m:
            link = m.group(0)
    if not link:
        raise RuntimeError(f"没找到音频链接，原始输出前 500 字：{data_str[:500]}")
    return {"url": link, "dialog": dialog}


def download(link, path):
    req = urllib.request.Request(link)
    with urllib.request.urlopen(req, timeout=300) as resp:
        with open(path, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)


def main():
    ap = argparse.ArgumentParser(description="Coze 文字转双主播播客（无 BGM 纯净版）")
    ap.add_argument("--text", help="文字稿内容（缺省则从 stdin 或交互输入读取）")
    ap.add_argument("--out", default="podcast.mp3", help="输出 mp3 路径（默认 podcast.mp3）")
    args = ap.parse_args()

    cfg = load_config()
    if not cfg.get("pat") or not cfg.get("workflow_id"):
        print("❌ 未找到 Coze 凭证。请设置环境变量 COZE_PAT / COZE_WORKFLOW_ID / "
              "COZE_SPACE_ID，或在脚本同目录创建 config.json。详见 references/coze_setup.md。")
        sys.exit(1)

    # 取文字稿：--text > stdin > 交互输入
    text = (args.text or "").strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        text = input("粘贴播客文字稿（输入完按回车）：\n").strip()
    if not text:
        print("文字稿为空，已退出。")
        sys.exit(1)

    print("🎙️ 正在生成播客，请稍候（最长约 10 分钟）...")
    t0 = time.time()
    res = generate(text, cfg)

    out_path = args.out
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    download(res["url"], out_path)

    print(f"✅ 完成（用时 {int(time.time() - t0)} 秒）")
    print(f"   音频直链：{res['url']}")
    print(f"   本地文件：{os.path.abspath(out_path)}")
    if res["dialog"]:
        print(f"   对话稿前 200 字：{res['dialog'][:200]}")


if __name__ == "__main__":
    main()

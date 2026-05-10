# English Coach

Hermes 的英语学习 skill。

它可以帮你：

- 中英互译
- 查单词、短语
- 练发音
- 改语法
- 润色英文

## 安装 / 更新

把这句发给 Hermes：

```text
请帮我安装/更新这个 skill：https://github.com/BlueBirdBack/english-coach
```

## 怎么用

在消息开头加一个前缀：

- `en: 你好` → 翻成自然英文
- `zh: Hello` → 翻成简体中文
- `word: agent` → 单词卡：意思、音标、例句、音频/图片/视频
- `words: paste a paragraph` → 从一段英文里挑重点词
- `say: I worked it out` → 发音练习
- `fix: I goed to store` → 小幅纠错
- `polish: Thanks for your help` → 改得更自然

前缀优先。比如 `fix: ...` 一定会当作英文纠错处理。

## 媒体

`word:` 会先给文字卡。

如果工具可用，Hermes 还会生成：

- 音频
- 图片
- 短视频

没有图片生成也能用；只会少图片和视频。

## 图片生成（可选）

如果图片生成已经能用，不需要改设置。

如果还没配置，并且你想用 Codex 生成图片：

```bash
hermes tools enable image_gen
hermes login --provider openai-codex
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-low
```

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

推荐用 `coach:` 作为主命令。它会根据内容自动判断模式：

- `coach: plausible` → 单词 / 短语卡
- `coach: can we ignore it in p0` → 纠错 / 润色
- `coach: best way for Telegram: good to see the agent is agent ;-)` → 给最佳母语感表达，并保留玩笑 / 语气
- `coach: 我想确认一下这个方案是否合理` → 翻成自然英文
- `po: Thanks for your help` → 只做纠错 / 润色
- `en: 你好` → 翻成自然英文
- `zh: Hello` → 翻成简体中文
- `say: I worked it out` → 发音练习

旧前缀仍可用：`polish:`、`word:`、`words:`、`fix:`。

不建议继续用 `polish:`。它看起来像普通任务指令，已经不止一次让 agent 误以为要去完善 MD 文档、改代码或执行其他任务。需要润色/纠错时，优先用 `coach:`；只想要短命令时，用 `po:`。

不建议为了 “best wording / native-sounding / tone” 再加更多前缀。继续用 `coach:`，在内容里直接说清楚目标，比如 “best way for Telegram”、“make it native but playful”、“keep the meme”。

## 前缀优先

如果一句话以 `coach:`、`po:`、`polish:`、`fix:`、`word:`、`say:`、`en:`、`zh:` 等前缀开头，English Coach 会把冒号后面的内容当作学习材料处理，不会把它当成真正的任务来执行。

```text
coach: make the md better so that i can follow it effortlessly when implementing p0 (cli/etl)
```

这会返回润色后的英文，不会编辑 markdown 文件。想让 Hermes 真正执行任务时，不要加 English Coach 前缀。

## 媒体

`word:` / `coach: 单词` 会先给文字卡。

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

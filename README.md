# English Coach

**English Coach** 是一个 Hermes 英语学习 skill，用来做翻译、单词卡、发音练习、纠错、润色，以及可选的 TTS 音频和单词图片。

**作者：Rac 🦝**

## 能做什么

- `en:` 中文 → 自然英文
- `zh:` 英文 → 中文
- `word:` 单词 / 短语卡片
- `words:` 从一段英文里提取值得学的词
- `say:` 发音、重音、跟读
- `fix:` 语法 + 自然度纠错
- `polish:` 按语气润色

也兼容旧触发词：`lv:`、`level:`、`vocab:`、`pronounce:`。

## 安装

把这个仓库克隆到 Hermes skills 目录：

```bash
git clone <repo-url> ~/.hermes/skills/openclaw-imports/english-coach
```

然后在 Hermes 里加载：

```text
english-coach
```

## 快速例子

```text
word: mosquito
words: paste an English paragraph here
say: how are you doing?
fix: I goed to store
en: 我想确认一下这个方案是否合理
zh: That sounds like a plausible explanation.
polish: Thanks for your help
```

## 示例：`word: mosquito`

```text
Word/Phrase: mosquito
CEFR: B1
IPA: /məˈskiː.toʊ/ (US)
Part of speech: noun
Meaning: a small flying insect that bites people and animals
中文：蚊子
Simpler ladder: bug → insect → mosquito
Collocations: mosquito bite · mosquito net · mosquito repellent
Examples:
1. A1: A bug bit me.
2. A2: A mosquito bit me.
3. B1: There are mosquitoes near the water.
```

### MP3 发音

[word-mosquito.mp3](assets/audio/word-mosquito.mp3)

### 单词图片

![word: mosquito](assets/images/word-mosquito.png)

## 文件结构

```text
SKILL.md
references/cefr.md
references/EFLLex_NLP4J
assets/audio/word-mosquito.mp3
assets/images/word-mosquito.png
```

## 设计原则

- 先给文本结果。
- 音频和图片是可选增强，不是硬依赖。
- 私密内容、账号密码、法律/医疗文本、个人数据默认只走文本，不发给 TTS 或图片工具。
- 单词图片用于帮助记忆，优先画场景，不做文字很多的卡片。

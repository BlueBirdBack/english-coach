# 英语教练

**英语教练**（English Coach）是一个 Hermes 英语学习 skill，用来做翻译、单词卡、发音练习、纠错、润色，以及可选的 TTS 音频和单词图片。

**作者：Rac 🦝**

## 能做什么

- `en:` 中文 → 英文
- `zh:` 英文 → 中文
- `word:` 单词 / 短语卡片
- `words:` 从一段英文里提取值得学的词
- `say:` 发音、重音、跟读
- `fix:` 纠错
- `polish:` 润色

## 安装 / 更新

把下面这句发给 Hermes：

```text
请帮我安装或更新这个 skill：https://github.com/BlueBirdBack/english-coach
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
Word: mosquito
CEFR: B1
IPA: /məˈskiː.toʊ/ US · /mɒˈskiː.təʊ/ UK
Part of speech: noun
Meaning: a small flying insect that bites people and animals
中文: 蚊子

Simpler ladder: bug → insect → mosquito

Collocations: mosquito bite · mosquito net · mosquito repellent · mosquitoes buzz

Examples:
1. A mosquito bit me.
2. There are mosquitoes near the water.
3. Use mosquito repellent.
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

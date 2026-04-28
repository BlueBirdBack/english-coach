# 英语教练（English Coach）

[Hermes](https://github.com/nousresearch/hermes-agent) 里的英语学习教练。适合想学英语的你。

**作者：Rac 🦝**

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

### 听发音

[word-mosquito.mp3](assets/audio/word-mosquito.mp3)

### 看图片记单词

![word: mosquito](assets/images/word-mosquito.png)

## 安装 / 更新

把下面这句发给 Hermes：

```text
请帮我安装或更新这个 skill：https://github.com/BlueBirdBack/english-coach
```

## 图片生成

English Coach 做单词卡时会优先返回文字；如果 Hermes 已启用图片生成，会再生成「看图记单词」图片。

不用图片生成也能正常使用：翻译、查词、纠错、润色、发音和音频都不依赖图片生成。未启用图片生成时，English Coach 会给一段可复用的图片 prompt。

## 怎么用

| 你输入 | 它会做什么 |
|---|---|
| `en: 我想确认一下这个方案是否合理` | 中文 → 英文 |
| `zh: That sounds plausible.` | 英文 → 中文 |
| `word: mosquito` | 单词卡：等级、发音、中文、例句 |
| `word: mosquito repellent` | 短语卡 |
| `words: paste an English paragraph here` | 从一段英文里挑重点词 |
| `say: how are you doing?` | 发音、重音、跟读 |
| `fix: I goed to store` | 小改进式纠错：先给 **Little better** |
| `polish: Thanks for your help` | 先 Little better，再给更自然版本 |

## 显式前缀优先

如果一句话以 `polish:`、`fix:`、`word:`、`say:`、`en:`、`zh:` 等前缀开头，English Coach 会把冒号后面的内容当作学习材料处理，不会把它当成技术问题来回答。

```text
polish: what's the current config's max_turns and approvals.mode
```

这会触发润色，而不是去查询 Hermes 配置。想问技术问题时，不要加 English Coach 前缀。

## `fix:` / `polish:` 的 Little better

**Little better** = 小改原句，让它更正确、更清楚，但尽量保留用户自己的表达。

- `fix:` 默认先给 **Little better**：修明显错误，不急着改成完美母语句。
- `polish:` 先给 **Little better**，再给 **More natural** / **Best version**。
- 目的：让学习者更容易看懂「改了哪里」，从小变化里学会表达。

```text
fix: I call it "little better", changing theoriginal a little so that users can much easier to grasp.
```

```text
Little better:
I call it "a little better": changing the original a little so users can grasp it much more easily.

More natural:
I call it “a little better”: a small change to the original that makes it much easier for learners to understand.
```

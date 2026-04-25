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

## 可选：开启 `image_gen` 图片生成

`image_gen` 是 Hermes 的图片生成工具集，不是这个 skill 自带的模型或 API key。English Coach 只在做单词卡时用它生成「看图记单词」图片。

不用 `image_gen` 也能正常使用：翻译、查词、纠错、润色、发音和 MP3 都不依赖图片生成。

`image_gen` 的行为：

- 已启用并配置好：Hermes 会调用 `image_generate` 生成单词配图。
- 未启用或未配置好：English Coach 仍会返回文字结果和音频，并给一段可复用的图片 prompt。
- 报 `FAL_KEY environment variable not set`：说明 Hermes 还在走默认 FAL 图片后端，但当前机器没有配置 FAL key。

推荐改用 Codex/ChatGPT OAuth 的 GPT Image 2，不需要 `OPENAI_API_KEY`。

想让 Hermes 帮你自动配置，把这句发给 Hermes：

```text
请帮我自动配置 image_gen：启用 image_gen，优先使用 openai-codex + gpt-image-2-medium；如果需要登录 Codex，请引导我完成 `hermes login --provider openai-codex`；配置后告诉我是否要 `/reset` 或 `/restart`。
```

手动配置也可以：

```bash
hermes tools enable image_gen
hermes auth status openai-codex
hermes login --provider openai-codex
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
```

然后开启新会话；如果是在 Telegram / Discord gateway 里用 Hermes，执行 `/restart`。

如果你想继续用 FAL，也可以设置 `FAL_KEY`。

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

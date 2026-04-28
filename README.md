# 英语教练（English Coach）

[Hermes](https://github.com/nousresearch/hermes-agent) 里的英语学习教练。适合想学英语的你。

**作者：Rac 🦝**

## 示例 1：`word: agent`

```text
Word/Phrase: agent
CEFR: B1–B2
IPA: /ˈeɪ.dʒənt/
Part of speech: noun
Meaning: a person or system that acts for someone, or something that causes change
中文: 代理人；智能体；作用因素
Simpler ladder: person → helper → representative → agent
Collocations: travel agent · AI agent · secret agent · cleaning agent
Examples:
1. The travel agent booked our tickets.
2. An AI agent can complete tasks for a user.
3. Soap is a cleaning agent.
```

### 听发音

[word-agent.mp3](assets/audio/word-agent.mp3)

### 看图片记单词

![word: agent](assets/images/word-agent.png)

## 示例 2：`word: harness`

```text
Word/Phrase: harness
CEFR: B2 (estimated)
IPA: /ˈhɑːr.nəs/ US · /ˈhɑː.nəs/ UK
Part of speech: noun / verb
Meaning: equipment that holds someone safely; or to control and use something powerful
中文: 安全带；挽具；利用
Simpler ladder: hold → use → control → harness
Collocations: safety harness · test harness · harness energy · harness the power of AI
Examples:
1. The worker wore a safety harness.
2. We use a test harness to run the checks automatically.
3. The company wants to harness AI to improve customer support.
```

### 听发音

[word-harness.mp3](assets/audio/word-harness.mp3)

### 看图片记单词

![word: harness](assets/images/word-harness.png)

## 安装

把下面这句发给 Hermes：

```text
请帮我安装这个 skill：https://github.com/BlueBirdBack/english-coach
```

## 更新

把下面这句发给 Hermes：

```text
请帮我更新这个 skill：https://github.com/BlueBirdBack/english-coach
```

## Python / uv 设置

这个 skill 带了一个已经生成好的 EFLLex SQLite 词表缓存，普通使用不需要自己跑 Python。

只有在你想重新生成 `references/efllex.sqlite` 或运行测试时，才需要 Python 和 `uv`。

### 安装 uv

macOS / Linux：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

检查是否安装成功：

```bash
uv --version
uv python --version
```

如果没有 Python，安装一个 3.11+ 版本：

```bash
uv python install 3.11
```

### 重新生成 EFLLex SQLite（可选）

```bash
uv run python scripts/build_efllex_cache.py references/EFLLex_NLP4J references/efllex.sqlite
```

### 运行测试（可选）

```bash
uv run pytest -q
```

如果没有安装 `pytest`：

```bash
uv add --dev pytest
uv run pytest -q
```

## 图片生成 image_gen 设置

不用图片生成也能正常使用：翻译、查词、纠错、润色、发音和音频都不依赖图片生成。

如果 Hermes 已启用 `image_gen`，English Coach 做 `word:` 单词卡时会自动生成「看图记单词」图片。未启用时，它会给一段可复用的图片 prompt。

### 推荐设置：Codex / ChatGPT OAuth

把下面这句发给 Hermes：

```text
请帮我自动配置 image_gen：启用 image_gen，优先使用 openai-codex + gpt-image-2-medium；如果需要登录 Codex，请引导我完成 `hermes login --provider openai-codex`；配置后提醒我开启新会话或执行 `/restart`。
```

也可以手动执行：

```bash
hermes tools enable image_gen
hermes login --provider openai-codex
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
```

然后开启新会话；如果是在 Telegram / Discord gateway 里用 Hermes，执行 `/restart`。

### 如果看到 FAL_KEY 错误

这通常表示 Hermes 还在使用默认 FAL 图片后端，但当前机器没有配置 FAL key。

两种选择：

1. 按上面的步骤切换到 `openai-codex + gpt-image-2-medium`。
2. 如果你想继续用 FAL，就配置 `FAL_KEY`。

## 怎么用

| 你输入 | 它会做什么 |
|---|---|
| `en: 我想确认一下这个方案是否合理` | 中文 → 英文 |
| `zh: That sounds plausible.` | 英文 → 中文 |
| `word: agent` | 单词卡：等级、发音、中文、例句、音频、图片 |
| `word: harness` | 单词卡：支持名词/动词、多义项 |
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

---
name: writing-great-skills
description: 编写和编辑优秀 skills 的参考：让技能可预测的词汇和原则。
disable-model-invocation: true
---

Skill 的存在，是为了从随机系统中拧出 determinism。**Predictability**——agent 每次采取相同的 _process_，而不是产出相同的 output——是根本美德；下面所有杠杆都服务于它。

**粗体术语** 在 [`GLOSSARY.md`](GLOSSARY.md) 中定义；需要完整含义时查那里。

## Invocation

两种选择，成本不同：

- **Model-invoked** skill 保留 **description**，所以 agent 可以自主触发它，其他 skills 也能触达它（用户仍可手动输入名称）。它会带来 **context load**：description 每轮都在 context window 中。机制：省略 `disable-model-invocation`，并写 model-facing description，带丰富触发措辞（"Use when the user wants…"、"mentions…"）。
- **User-invoked** skill 把 description 从 agent 触达范围中拿掉：只有用户输入名称时才能调用，其他 skill 也不能调用它。零 context load，但会花 **cognitive load**：_用户_ 是那个必须记得它存在的 index。机制：设置 `disable-model-invocation: true`；`description` 变成人类看到的一行摘要，不放触发列表。

只有当 agent 必须自行找到该 skill，或另一个 skill 必须调用它时，才选择 model-invocation。如果它只会被手动触发，就做成 user-invoked，不付 context load。

当 user-invoked skills 多到用户记不住时，堆积的 cognitive load 由一个 **router skill** 来治疗：一个 user-invoked skill，负责命名其他 user-invoked skills 以及何时使用它们。

## Writing the description

Model-invoked **description** 做两件事：说明 skill 是什么，并列出应触发它的 **branches**。每个词都会增加 **context load**，所以 description 比正文更需要修剪：

- **把 skill 的 leading word 放前面**——description 是它做 invocation 工作的地方。
- **每个 branch 一个 trigger。** 同义词如果只是重命名单一 branch，就是 **duplication**——"build features using TDD … asks for test-first development" 是同一个 branch 写了两次。合并它们；只保留真正不同的 branches。
- **删掉正文已有的 identity。** Description 只保留 triggers，以及必要的 "when another skill needs…" reach clause。

## Information hierarchy

Skill 由两类内容构成：**steps** 与 **reference**，它们自由混合：skill 可以全是 steps、全是 reference，或两者都有。核心决策是用哪类内容，以及每块内容放在 **information hierarchy** 的哪一层——一个按 agent 需要材料的即时程度排序的 ladder：

1. **In-skill step** - `SKILL.md` 中的有序动作，是 primary tier：agent 按顺序做什么。每个 step 以 **completion criterion** 结束，即告诉 agent 工作完成的条件。让它 _可检查_（agent 能分辨 done 与 not-done 吗？），必要时 _exhaustive_（"每个修改过的 model 都被考虑到"，而不是 "产出一个变更列表"）——模糊的 criterion 会诱发 **premature completion**。
2. **In-skill reference** - `SKILL.md` 中的定义、规则或事实，按需查阅。通常是合法的 flat peer-set（一个 review 的所有规则在一个 rung 上）——这不是坏味道。_本 skill 全是 reference。_
3. **External reference** - 从 `SKILL.md` 推到独立文件中，经 **context pointer** 触达，只在 pointer 触发时加载。（涵盖 _disclosed_ reference——像 `GLOSSARY.md` 这样的 sibling 文件，仍是 skill 的一部分——到完全位于 skill system 之外、任何 skill 都能指向的 **external reference**。）

强 completion criterion 会驱动充分 **legwork**——agent 在工作中做的挖掘——无论 skill 是否有 steps，因为 "每条规则都被应用" 约束 flat reference，正如 "每个 step 都完成" 约束 sequence。

把太少内容下放会让顶层膨胀；把太多内容下放会隐藏 agent 实际需要的材料。那种张力就是整个决策。

**Progressive disclosure** 是沿 ladder 下移——移出 `SKILL.md`、进入 linked 文件——让顶层保持清晰。Mechanics：skill folder 中的 linked `.md` 文件，用内容命名（本 skill 把完整定义 disclose 到 `GLOSSARY.md`）。有些 skills 以不止一种方式使用，每种不同的方式都是一个 **branch**——不同 runs 沿着不同路径穿过 skill。Branching 是最干净的 disclosure 测试：内联每个 branch 都需要的内容，把只有部分 branches 触达的内容放到 pointer 后面。**Context pointer** 的 _措辞_，而不是目标文件，决定 agent 何时以及多可靠地触达材料。

Ladder 决定一块内容 _下移多远_，**co-location** 决定一旦到了那里 _什么在它旁边_：把一个概念的定义、规则和 caveats 放在同一 heading 下，而不是散落各处，这样读一部分时它的邻居也随之而来。

## When to split

**Granularity** 是 skill 切分粒度，每次切分都会花两种 load 之一，所以只有切分有收益时才切。两种切法：

- **By invocation** - 当你有一个独立 **leading word** 应自主触发，或另一个 skill 必须触达它时，拆出 **model-invoked** skill。你要为新的始终加载的 **description** 支付 **context load**，所以独立触达必须值得。
- **By sequence** - 当后续 **steps**（一个 step 的 **post-completion steps**）会诱使 agent 急着结束前一步（**premature completion**）时，拆分一连串 **steps**。把它们藏在视野之外，鼓励 agent 在当前任务上做更多 **legwork**。

## Pruning

让每个 meaning 都有 **single source of truth**：一个权威位置，这样改变 behavior 就是一处的编辑。

逐行检查 **relevance**：它是否仍支撑 skill 的工作？

然后逐句寻找 **no-ops**，不只是逐行：把每个句子单独做 no-op test；失败时删除整句，而不是只修剪词。要激进——多数失败 prose 应删除，不应重写。

## Leading words

**Leading word** 是一个已经存在于模型预训练中的紧凑概念，agent 会在运行 skill 时用它思考（例如 _lesson_、_fog of war_、_tracer bullets_）。它在文本中反复出现（但不一定——一个强的 leading word 可能只需要一次），累积 distributed definition，并通过招募模型已持有的 priors，用最少 tokens 锚定一整片 behavior。

它两次服务 predictability。正文中它锚定 _execution_：agent 每次遇到该词都触发同类行为。Description 中它锚定 _invocation_：当同一个词存在于你的 prompts、docs 和 codebase 中，agent 会把那份 shared language 连到该 skill，更可靠地触发它。

寻找机会把 skills 重构为使用 leading words。三处重复展开的 triad（**duplication**）、花一句话绕一个概念的 description——每一段都是恳求 **collapse** 成单个 token 的文字。例如：

- "fast, deterministic, low-overhead" -> _tight_——一个品质在一个阶段中被反复陈述——收进一个预训练词（一个 _tight_ loop）。
- "a loop you believe in" -> _red_——把一个模糊的 gate 转换成一个二元可观察状态（loop 在 bug 上变 _red_，或者不变）。

你同时赢得更少 tokens，_以及_ 一个更尖锐的 hook 让 agent 挂起它的思考。假设每个 skill 都携带着 leading words 可以退役的重复陈述——去找它们。

## Failure modes

用这些来诊断用户可能在使用 skill 时遇到的问题。

- **Premature completion** - 当前 step 尚未真正完成就结束，注意力滑向 _being done_。防御顺序：先 sharpen completion criterion（廉价、局部）；只有当它不可避免地模糊 _且_ 你观察到 rush 时，才通过拆分隐藏 post-completion steps（sequence cut）。
- **Duplication** - 同一 meaning 出现在多个地方。它提高维护成本、浪费 tokens，并夸大该 meaning 在 ladder 上的 prominence 超过其真实等级。
- **Sediment** - 因为添加看似安全、删除看似有风险而沉积的 stale layers。任何缺少 pruning discipline 的 skill 的默认命运。
- **Sprawl** - skill 太长，即使每一行都 live 且 unique。伤害 readability 和 maintainability，浪费 tokens。治疗方式是 ladder：把 **reference** disclose 到 pointers 后面，按 **branch** 或 sequence 拆分，让每条路径只携带它需要的。
- **No-op** - 模型默认就会做的一行，所以你付 load 却什么也没说。测试：它是否改变默认 behavior？弱 leading word（如 _be thorough_，当 agent 已经大致 thorough）就是 no-op；修法是换更强的词（如 _relentless_），而不是换一种 technique。
- **Negation** - 用禁止来引导会适得其反：_don't think of an elephant_ 点名了 elephant，让它更容易浮现，而不是更难。应 prompt **positive**——直接说明目标 behavior，让被禁止的行为从不被说出；只有无法正向表达的 hard guardrail 才保留 prohibition，即使如此也要配上应该怎么做。

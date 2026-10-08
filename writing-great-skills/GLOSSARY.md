# Glossary — Building Great Skills

这是关于什么让一个 skill 优秀的 domain model。Skill 的存在，是为了从随机系统中拧出 determinism；根本美德是 **Predictability**，下面每个 term 都是作用于它的杠杆。它是 [`writing-great-skills`](SKILL.md) 的 disclosed reference。

Terms 按轴分组：**Invocation**（skill 如何被触达）、**Information Hierarchy**（内容如何安排）、**Steering**（如何塑造 agent 运行时行为）、**Pruning**（如何保持精瘦）。每个 **failure mode** 都放在治疗它的杠杆旁，并标记为 _failure mode_。

任何定义中的 **粗体术语** 本身都在本 glossary 中定义；按其 heading 查找。

## Predictability

Skill 让 agent 每次以同样 _方式_ 行动的程度：同样的 process，不是同样的 output（brainstorming skill 应 _predictably_ diverge；tokens 会变，behavior 不变）。这是其他术语服务的根本美德；cost 和 maintainability 是它的症状，不是 rival。

_Avoid_: consistency, reliability, robustness, output-determinism

## Invocation

Skill 如何被触达，以及你为选择支付的两种 load。

### Model-Invoked

保留 **description** field 的 skill，所以 agent 能看到并自主触发它——而人类仍能输入名称，因此 model-invocation 总是 _包含_ user reach。不存在 model-only 状态：description 只会 _增加_ agent discovery，从不会移除人类的。它为那份 discoverability 支付每轮永久的 **context load**。其他 skills 也能触达它，因为让它能被 agent 发现的 description 也让它可被调用。一个内容全是 **reference** 的 model-invoked skill 也是共享 reference 的一个 home：另一个 skill 可以调用它，所以多个 skills 需要的 reference 就放在一处。只有当 agent 必须自行触达时才选择它；如果它除了手动触发外从不触发，就去掉 description，不付 context load。

_Avoid_: ability, tool, capability

### User-Invoked

去掉 **description** 的 skill——对 agent 不可见，只能由人类输入名称触达（user-_only_，而 **model-invoked** 是 user-_and-agent_）。它用零 **context load** 换取 agent-discoverability。因为没有 description，除了人类以外没有任何东西能触达它：其他 skill 也不能触发它。

_Avoid_: procedure, workflow, command

### Description

Skill 的 machine-readable trigger，也是 **model-invoked** skill 被迫始终加载的唯一 **context pointer**。它的存在本身 _就是_ invocation axis：保留它，skill 就是 model-invoked（且可被其他 skills 触达）；删除它，skill 就是 **user-invoked**，只能由人类触达。它是 model-invoked skill 的 **context load** 来源。

_Avoid_: frontmatter, summary

### Context Pointer

保存在 agent context 中的一段 reference，命名某个 out-of-context material，并编码触达它的条件。**Description** 是顶层 context pointer（context window → skill）；指向 disclosed files 的 pointers 是同一对象下一层。它的措辞，而不是目标，决定 agent _何时_ 触达——以及 _多可靠_。一个 must-have 目标藏在措辞薄弱的 pointer 后面，就是一个 variance bug：先修措辞，只有在 sharpening 失败时才内联材料。

_Avoid_: link, reference, import

### Context Load

**Model-invoked** skill 对 agent context window 施加的成本：它的 **description** 始终加载，消耗 tokens 和 attention。**User-invoked** skills 通过没有 description 避开它，它也是拆分成更多 model-invoked skills 的刹车。

_Avoid_: token cost, context bloat

### Cognitive Load

**User-invoked** skill 对人施加的成本：他们必须记在脑子里的东西——哪些 skills 存在以及何时使用它们（人是 index）。**Model-invocation** 通过 agent-discoverability 消除它，它也是拆分成更多 user-invoked skills 的刹车。它不是纯粹要最小化的成本：这是 human agency 的价格，是一些 skills 保持 user-invoked 的原因。把它花在 human judgement 重要处；在不重要处移除它。

_Avoid_: human index, burden, overhead

### Router Skill

一个 **user-invoked** skill，职责是指向你其他的 user-invoked skills——命名每一个以及何时触达它——这样人只需记住一个 skill 而不是许多。它只能提示，从不能触发它们：user-invoked skills 没有 **description**，所以除了人类以外没有任何东西能触达它们。它治疗 user-invoked skills 增多后的 **cognitive load**。

_Avoid_: dispatcher, menu, registry, index, router procedure

### Granularity

Skills 的切分细度。更细的切分会花两种 load 之一：更多 **model-invoked** skills 花 **context load**（更多 descriptions 挤占 window、争夺 attention）；更多 **user-invoked** skills 花 **cognitive load**（更多要人记住和触达的东西）。两种切法指引切分。按 **invocation** 切时，当你有一个独立的 **leading word** 来触发它——一个你真的在 prompts 中使用的触发词——就拆出 model-invoked skill。按 **sequence** 切时，当一个 step 的 **post-completion steps** 需要隐藏时就拆分一连串 **steps**，因为把它隔离在自己的 context 中能清空后续内容。当心反方向：合并 sequences 会把每个 step 的 post-completion steps 暴露给后续内容，诱发 premature completion。

_Avoid_: chunking, modularity

## Information Hierarchy

Skill 内容如何安排，以及每块内容在 ladder 上的位置。

### Information Hierarchy

Skill 的内容按 agent 需要材料的即时程度排序——一个单一的 ladder，由两种切法产生：in-file 还是在 pointer 后面，以及 step 还是 reference。Rungs：

- **Steps** — in-file, primary
- **Reference**, in-file — secondary
- **Reference**, disclosed — behind a **context pointer**

没有 **steps** 的 skill 只使用底下两层——通常是合法的 flat peer-set（例如一个 review 的所有规则在一个 rung 上），这不是坏味道。Hierarchy 独立于 invocation：skill 可以 model- 或 user-invoked，无论它是全 steps、全 reference 还是两者都有。当一个 skill 有 steps 时，本应 disclosed 的 in-file reference 会埋没它们，让关注它们变成抛硬币——这是一个 variance 杠杆，而不只是 legibility 杠杆。保持 ladder 顶层清晰；把能下放的都推下去。

_Avoid_: structure, organization, layout

### Steps

Agent 执行的有序动作——当一个 skill 有它们时，是其内容的 primary tier，也是在 SKILL.md 中赢得位置的部分。不是所有 skill 都有 steps：skill 可以全是 steps（`tdd`）、全是 **reference**（一个 review），或两者都有，独立于 invocation。每个 step 都以 **completion criterion** 结束，无论清晰还是模糊。

_Avoid_: workflow, instructions, choreography

### Reference

Agent 按需查阅的材料：definitions、facts、parameters、examples、conditional instructions。当一个 skill 有 **steps** 时，它次于它们；当一个 skill 没有 steps 时，它就是全部内容；或者它完全活在任何 skill 之外——见 **External Reference**。它通过 **context pointers** 触达，是 **progressive disclosure** 的主要候选。

_Avoid_: supporting material, docs, background

### External Reference

位于 skill system 之外的 **Reference**：普通文件，没有 **description**，没有 **steps**，不可调用——任何 skill 都能指向它。它是无需自行触发的共享 reference 的 home，也是两个 **user-invoked** skills 能使用的唯一共享 home，因为两者都没有 description，所以谁也不能触发对方。

_Avoid_: doc, resource, knowledge base

### Progressive Disclosure

把 **reference** 沿 ladder 下移——移出 SKILL.md、放到 **context pointer** 后面——让顶层保持清晰。这主要不是 token 优化；它是 **information hierarchy** 得以保护的方式。通过 **branching** 授权：disclose 只有部分 branches 需要的内容，内联每条路径都需要的内容，如果一个 pointer 在 must-have 材料上触发不可靠，就 sharpen 它的措辞，只有在那失败时才把它拉回内联。

_Avoid_: lazy loading, chunking

### Co-location

把 agent 同时需要的材料放在一起：一个概念的 definition、rules 和 caveats 放在同一 heading 下，而不是散落在文件各处——这样读一部分时它的邻居也随之而来。它是 **Information Hierarchy** 的文件内 companion：hierarchy 排列一块内容 _下移多远_；co-location 决定一旦到了那里 _什么在它旁边_。对于一组 **reference** 的正确格式没有公式；检验标准是一个 skill 应读起来像为 agent 写的文档，而分组的材料读起来就是那样，散落的材料则不是。有别于 **Duplication**：那是在两处重复同一个 meaning，而散落是把单个 meaning 碎片化到许多处。

_Avoid_: grouping, clustering, cohesion

### Sprawl

_Failure mode._ 一个 skill 实在太长——SKILL.md 中太多行——无论它们是否 stale 或重复。即使一个全 live、全 unique 的 skill 也会 sprawl。它伤害 readability（agent 要跋涉过更多才能行动，attention 在过量内容上变薄）、maintainability（每多一行就多一行要保持 **relevant**）和 tokens。治疗方式是 **information hierarchy**：把 **reference** 推到 **context pointers** 后面，并按 **branch** 或 sequence 拆分，让每条路径只携带它需要的。有别于 **sediment**（来自 stale 累积的长度）和 **duplication**（来自重复 meaning 的长度）——sprawl 是长度本身，无论其成因。

_Avoid_: bloat, length, size, verbosity

## Steering

塑造 agent runtime behavior、朝向 **Predictability** 的杠杆。

### Branch

Skill 可以被调用的一种不同方式——skill 处理的一个 case——这样不同 runs 会沿着不同路径穿过它。一个有许多 steps 的 skill 可能携带许多 branches；线性 skill 没有 branch。

_Avoid_: path, case, fork

### Leading Word

一个紧凑概念——也叫 _Leitwort_——已经存在于模型预训练中，agent 会在运行 skill 用它思考。它通过调用模型已持有的 priors，用最少 tokens 编码 behavioral principle（例如 _lesson_、_proximal zone of development_、_fog of war_、_tracer bullets_）。作为 token 而非句子重复，它在整个 skill 中累积 distributed definition，并锚定一整片 behavior。如果你定义清楚，自创一个也行，但一个生造的词不招募 priors——你用 definition tokens 支付一个预训练词免费给予的东西。先找一个已有的词。

Leading word 两次服务 **predictability**。正文中它锚定 **execution**——agent 每次遇到该概念都触发同类行为，在 flat reference 内部它把 attention 聚焦到要找的一类东西上，每次 run 招募正确的检查。**Description** 中它锚定 **invocation**——而且不仅在 skill 内部：当同一个词存在于你的 prompts、docs 和 codebase 中，agent 会把那份 shared language 连到该 skill，更可靠地触发它。用你真的在想要该 skill 时使用的 leading words 来措辞 description。

_Avoid_: keyword, term, motif

### Completion Criterion

告诉 agent 一个工作单元完成的条件——它据以判断的目标。两个属性让它成为杠杆，而不只是一种品质。它的 **clarity**（agent 能分辨 done 与 not-done 吗？）抵抗 **premature completion**——一个模糊的边界（"达成了理解"）让 agent 宣布完成并滑向下一步；这个轴需要 _steps_ 才起作用，因为 premature completion 是 steps 之间的失败。它的 **demand**（它要求多少）设定 **legwork**——"每个修改过的 model 都被考虑到" 迫使彻底的工作，而 "产出一个变更列表" 则不会——而这个轴 _不_ 绑定 step：它也能约束一组 flat reference，这就是为什么一个没有 steps 的 skill 仍携带 exhaustiveness 标准（"每条规则都被应用"）。最强的 criteria 既可检查又 exhaustive。

_Avoid_: done condition, exit condition, stopping rule

### Legwork

Agent 在单个 step 内幕后做的工作：读文件、探索 codebase、修改、挖出所需材料，而不是把问题丢给用户。它活在 step 结构之下：从不作为自己的 step 写出，潜伏在措辞中，由 agent 而非 skill 控制。它是 **post-completion steps** 跨 step 拉力的 step 内对应物。它被一个 **leading word**（_comprehensive_、_thorough_）或一个要求工作 exhaustive 的 **completion criterion** 提升——包括应用于 flat reference 的 demand 轴，正是它驱动一个 flat reference 的 skill 覆盖它所有的 rungs。它要么在缺少那种 demand 时变薄，要么在 **premature completion** 把 step 截短时变薄。

_Avoid_: scope, effort, diligence, coverage

### Post-Completion Steps

当前 step 之后的 **steps**。可见时，它们会把 agent 向前拉入 **premature completion**——它看到的越多，拉力越强；防御方式是把 steps 的 sequence 拆成两段来隐藏它们。

_Avoid_: horizon, fog of war, lookahead

### Premature Completion

_Failure mode._ 当前 step 尚未真正完成就结束，因为 agent 的注意力滑向 being done 而非工作本身。一个 steps 之间的失败：它需要 **steps** 才会发生——一个没有 steps 却提前退出的 skill 不是 premature completion，而是未满足 demand 下的单薄 **legwork**。两股力量的拔河：可见的 **post-completion steps**（向前的拉力）与 **completion criterion** 的 clarity（阻力——一个尖锐、可检查的标准能守住；模糊的则会让步）。模糊是必要条件：一个尖锐的边界无论后续有多少 steps 可见都能抵抗拉力，所以一个从不 rush 的 step 无需防御。两个杠杆能守住一个确实 rush 的 step，但要按顺序取用：**先 sharpen 边界**——它是局部且廉价的。只有当 criterion 不可避免地模糊 _且_ 你真的观察到 rush 时，才 **隐藏后续 steps**——而隐藏只在跨越一个真实的 context 边界时才起作用（一个 user-invoked 交接或一个 subagent 派发；一个内联的 model-invoked 调用会把后续 steps 留在 context 中，什么也没清空）。它是单薄 legwork 的一个成因，但有别于它：即使一个 step 运行到完全完成，legwork 也可能单薄。

_Avoid_: premature closure, the rush, rushing, shortcutting

### Negation

_Failure mode._ 用 prohibition 引导——告诉 agent _不要_ 做什么——会把被禁止的 behavior 拖进 context，让它 _更_ 容易出现，而不是更少。_Don't think of an elephant_，于是满脑子都是 elephant；_never write verbose comments_，verbosity 恰恰是模型刚读到的 pattern。Negation 是弱 modifier，会被强烈激活的 concept 压过，因此禁令读起来有一半像是在指示它去做那件事。它的 **leading word** 是 _elephant_：prohibition 带入 frame 的任何东西。修复方法：prompt **positive**——描述目标 behavior（"write one-line comments"），让被禁止的行为根本不被说出。只有某种行为无法用正面措辞表达、必须作为 hard guardrail 时，prohibition 才有存在价值；即使如此，也要配上 positive target，让注意力落到应该怎么做。

_Avoid_: ironic rebound, don't-prompting, the pink elephant

## Pruning

保持 skill 精瘦——每个 remedy 对应它治疗的 failure。

### Single Source of Truth

每个 meaning 恰好存在于一个权威位置的期望状态，这样对 skill behavior 的改动就是一处的改动。**Duplication** 是它的违反。

_Avoid_: home, canonical location

### Duplication

_Failure mode._ 同一个 meaning 被给予多个 **single source of truth**。它增加维护成本（改一处，你必须改其他处）、消耗 tokens，并夸大 prominence——重复一个 meaning 会让它在 ladder 上的权重超过其真实等级。它是 **leading word** 的意外反面，后者通过重复一个 token（从不是 meaning）来故意提升 attention。

_Avoid_: repetition, redundancy

### Relevance

一行是否仍然支撑 skill 的工作——这是保留什么的透镜。一行失去 relevance，要么是因为从不支撑任务（纯粹的阐述，或一个本应 disclosed 的 **branch**），要么是因为变 stale：随着它描述的 behavior 或世界变化而过时。更短的 skills 更容易保持 relevant，因为每一行检查起来更廉价。有别于 **no-op**：relevance 问的是一行是否支撑任务，而不是它是否改变 behavior。

_Avoid_: load-bearing, staleness, freshness

### Sediment

_Failure mode._ 沉积在 skill 中、从不清理的旧内容层，因为添加看似安全、删除看似有风险——于是 stale 且无关的行累积，你必须钻透它们才能找到仍然 live 的东西。它是任何缺少 pruning discipline 的 skill 的默认命运；是 **relevance** 的缓慢侵蚀，有别于 **duplication** 的重复 meaning。

_Avoid_: accretion, bloat, cruft, rot

### No-Op

_Failure mode._ 一条没有改变任何东西的 instruction，因为模型默认就会这么做——你付 load 去告诉 agent 它本来就会做的事。测试：一行是否改变默认 behavior？一行可以完全 **relevant** 却仍是 no-op。让一个 **leading word** 免费的那些 priors，也让一个 no-op 毫无价值。

Leading word 是一种 _technique_；No-Op 是对一行的 _verdict_——而它们会交叉。一个弱到打不过默认的 leading word 就是 no-op（_be thorough_，当 agent 已经大致 thorough），修法是换一个能通过 verdict 的更强的词（_relentless_），而不是换一种 technique。所以 No-Op 测试——它是否改变默认 behavior？——也是你评判一个 leading word 是否配得上其重复的方式。这是 model-relative 的，不是 reader-relative 的：两个人对一行是否是 no-op 有分歧，是在对默认有分歧，通过运行 skill 来解决，而不是通过辩论。

_Avoid_: redundant instruction, restating the obvious, belaboring

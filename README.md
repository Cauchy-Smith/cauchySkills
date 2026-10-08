# cauchySkills

个人 **Agent Skills** 合集：面向 Codex / Claude Code 等编码智能体的技能库，以「一个目录一个技能」组织，每个技能由一份 `SKILL.md` 定义（YAML frontmatter 声明 `name` 与 `description`，正文为执行指令）。

共 **99** 个技能：82 个顶层技能 + `nature-skills/` 套件 12 个 + `.system/` 内置技能 5 个。

## 目录结构

```
cauchySkills/
├── <skill-name>/SKILL.md        # 顶层技能，共 82 个
├── nature-skills/              # Nature 系列学术写作套件（含 12 个子技能）
├── .system/                    # 随 Codex 分发的内置技能
└── *.md                        # 说明文档
```

## 技能清单

### 核心入口 · 元技能

| 技能 | 说明 |
| --- | --- |
| [`ask-matt`](ask-matt/SKILL.md) | 询问当前情境适合哪个技能或流程；它是本仓库所有 skills 的路由器。 |
| [`find-skills`](find-skills/SKILL.md) | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities … |
| [`create-plan`](create-plan/SKILL.md) | Create a concise plan. Use when a user explicitly asks for a plan related to a coding task. |
| [`planning-with-files`](planning-with-files/SKILL.md) | Manus-style persistent file-based planning for AI coding agents: keeps task plan.md, findings.md, and progress.md on disk so work survives context loss and /clear … |
| [`brainstorming`](brainstorming/SKILL.md) | You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation. |
| [`wayfinder`](wayfinder/SKILL.md) | 把单个 agent session 装不下的一大块工作规划成 issue tracker 上的 decision tickets shared map，并逐一解决，直到通往 destination 的路清晰。 |
| [`handoff`](handoff/SKILL.md) | 把当前对话压缩成交接文档，让另一个代理接手。 |
| [`claude-handoff`](claude-handoff/SKILL.md) | 把当前对话交接给一个全新的 background agent，让它立即接手工作。 |
| [`pua`](pua/SKILL.md) | 让你的 AI 不敢摆烂。用大厂 PUA 话术穷尽一切方案。触发条件：(1) 任务失败 2+ 次或反复微调同一思路; (2) 即将说'我无法解决'、建议用户手动操作、未验证就归因环境; (3) 被动等待——不搜索、不读源码、只等指示 … |
| [`capacity-evolver`](capacity-evolver/SKILL.md) | A self-evolution engine for AI agents. Analyzes runtime history to identify improvements and applies protocol-constrained evolution. |
| [`writing-great-skills`](writing-great-skills/SKILL.md) | 编写和编辑优秀 skills 的参考：让技能可预测的词汇和原则。 |
| [`setup-matt-pocock-skills`](setup-matt-pocock-skills/SKILL.md) | 为此仓库配置 engineering skills——设置其 issue tracker、triage labels 词汇与 domain docs 布局。在首次使用其他 engineering skills 前运行一次。 |

### 学术 · 科研 · 论文

| 技能 | 说明 |
| --- | --- |
| [`academic-research-suite`](academic-research-suite/SKILL.md) | ARS-Codex workflows for research, academic writing, manuscript review, research-to-paper pipelines, and experiment planning … |
| [`research`](research/SKILL.md) | 对照高可信一手来源调研问题，并把发现保存为仓库中的 Markdown 文件。适用于用户想调研主题、收集文档或 API 事实，或把阅读工作委托给后台代理时。 |
| [`literature-survey-generator`](literature-survey-generator/SKILL.md) | Generate a complete academic literature survey from scratch using multi-agent orchestration. Searches academic databases (OpenAlex, CrossRef, Unpaywall), downloads PDFs, builds BibTeX … |
| [`paper-reader`](paper-reader/SKILL.md) | Use when user asks to "read paper", "analyze paper", "summarize paper", "读论文", "分析文献", "帮我看一下这篇paper", "论文笔记", or provides a PDF file that appears to be an academic paper … |

### 数学建模全流程

| 技能 | 说明 |
| --- | --- |
| [`problem-analysis`](problem-analysis/SKILL.md) | 解读数学建模题目，为后续建模产出准确、可审计的问题定义。 |
| [`modeling`](modeling/SKILL.md) | 基于题目分析建立可复现的数学模型和模型契约。 |
| [`coding`](coding/SKILL.md) | 实现并执行已批准的数学模型，产出可复现代码和执行记录。 |
| [`visualization`](visualization/SKILL.md) | 将真实执行的建模结果转化为可追溯的图表、表格和证据映射。 |
| [`compliance`](compliance/SKILL.md) | 审查数学建模项目的证据、 一致性、可复现性和投稿合规性。 |
| [`paper-writing`](paper-writing/SKILL.md) | 撰写并编译数学建模 LaTeX 论文，确保最终 PDF 和所有数字论断都能追溯到当前证据。 |
| [`math-modeling-orchestrator`](math-modeling-orchestrator/SKILL.md) | Coordinate a math-modeling project from problem interpretation through compliance review using project state, stage-specific skills, quality gates, dependency versioning, and rollback. |
| [`math-analyst`](math-analyst/SKILL.md) | 充当数学建模竞赛的赛题剖析者（审题）：收齐题目与附件，逐句解析出背景信息/核心问题/已知条件/约束条件四类信息，拆出各小问的直接目标与隐含目标，梳理小问关联与条件依赖，判定各问题型并记录判断依据，盘点数据与门槛，登记歧义与假设，产出供建模手、编程手、写作手共用的剖析简报。用于拿到赛题后需要读懂题目、拆解小问、判断题型、盘点附件数据、识别隐含目标与陷阱、或在建模动手前建立团队共同理解时。触发词：审题 … |
| [`math-modeler`](math-modeler/SKILL.md) | 充当数学建模竞赛的建模手：以赛题剖析简报为起点，从内置模型库中为每个小问生成候选集，按数据门槛、假设匹配、可解性与创新性对候选模型做对比选型，并为选定模型撰写假设、符号、方程与检验设定，产出可直接交接给编程手与写作手的建模契约与交接记录。用于研究生数学建模竞赛（华为杯）及各类数学建模赛题的建模阶段：需要在多个候选模型间比较取舍、选定主模型与备选、撰写模型假设与符号说明、或为编写求解代码与撰写论文准 … |
| [`math-coder`](math-coder/SKILL.md) | 充当数学建模竞赛的编程手：读取建模手的模型契约与编程交接单，用可复现的代码实现模型、跑出真实结果与论文级图表，并按题型做检验、灵敏度与鲁棒性分析，产出可直接支撑论文写作的结果报告。用于把建模方案落成代码与结果时：编写或调试求解代码、跑数出图、复现结果、做模型检验与灵敏度分析、或为写作手整理结果素材。触发词：编程手、写代码、代码实现、求解、跑一下、出图、结果可视化、结果分析、模型检验、可复现、华为杯 … |
| [`math-writer`](math-writer/SKILL.md) | 充当数学建模竞赛的写作手：把建模手的模型方案与编程手的结果报告组织成符合「华为杯」格式规范与官方模板的完整论文，产出 paper/paper.md 源文件、论文.docx 与提交用 PDF，并自动核验格式合规性。用于撰写或修订数学建模论文时：写摘要、问题重述、问题分析、模型假设、符号说明、模型建立与求解、模型检验、模型评价与推广、参考文献、附录，或处理排版、页码、图表编号、公式、参考文献格式与格式 … |
| [`math-modeling-review`](math-modeling-review/SKILL.md) | 输入数学建模竞赛论文文档，逐项对照国奖评审标准审核格式规范性、模型假设合理性、建模方法创造性、结果表述清晰度与参考文献引用正确性，输出结构化分项评分表、格式问题逐条标注与综合评价修改建议报告；适用于数学建模竞赛评委批量化审核参赛论文、指导教师对学生作品进行赛前预审、参赛团队自查论文是否达到国奖标准的场景；触发词：评审数学建模论文、检查建模论文质量、评估国奖水平、审核建模竞赛论文、论文国奖评审、数学 … |
| [`math-modeling-write`](math-modeling-write/SKILL.md) | 数学建模竞赛论文写作规范指导。适用于撰写、修改、评审数学建模竞赛论文时，提供标准的论文结构、各部分写作要求和格式规范。触发词：数学建模写作、建模论文、论文结构、摘要写作、模型假设、符号说明、参考文献格式、模型建立、模型总结。 |

### 中文写作 · 沟通

| 技能 | 说明 |
| --- | --- |
| [`humanizer-zh`](humanizer-zh/SKILL.md) | 去除文本中的 AI 生成痕迹。适用于编辑或审阅文本，使其听起来更自然、更像人类书写。 基于维基百科的"AI 写作特征"综合指南。检测并修复以下模式：夸大的象征意义、 宣传性语言、以 -ing 结尾的肤浅分析、模糊的归因、破折号过度使用、三段式法则、 AI 词汇、否定式排比、过多的连接性短语。 |
| [`edit-article`](edit-article/SKILL.md) | 通过重组章节、提升清晰度、收紧文字来编辑并改进文章。适用于用户想编辑、修订或改进文章草稿时。 |
| [`writing-shape`](writing-shape/SKILL.md) | Writing, exploit——把原始素材塑造成文章，一段一段地推进。 |
| [`writing-beats`](writing-beats/SKILL.md) | Writing, exploit——把原始素材组装成一段节拍旅程，在某个 beat 依赖一个术语之前先把它 grounded。 |
| [`writing-fragments`](writing-fragments/SKILL.md) | Writing, explore——挖掘原始 fragments，暂不施加任何结构。 |
| [`to-questionnaire`](to-questionnaire/SKILL.md) | 把你无法完整回答的 decision 转成一份交给他人填写的 questionnaire。 |
| [`to-spec`](to-spec/SKILL.md) | 把当前对话转成 spec 并发布到项目 issue tracker——不做访谈，只综合已经讨论的内容。 |
| [`to-tickets`](to-tickets/SKILL.md) | 把 plan、spec 或当前对话拆成一组 tracer-bullet tickets，每个 ticket 声明 blocking edges，并发布到已配置的 tracker；本地用每 ticket 一个文件中的文本 edge，真实 tracker 用 native blocking links。 |

### 前端 · 设计 · 演示

| 技能 | 说明 |
| --- | --- |
| [`frontend-design`](frontend-design/SKILL.md) | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters … |
| [`design-taste-frontend`](design-taste-frontend/SKILL.md) | Anti-slop frontend skill for landing pages, portfolios, and redesigns. The agent reads the brief, infers the right design direction, and ships interfaces that do not look templated … |
| [`ui-ux-pro-max`](ui-ux-pro-max/SKILL.md) | UI/UX design intelligence for web and mobile. Searchable local database with 84 styles, 192 color palettes, 74 font pairings, 192 product types, 98 UX guidelines, 104 icon entries … |
| [`emilkowalski-motion`](emilkowalski-motion/SKILL.md) | Motion-design follow-up skill inspired by Emil Kowalski's animation guidance. Use after an interface exists to add tasteful micro-interactions, state transitions … |
| [`impeccable-design-polish`](impeccable-design-polish/SKILL.md) | Follow-up design polish skill inspired by Impeccable. Use after a web or HTML artifact exists to audit, critique, polish, animate, harden, and prepare the page for a live/share pass. |
| [`design-an-interface`](design-an-interface/SKILL.md) | 使用并行子代理为模块生成多个显著不同的接口设计。适用于用户想设计 API、探索接口选项、比较模块形状，或提到 “design it twice” 时。 |
| [`prototype`](prototype/SKILL.md) | 构建一次性原型来回答一个设计问题。适用于用户想验证某个 state model 或 logic 是否感觉对，或探索 UI 应该长什么样时。 |
| [`ppt-master`](ppt-master/SKILL.md) | AI-driven multi-format SVG content generation system. Converts source documents (PDF/DOCX/URL/Markdown) into high-quality SVG pages and exports to PPTX through multi-role collaboration … |
| [`ppt-outline-generator`](ppt-outline-generator/SKILL.md) | Use when the user wants to plan a presentation, turn notes or drafts into a slide outline, or structure a report, pitch, or review deck. |
| [`hatch-pet`](hatch-pet/SKILL.md) | Create, repair, validate, visually QA, and package Codex-compatible animated pets and pet spritesheets from character art, generated images, company or prospect brand cues, or visual references … |

### 工程实践 · 调试 · 架构

| 技能 | 说明 |
| --- | --- |
| [`tdd`](tdd/SKILL.md) | 测试驱动开发。适用于用户想用先写测试的方式构建功能或修复缺陷、提到 “red-green-refactor”，或需要集成测试时。 |
| [`systematic-debugging`](systematic-debugging/SKILL.md) | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| [`diagnosing-bugs`](diagnosing-bugs/SKILL.md) | 面向棘手缺陷和性能回退的诊断循环。适用于用户说 “diagnose” / “debug this”，或报告某些东西 broken、throwing、failing、slow 时。 |
| [`debug-assistant`](debug-assistant/SKILL.md) | Helps debug Python errors and exceptions |
| [`codebase-design`](codebase-design/SKILL.md) | 用于设计深模块的共享词汇。适用于用户想设计或改进模块接口、寻找深化机会、决定 seam 放在哪里、让代码更容易测试或更适合 AI 导航，或其他技能需要深模块词汇时。 |
| [`improve-codebase-architecture`](improve-codebase-architecture/SKILL.md) | 扫描代码库中的深化机会，生成可视化 HTML 报告，然后围绕你选中的候选项继续追问。 |
| [`domain-modeling`](domain-modeling/SKILL.md) | 构建并打磨项目的领域模型。适用于用户想明确领域术语或通用语言、记录架构决策，或其他技能需要维护领域模型时。 |
| [`ubiquitous-language`](ubiquitous-language/SKILL.md) | 从当前对话提取 DDD 风格的 ubiquitous language glossary，标记歧义并提出标准术语。保存到 UBIQUITOUS LANGUAGE.md。适用于用户想定义领域术语、构建词汇表、收紧术语、创建通用语言，或提到 “domain model” / “DDD” 时。 |
| [`migrate-to-shoehorn`](migrate-to-shoehorn/SKILL.md) | 将测试文件从 as 类型断言迁移到 @total-typescript/shoehorn。适用于用户提到 shoehorn、想替换测试中的 as，或需要局部测试数据时。 |
| [`setup-ts-deep-modules`](setup-ts-deep-modules/SKILL.md) | 在 TypeScript repo 中接入 dependency-cruiser，让每个 package 成为 deep module：implementation 隐藏在 subfolders 中，只能通过 entry-point files 访问。User-invoked。 |
| [`request-refactor-plan`](request-refactor-plan/SKILL.md) | 通过用户访谈创建带小提交的详细重构计划，然后作为 GitHub issue 提交。适用于用户想规划重构、创建重构 RFC，或把重构拆成安全的增量步骤时。 |
| [`implement`](implement/SKILL.md) | 基于 spec 或 ticket 集合实现一段工作。 |
| [`scaffold-exercises`](scaffold-exercises/SKILL.md) | 创建包含章节、题目、答案和讲解的练习目录结构，并确保通过 linting。适用于用户想 scaffold exercises、创建 exercise stubs，或设置新的课程章节时。 |
| [`resolving-merge-conflicts`](resolving-merge-conflicts/SKILL.md) | 适用于需要解决正在进行的 git merge/rebase 冲突时。 |
| [`ponytail`](ponytail/SKILL.md) | Forces the laziest solution that actually works, simplest, shortest, most minimal. Channels a senior dev who has seen everything: question whether the task needs to exist at all (YAGNI) … |

### 代码审查 · 安全 · 发布

| 技能 | 说明 |
| --- | --- |
| [`code-review`](code-review/SKILL.md) | 从固定点（commit、branch、tag 或 merge-base）开始，按 Standards（代码是否符合本仓库记录的编码标准？）和 Spec（代码是否符合来源 issue/PRD 的要求？）两个轴线审查变更。两个审查会在并行子代理中运行，并并排报告。适用于用户想审查 branch、PR、进行中的变更，或要求 “review since X” 时。 |
| [`code-reviewer`](code-reviewer/SKILL.md) | Reviews code for security vulnerabilities, performance issues, and best practices. Use when reviewing code, performing security audits, checking for code quality, reviewing pull requests. |
| [`security-threat-model`](security-threat-model/SKILL.md) | Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model … |
| [`qa`](qa/SKILL.md) | 交互式 QA 会话，用户以对话方式报告缺陷或问题，代理创建 GitHub issues。后台探索代码库以获取上下文和领域语言。适用于用户想报告缺陷、执行 QA、以对话方式提交 issues，或提到 “QA session” 时。 |
| [`gh-fix-ci`](gh-fix-ci/SKILL.md) | Inspect GitHub PR checks with gh, pull failing GitHub Actions logs, summarize failure context, then create a fix plan and implement after user approval … |
| [`setup-pre-commit`](setup-pre-commit/SKILL.md) | 在当前仓库设置 Husky pre-commit hooks，集成 lint-staged (Prettier)、类型检查和测试。适用于用户想添加 pre-commit hooks、设置 Husky、配置 lint-staged，或在提交时运行格式化、类型检查和测试时。 |
| [`git-guardrails-claude-code`](git-guardrails-claude-code/SKILL.md) | 设置 Claude Code hooks，在危险 git commands（push、reset --hard、clean、branch -D 等）执行前阻止它们。适用于用户想防止破坏性 git 操作、添加 git safety hooks，或在 Claude Code 中阻止 git push/reset 时。 |
| [`triage`](triage/SKILL.md) | 让 issues 和 external PRs 通过一组 triage roles 状态机——分类、验证、必要时 grilling，并写出 agent-ready briefs。 |
| [`teach`](teach/SKILL.md) | 在这个工作区中教用户一个新技能或概念。 |
| [`obsidian-vault`](obsidian-vault/SKILL.md) | 在 Obsidian vault 中使用 wikilinks 和索引笔记搜索、创建并管理笔记。适用于用户想在 Obsidian 中查找、创建或组织笔记时。 |
| [`webapp-testing`](webapp-testing/SKILL.md) | Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots … |
| [`pytorch-research`](pytorch-research/SKILL.md) | Advanced sub-skill for PyTorch focused on deep research and production engineering. Covers custom Autograd functions, module hooks, advanced initialization, Distributed Data Parallel (DDP) … |
| [`computer-vision-assistant`](computer-vision-assistant/SKILL.md) | Comprehensive CV learning assistant. Use when studying image processing, object detection, segmentation, or any CV tasks. Helps with algorithm understanding, implementation, and model optimization. |

### 上下文压缩 · 专家追问

| 技能 | 说明 |
| --- | --- |
| [`grilling`](grilling/SKILL.md) | 围绕计划、decision 或 idea 持续追问用户。适用于用户想对自己的思路做压力测试，或使用任何 “grill” 触发措辞时。 |
| [`grill-me`](grill-me/SKILL.md) | 一个用来打磨计划或设计的持续追问式访谈。 |
| [`grill-with-docs`](grill-with-docs/SKILL.md) | 一个用来打磨计划或设计的持续追问式访谈，并在过程中创建文档（ADRs 和词汇表）。 |
| [`batch-grill-me`](batch-grill-me/SKILL.md) | 持续追问式访谈，每一轮同时提出当前 frontier 上的所有问题。 |
| [`loop-me`](loop-me/SKILL.md) | 在这个工作区中，就我想构建的工作流规格访谈我。 |
| [`ds-vision-skill`](ds-vision-skill/SKILL.md) | 给纯文本模型（DeepSeek 等）加"眼睛"的多通道视觉路由。当用户发送、粘贴或引用图片、截图、照片、图表、架构图、UI 截图、代码截图、数学题图片、扫描件、PDF 或文档，并要求描述、理解、推理、阅读、提取文字、OCR、解析图表或分析内容时使用（例如"看看这张图"、"识别图中文字"、"解析这个图表"）。三层能力：视觉理解（GLM-4V-Flash 简单任务 / … |

### Nature 系列套件（`nature-skills/`）

| 技能 | 说明 |
| --- | --- |
| [`nature-skills/nature-academic-search`](nature-skills/nature-academic-search/SKILL.md) | Multi-source literature search, citation verification, MeSH search strategy, citation file management (.nbib/.ris/.bib conversion), and reference management (BibTeX, related articles … |
| [`nature-skills/nature-citation`](nature-skills/nature-citation/SKILL.md) | Add strict Nature/CNS citations to manuscript text by splitting long passages into citable segments, searching only accepted flagship and subjournal titles from Nature Portfolio … |
| [`nature-skills/nature-data`](nature-skills/nature-data/SKILL.md) | Prepare, audit, or revise Nature-ready Data Availability statements, data repository plans, dataset citations, and FAIR metadata checklists for manuscripts … |
| [`nature-skills/nature-figure`](nature-skills/nature-figure/SKILL.md) | Submission-grade Nature/high-impact journal figure workflow for Python or R. Use whenever the user asks to create, revise, audit, or polish manuscript figures, multi-panel scientific plots … |
| [`nature-skills/nature-paper-to-patent`](nature-skills/nature-paper-to-patent/SKILL.md) | Convert scientific papers, theses, technical reports, source code, figures, or research manuscripts into evidence-grounded Chinese invention patent drafts … |
| [`nature-skills/nature-paper2ppt`](nature-skills/nature-paper2ppt/SKILL.md) | Build a complete but efficient Nature-style Chinese PPTX presentation from a scientific paper, preprint, PDF, article text, abstract, figure legends, or reading notes … |
| [`nature-skills/nature-polishing`](nature-skills/nature-polishing/SKILL.md) | Polish, restructure, or translate academic prose into Nature-leaning English using writing-strategy principles, curated Nature/Nature Communications article patterns … |
| [`nature-skills/nature-reader`](nature-skills/nature-reader/SKILL.md) | Build full-paper Chinese-English side-by-side, figure/table-aware, source-grounded Markdown readers for journal or conference papers from PDF, DOI, arXiv, publisher HTML, or pasted text … |
| [`nature-skills/nature-response`](nature-skills/nature-response/SKILL.md) | Draft, audit, or revise point-by-point reviewer response letters for Nature-family manuscript revisions. Use when the user provides reviewer comments, editor decision letters, revision notes … |
| [`nature-skills/nature-reviewer`](nature-skills/nature-reviewer/SKILL.md) | Simulate a Nature-style reviewer assessment from the referee perspective rather than an author rebuttal. Use when the user wants a pre-submission review, reviewer report, peer-review style critique … |
| [`nature-skills/nature-writing`](nature-skills/nature-writing/SKILL.md) | Draft, restructure, or plan Nature-style manuscript sections from author-provided claims, results, figures, notes, or Chinese drafts … |
| [`nature-skills/openclaw-medical-skills`](nature-skills/openclaw-medical-skills/SKILL.md) | Codex adaptation of the OpenClaw Medical Skills library. Use for biomedical, clinical, healthcare AI, genomics, bioinformatics, drug discovery, pharmacovigilance, clinical trials, medical imaging … |

### 其他技能

| 技能 | 说明 |
| --- | --- |
| [`wizard`](wizard/SKILL.md) | 生成一个交互式 bash wizard，引导人完成一项手动流程——第三方 setup、一次性 migration、A→B 状态迁移——打开 URL、捕获值、逐步确认，并写入 .env 文件和 GitHub Actions secrets。 |

### 内置技能（`.system/`）

| 技能 | 说明 |
| --- | --- |
| [`.system/imagegen`](.system/imagegen/SKILL.md) | Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts … |
| [`.system/openai-docs`](.system/openai-docs/SKILL.md) | Use when the user asks how to build with OpenAI products or APIs, asks about Codex itself or choosing Codex surfaces, needs up-to-date official documentation with citations … |
| [`.system/plugin-creator`](.system/plugin-creator/SKILL.md) | Create and scaffold plugin directories for Codex with a required .codex-plugin/plugin.json, optional plugin folders/files, valid manifest defaults, and personal-marketplace entries by default … |
| [`.system/skill-creator`](.system/skill-creator/SKILL.md) | Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge … |
| [`.system/skill-installer`](.system/skill-installer/SKILL.md) | Install Codex skills into $CODEX HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill … |

## 使用方式

把技能目录放入所用智能体的 skills 目录即可被发现，例如 Codex：

```powershell
# 单个技能
Copy-Item -Recurse .\<skill-name> "$env:USERPROFILE\.codex\skills\"

# 全量同步
robocopy . "$env:USERPROFILE\.codex\skills" /E /XD tmp_browsermcp tmp_gms tmp_neon tmp_supabase .git
```

技能也可按需单独取用：克隆本仓库后，直接把需要的技能目录复制或软链到目标位置。

## 说明

- 各技能版权与许可见其自身目录内的 `LICENSE` / `LICENSE.txt`；第三方来源技能保留原始署名。
- `tmp_*` 临时目录（第三方 MCP 仓库的本地检出）不纳入版本管理，见 `.gitignore`。

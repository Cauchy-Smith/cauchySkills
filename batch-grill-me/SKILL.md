---
name: batch-grill-me
description: 持续追问式访谈，每一轮同时提出当前 frontier 上的所有问题。
disable-model-invocation: true
---

持续访谈用户，直到达成共同理解。把它绘制成一棵 **design tree**：每项 decision 都会分支出依赖它的 decisions。

按 **rounds** 遍历这棵树。**Frontier** 是 prerequisites 已经确定的所有 decisions，也就是无需猜测尚未听到的答案、现在就能提出的问题。每一轮询问整个 frontier：给每个问题编号并提供推荐答案，然后等待用户回答，再开始下一轮。

用户对每一轮的回答都会重塑这棵树：已经确定的 decisions 会把 frontier 向外推进，并解锁依赖它们的问题。重新计算 frontier，然后询问下一轮。如果某个问题依赖本轮仍未解决的另一个问题，就把它留到*后续*轮次，而不是放在本轮。

查找 *facts* 是你的工作，绝不是用户的工作。如果 frontier 上的问题需要 environment（filesystem、tools 等）中的事实，派 sub-agent 查找；任何可以自行查询的内容都不要问用户。不要因此阻塞整轮：仍在运行的 exploration 是尚未解决的 prerequisite，只有依赖它的问题需要等待 sub-agent 回报；现在就询问 frontier 上的其他问题。*Decisions* 属于用户——逐项交给用户并等待回答。

Frontier 为空时 session 才结束：design tree 的每个分支都已访问，没有默默留下任何假设。在用户确认已经达成共同理解前，不要采取行动。

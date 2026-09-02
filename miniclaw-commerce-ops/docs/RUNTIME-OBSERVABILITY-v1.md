# MiniClaw 运行观测口径与项目侧兼容规则 v1

## 1. 文档状态

- status: `source_audited_helper_corrected_and_dispatch_guard_validated_no_model`
- source_platform_commit: `3ff1c8d6a0707f4a9f0957ff411758e5e141583a`
- 适用范围：project017 的 MiniClaw 主会话、Pi Subagent foreground 运行和 synthetic 冒烟证据。
- 本轮根因修复没有调用模型、没有修改 MiniClaw 或 pi-subagents 来源代码，也没有把 synthetic 结果写成真实经营效果。

## 2. 两类计数不能混用

`@tintinweb/pi-subagents@0.16.1` 的 `record.toolUses` 是 activity-end 聚合值，不是子 Agent 原始 `toolCall` 记录数。

固定来源中：

- `agent-manager.ts:321`、`:582`、`:672` 对每个 `activity.type === "end"` 执行 `record.toolUses++`。
- `agent-runner.ts:944-947` 和 `:1011-1012` 将真实 `tool_execution_end` 映射为 activity end。
- 同一文件的 `:682`、`:701`、`:712`、`:725`、`:735`、`:889` 还会把未知工具、extension 配置告警或 extension bind 错误映射为 activity end；这些活动不一定在子 Agent `.output` 中形成 assistant `toolCall`。

因此 project017 固定采用以下证据优先级：

1. 子 Agent `.output` 中 assistant content 的显式 `toolCall`：业务调用次数权威来源。
2. 对应 `toolResult`：参数结果、`service_run_id`、`analysis_run_id`、耗时和失败状态来源。
3. 父级 `Agent.details.toolUses`：仅作为运行时活动聚合参考；与显式 toolCall 不一致时保留差异，不用于判定 inspect/analyze 的准确次数。
4. Agent 最终自然语言摘要：用于表达审计，不能替代原始轨迹。

第三次冒烟中，父级聚合为 3，子 Agent `.output` 的显式业务 toolCall 为 2。业务链路按后者判定为 inspect ×1、analyze ×1；多出的 activity end 没有足够事件明细可精确归因，不能猜测成第三次业务调用。

## 3. conversation agent 的正常回收状态是 idle

MiniClaw 固定来源 `src/index.ts` 中：

- `:14210` 在处理消息前把 conversation agent 状态设为 `running`。
- `:16975-16984` 的 finally 逻辑对持久 conversation agent 使用 `idle`，只有 fire-and-forget spawn agent 才使用 `completed/error`。
- 最终 assistant 回复可以在 finally 回收状态之前先写入消息存储并广播，因此同一次页面轮询可能观察到“最终回复已出现、平台状态仍为 running”。这是一段可发生的短暂竞态，不应立即等同于平台永久卡死。

旧版辅助页存在两个项目侧问题：

- settled 状态集合遗漏了 `idle` 和 `error`。
- 一看到最终回复就立即停止轮询，没有给 finally 状态回收留出观察窗口。

`runtime/setup-helper/smoke.html` 已改为：

- 最终回复出现后继续只读轮询，不提交新任务。
- 把 `idle/completed/error/failed/interrupted/stopped` 视为平台已回收。
- 最多等待 20 秒；若仍为 running，再记录 `lifecycle_difference` 并停止。
- 始终分别显示 `platform_status` 与 `observed_execution_state`，不互相改写。

## 4. 第三次冒烟的当前结论

- strict business smoke: `pass`
- final reporting accuracy: `pass`
- parent toolUses 与显式 toolCall：`known_non_equivalent_aggregation_semantics`
- 用户当时观察到的 running-after-final：`race_observed_before_helper_fix`
- 是否已证明该 session 后续回收到 idle：`not_captured`

这次运行不需要付费重跑。以后若需要验证生命周期，只使用修复后的只读等待逻辑，或建立不具备提交能力的状态查看页。

## 5. 父级派发尝试必须独立记账

内容增长 v1 的主会话显式轨迹包含两次 `Agent`：第一次由模型添加 `isolation=worktree`，在非 Git 的 project017 中派发失败；第二次才成功创建 `content-growth-analyst`。子 Agent 的 inspect→短视频分析成功不能覆盖第一次父级失败，也不能支持最终回复中的“零失败、无重试”。

无模型根因修复包含两层：

1. authored Supervisor Prompt 明确必须省略 isolation，任一父级参数校验或派发失败立即使当前分支 `blocked`，同一会话不得再次调用 `Agent`。
2. project-local compatibility bridge 在注册 `Agent` ToolDefinition 时移除上游 worktree 推荐，把 isolation 字段说明改为禁止使用，并在 `tool_call` 前置门控中拒绝该参数。首次失败后锁住后续派发，`tool_result` 标记 `isError=true`，同时附加 `project017DispatchAudit`。

`artifacts/miniclaw-subagent-bridge-validation-v2.json` 由真实 `DefaultResourceLoader` 生成，`25/25` 通过；验证中第一次 worktree 调用和第二次无 isolation 调用均在上游 execute 前被阻断，没有创建 AgentSession、没有调用模型。修复后 Profile 随后已写入隔离运行数据库，但内容增长 v2 的首个 Provider 请求在推理前被 `Arrearage` 拒绝，因而没有 Supervisor 工具调用或子 Agent 输出；门控仍未获得修复后真实模型轨迹。

最终运行评估必须分别采集：

- 父级主会话中的 `Agent` toolCall/toolResult、参数、失败与次数。
- 子 Agent `.output` 中的业务 toolCall/toolResult、service/analysis run_id 与顺序。
- Supervisor 最终声明是否与上述两层显式尝试一致。

## 6. 证据边界

- 本文确认的是固定源码的计数与状态语义，以及 project017 辅助页的观测修复。
- 本文没有证明完整一主四专工作流、30 条真实模型评测、真实业务数据或真实经营收益。
- MiniClaw、Pi Agent Runtime 和 pi-subagents 的平台实现不能包装为本人从零研发成果。
- project017 可表述为：基于原始轨迹建立业务 toolCall 权威口径，识别 activity 聚合差异，并修复冒烟页对 conversation agent `idle` 回收状态的误判。
- project017 还可表述为：针对非 Git 工作区补充父级 Agent 的 isolation fail-closed 门控和父子尝试账本；该能力目前只完成无模型验证，不能写成修复后真实 AgentSession 已通过。

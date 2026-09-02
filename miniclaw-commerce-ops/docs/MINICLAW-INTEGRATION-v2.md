# MiniClaw 接入与运行验证说明 v2

## 当前结论

project017 已为 MiniClaw `main@3ff1c8d6a0707f4a9f0957ff411758e5e141583a` 准备一主四专角色文件、五工具 Pi extension、Profile/Workspace 请求模板和 Plugin Catalog 静态资产，并完成 Supervisor + 单个直播专业子 Agent 的真实 synthetic 冒烟。内容增长 v1 暴露出的 worktree 派发与漏报问题已完成无模型根因修复，修复后 Profile 已落库；内容增长 v2 的首个 Provider 请求却在模型推理前被 `Arrearage` 拒绝，所以修复后的 Agent 路由尚未得到真实模型验证。

当前状态：

- Provider configured in isolated runtime: `true`
- Plugin imported: `false`
- Plugin enabled: `false`
- AgentProfile created in isolated runtime: `true`
- Workspace created in isolated runtime: `true`
- ModelRuntime created in isolated runtime: `true`
- AgentSession executed: `true`
- Standalone specialist executed: `false`
- Supervisor plus one specialist executed: `true`
- Full one-main-four-specialist workflow executed: `false`
- Real model called for synthetic smoke: `true`
- Real business data used: `false`
- Post-fix compatibility bridge no-model validation: `true`
- Post-fix AgentProfile applied to isolated runtime: `true`
- Post-fix AgentSession executed: `false`
- Post-fix Pi session initialized before Provider rejection: `true`
- Post-fix Provider inference accepted: `false`

静态/无模型 harness 与真实 AgentSession 证据仍需分开。harness 直接调用 Pi ToolDefinition 或 Loader 已注册工具；v3 脱敏轨迹则记录了 Supervisor 真实派发 `live-conversion-analyst`，并由该子 Agent 显式调用 inspect 与直播分析工具。

## 平台与项目职责

| 类别 | 来源 | 当前用途 | 归属边界 |
| --- | --- | --- | --- |
| Pi Agent Runtime、AgentSession、Plugin Catalog、Subagent 生命周期 | MiniClaw 平台 | 提供运行和调度底座 | 平台整体架构，不写为本人从零研发 |
| `@tintinweb/pi-subagents@0.16.1` | MiniClaw runner | 读取 `.pi/agents` 与 `subagents.json` | 平台依赖；project017 只做角色配置与约束适配 |
| 五工具 Python/FastAPI/stdio MCP | project017 | 执行确定性数据检查、分析和钻取 | project017 已实现并通过 synthetic 工具层验证 |
| Pi extension、compatibility bridge、角色 frontmatter 与运行配置 | project017 | 将业务契约映射到 MiniClaw/Pi，并对非 Git 工作区的父级派发执行 fail-closed 门控 | 静态、无模型加载和旧配置下的一主一子 synthetic 冒烟已验证；修复后 AgentSession 与完整一主四专未验证 |

## 运行结构

```text
MiniClaw Supervisor
  ├─ Agent → content-growth-analyst
  │    └─ role-local Pi extension → role-local stdio MCP process
  ├─ Agent → live-conversion-analyst
  │    └─ role-local Pi extension → role-local stdio MCP process
  ├─ Agent → attribution-lead-analyst
  │    └─ role-local Pi extension → role-local stdio MCP process
  └─ Agent → commerce-review-strategist
       └─ no extension, no tool
```

Supervisor 只负责 `workflow_run_id`、路由、结果收集、Schema 校验和汇总。三个专业角色分别在自己的 MCP 进程内先调用 `inspect_commerce_data`，再调用本域分析和可选 drilldown。这样处理是因为 DatasetManifest 注册表为 MCP 进程内状态，不能假设一个进程登记的数据会自动出现在另一个进程。

## Supervisor 工具边界

MiniClaw 当前 Pi runner 把主会话 `DEFAULT_ALLOWED_TOOLS` 映射为明确的 `selectedTools`，Pi `allowedToolNames` 再过滤项目 extension 工具。project017 的 Profile 同时将 `runtime_policy.mcp` 设为 `disabled`，不把 Plugin MCP 加入 Supervisor 能力。

因此当前设计中：

- Supervisor 使用平台提供的 `Agent`、`get_subagent_result`、`steer_subagent`。
- Supervisor 不直接获得 `commerce_ops_*` 五个项目 extension 工具。
- 专业子 Agent 通过 `extensions` 显式加载 project017 extension，再由 `ext:commerce-ops-mcp/<tool>` 缩小工具范围。
- 复盘策略 Agent 使用 `tools: none`、`extensions: false`。

锁定 commit 的源码、静态配置和 v3 脱敏轨迹共同证明：直播单域冒烟中 Supervisor 只调用一次 `Agent`，没有直接调用 `commerce_ops_*`；`live_conversion_analyst` 依次调用 inspect 与直播分析。内容增长 v1 则真实记录了首次 `isolation=worktree` 失败和第二次派发，不能写成严格通过。

project017 兼容桥现已在注册 `Agent` ToolDefinition 时移除上游 worktree 推荐文案，把 `isolation` 参数说明改为必须省略，并通过 `tool_call`/`tool_result` 门控在创建子 Agent 前拒绝带 isolation 的调用。首次父级失败会锁住本会话后续 `Agent` 派发，并附加 `project017DispatchAudit`；最终报告仍须把父级派发和子级业务工具合并为同一尝试账本。该门控已由真实 `DefaultResourceLoader` 无模型验证，未创建 AgentSession。

## 角色级权限

| 角色 | 允许工具 | 进程状态要求 |
| --- | --- | --- |
| `content_growth_analyst` | inspect、短视频分析、drilldown | 在同一角色进程先 inspect |
| `live_conversion_analyst` | inspect、直播分析、drilldown | 在同一角色进程先 inspect |
| `attribution_lead_analyst` | inspect、渠道线索分析、drilldown | 在同一角色进程先 inspect |
| `commerce_review_strategist` | 无 | 只读取 Supervisor 提供的结构化诊断包 |

`.pi/subagents.json` 使用：

- `strictAgentFiles=true`
- `fallbackSubagent=none`
- `disableDefaultAgents=true`
- `maxSubagentDepth=1`
- `schedulingEnabled=false`

这些配置用于拒绝未知角色、损坏角色文件、默认全工具 Agent、嵌套委派和计划任务入口。

## 五工具 extension

入口：`.pi/extensions/commerce-ops-mcp/index.ts`

依赖：

- `@earendil-works/pi-coding-agent@0.84.2`
- `@modelcontextprotocol/sdk@1.30.0`
- `typebox@1.3.7`

extension 只注册：

1. `commerce_ops_inspect_commerce_data`
2. `commerce_ops_analyze_short_video_data`
3. `commerce_ops_analyze_live_commerce_data`
4. `commerce_ops_analyze_attribution_and_leads`
5. `commerce_ops_drilldown_commerce_metric`

每个 extension 实例维护自己的 MCP Client 与 stdio transport；`session_shutdown` 关闭 transport。所有映射强制 `synthetic=true`，结果详情记录 `automaticRetry=false`。harness 证据仍属于无模型桥接；v3 运行轨迹已另行证明其中两个业务工具由直播专业子 Agent 实际调用。

## Plugin、Profile 与 Workspace

`integrations/miniclaw-plugin-marketplace` 是未来导入 MiniClaw Catalog 的静态目录。它声明同一个 Python stdio MCP Server，但当前仍未导入、未启用，也不是本次运行的工具来源。本次运行使用 project-local Pi extension 与 Subagent compatibility bridge。

`config/agent-profile-create.template.json`：

- 使用四段 Prompt Schema v2。
- authored 模板继续保留 `model_config_id=null`，不把本机运行数据库 ID 写入可复制配置。
- `runtime_policy.skills` 与 `runtime_policy.mcp` 均 disabled。
- 保留 MiniClaw preset，只追加 project017 的 Supervisor 契约。
- 明确 project017 非 Git，`Agent` 必须省略 isolation；父级派发失败立即 `blocked` 且不得第二次派发；最终尝试账本同时覆盖父级与子级。
- authored 模板保持 `model_config_id=null`；隔离运行数据库中的同名 Profile 已通过官方 API 更新为 version 2，并保留原模型绑定。Profile 落库只能证明运行配置已生效，不能替代修复后 Agent 工具轨迹。

`config/workspace-create.template.json`：

- `execution_mode=host`
- `interaction_mode=assistant`
- `custom_cwd=D:\Workspace\project017-miniclaw-commerce-ops`
- authored 模板中的 Profile ID 保留占位符；隔离运行时已另行创建实际 Profile 与 Workspace，敏感或数据库 ID 不进入文档。

## 本地无模型验证命令

```powershell
cd D:\Workspace\project017-miniclaw-commerce-ops
python -B scripts\verify-miniclaw-static-config.py --output artifacts\miniclaw-static-config-v5.json
node scripts\verify-miniclaw-subagent-bridge.mjs --output artifacts\miniclaw-subagent-bridge-validation-v2.json
python -B -m commerce_ops.tool_validation
python -B -m unittest discover -s tests -p "test_*.py" -v
cd .pi\extensions\commerce-ops-mcp
node validate-runtime.mjs --output ..\..\..\artifacts\pi-extension-runtime-v2.json
node validate-pi-resource-loader.mjs --output ..\..\..\artifacts\pi-default-resource-loader-v2.json
npm.cmd audit --json
```

## 结果解释

静态与无模型结果：

- 静态配置：`128/128` 通过。
- extension API harness：`15/15` 通过。
- Pi `DefaultResourceLoader` harness：`14/14` 通过，1 个目标 extension、0 个加载错误。
- Subagent compatibility bridge：`25/25` 通过；包括 worktree 前置拒绝、第二次派发锁止和 `tool_result isError` 审计。
- Node 依赖：Pi `0.84.2`、MCP SDK `1.30.0`、TypeBox `1.3.7`。
- `npm audit --json`：执行时 0 vulnerabilities。
- 两个 harness 均完成 7 次 synthetic 工具调用，`automatic_retry_attempted=false`，并触发 shutdown 关闭 transport。

- 静态配置通过：证明文件、Prompt、角色 allowlist、Plugin 声明、版本和文档边界一致。
- extension harness 通过：证明 Node 原生 TypeScript 加载、五个 ToolDefinition 注册及 synthetic stdio MCP 调用可用。
- DefaultResourceLoader 通过：证明同版本 Pi Loader 能发现 extension、注册五工具并完成无模型 synthetic 调用。
- npm audit 通过：只证明当前 project017 extension 锁文件依赖图在执行时没有 npm 已知漏洞报告。

真实 synthetic 冒烟结果：

- Provider/模型：阿里云百炼 / `qwen3.7-plus-2026-05-26`。
- v2：真实派发和业务工具链已发生，但严格 inspect 参数/次数与最终报告准确性不通过；失败证据保留。
- v3：Supervisor + `live-conversion-analyst` 严格业务冒烟通过；显式调用为 `Agent ×1、inspect ×1、analyze ×1、drilldown ×0`。
- 内容增长 v1：专业子链 `inspect ×1、analyze_short_video ×1` 通过，但父级 `Agent ×2`、首次 worktree 失败和错误最终声明使严格端到端冒烟失败。
- 内容增长 v2：修复后 Profile 已生效，任务只提交一次；百炼返回 HTTP 400 `Arrearage`，没有完成模型推理，也没有 Agent 或业务工具调用，因此严格契约为 `not_evaluated`。
- v3 评估：16 项中 14 项通过、0 项失败、2 项观测差异；差异涉及父级 activity-end 聚合计数和 final reply/平台状态时序。
- v3 记录 5 次模型请求、46,599 reported tokens，估算成本为 `null/unknown`。

以上结果仍不能推出 Plugin 已启用、完整一主四专已运行、30 条评测通过、真实电商数据已接入，或 GMV、ROI、转化率、效率和成本收益成立。

## 后续运行顺序

下一阶段若继续真实运行，需要先恢复百炼账户可用状态，再重新确认范围与费用，并使用新的唯一会话名重跑内容增长；不得复用或覆盖 v2 `Arrearage` 证据。通过后再决定渠道线索、复盘策略、完整一主四专、失败恢复和 30 条正式评测；Plugin 是否导入/启用应作为独立选择，不能把当前 project-local extension 冒充 Plugin 运行证据。

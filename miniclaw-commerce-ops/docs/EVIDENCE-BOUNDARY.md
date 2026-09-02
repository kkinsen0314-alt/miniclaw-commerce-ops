# 证据边界

## 证据分层

| 标签 | 含义 | 当前状态 |
| --- | --- | --- |
| `reused_from_project015` | 代码、设计或 fixture 来自只读直播项目 | 三个白名单文件已复制并记录来源哈希；不能继承 project015 的运行结论 |
| `miniclaw_native_capability` | MiniClaw 数据库、队列、认证、Catalog、Pi Runtime 或 Subagent | 平台能力，不是个人从零研发成果 |
| `project017_static_verified` | project017 配置、Schema、源码和文档经过静态验证 | 当前静态配置为 128/128 通过 |
| `project017_synthetic_tool_verified` | 确定性工具或无模型桥接使用 synthetic 数据运行 | Python、HTTP、stdio MCP、Pi extension、Loader 和 compatibility bridge 已完成分层验证 |
| `project017_eval_infrastructure_verified` | 电商评测集、fixture、评分器和回归比较器完成离线验证 | 30/30 fixture preflight、评测执行器单元测试通过；不等于 30 条 Agent 用例通过 |
| `project017_deterministic_demo_verified` | 本地演示编排实际调用确定性工具并生成结构化报告 | 三域内置样例、synthetic 上传、结果读取和报告下载已验证；固定声明未调用 Provider/Agent Runtime |
| `project017_development_tools_discovered` | 项目级 Skill 已被 Codex 发现，可用于后续界面开发与验收 | 7/7 已发现；不属于 MiniClaw 或项目运行能力 |
| `project017_single_specialist_runtime_verified` | MiniClaw Supervisor 与一个专业子 Agent 使用真实模型运行 synthetic 冒烟 | 直播 v3 严格通过；内容增长 v1 的专业子链完成，但父级单次派发与最终报告契约失败 |
| `project017_full_multi_agent_runtime_verified` | 内容、直播、归因、策略和 Supervisor 的完整一主四专轨迹 | 尚未运行 |
| `real_business_verified` | 真实数据、真实经营指标和业务收益有测量证据 | 尚未开始 |

## 当前可以声明

- 已实现独立的电商运营统一契约、五个只读确定性工具、FastAPI 与 stdio MCP 入口。
- 已建立一主四专角色配置，Supervisor 只负责调度与校验；三个专业角色各自先 inspect，再调用本域分析和受限钻取；策略角色不加载工具。
- 已建立角色级 `ext:commerce-ops-mcp/<tool>` 白名单、未知角色拒绝、默认 Agent 禁用、嵌套禁用和计划调度禁用。
- 已实现五工具 Pi extension，并通过 Node 24 原生 TypeScript、extension harness 与同版本 Pi Loader 验证。
- 已通过 `128/128` 静态配置检查、`15/15` extension harness、`14/14` Pi `DefaultResourceLoader` 和 `25/25` compatibility bridge fail-closed 检查。
- 已编写 30 条电商评测用例和 7 个专用 fixture，并通过 30/30 fixture preflight；H09、H10、H12 语义项仍保留给人工或 Judge。
- 已在 project017 隔离运行配置中实际使用阿里云百炼与 `qwen3.7-plus-2026-05-26`，创建并运行 MiniClaw AgentSession。
- 已真实运行 Supervisor + `live-conversion-analyst` 的 synthetic 冒烟。v3 中显式业务调用为 `Agent ×1、inspect ×1、analyze_live ×1、drilldown ×0`，Supervisor 未直接调用业务工具。
- v3 strict business smoke 与最终报告准确性均通过；两个 service_run_id、analysis_run_id 和 evidence→finding 引用均可由脱敏轨迹核验。
- v2 的 inspect 参数/次数报告失败和 v3 的两项观测差异均保留，没有删改失败证据或猜测聚合计数来源。
- v3 共记录 5 次模型请求和 46,599 reported tokens；估算成本仍为 `null/unknown`。
- 已真实运行 Supervisor + `content-growth-analyst`。子 Agent 仅执行 `inspect ×1 → analyze_short_video ×1`，未钻取，业务参数、service/analysis run_id 和 evidence→finding 完整。
- 内容增长 v1 的首次 `Agent` 因错误的 worktree isolation 失败，Supervisor 随后发起第二次 `Agent`；最终回复遗漏父级失败并错误声明零失败、无重试、全部约束满足。该次只能声明“内容增长专业子链完成”，不能声明严格冒烟通过。
- 内容增长 v1 评估为 13 pass、4 fail、2 difference；6 次模型请求、65,235 reported tokens，成本为 `null/unknown`。
- 已针对该失败实现 project017 父级派发门控：Agent 描述不再推荐 worktree，带 isolation 的调用在子 Agent 创建前返回 blocked/isError，首次失败后锁住后续派发，并通过 `project017DispatchAudit` 保留父级尝试。真实 `DefaultResourceLoader` 无模型验证为 25/25，未创建 AgentSession。
- 修复后 AgentProfile 已通过官方 API 写入隔离运行数据库并核对为 version 2；四段 Prompt 哈希匹配，平台额外默认的 reasoning 字段未被误写为 authored 能力。
- 内容增长 v2 只提交一次，但首个百炼请求在模型推理前被 `Arrearage` 拒绝；没有 Agent/业务工具调用，0 reported token 不能独立证明最终账单为零。该次只能证明 Profile 已落地和单次提交保护生效，不能证明派发门控通过或失败。
- 已实现本地确定性演示编排与 FastAPI 演示接口；内置样例实际生成三域 AnalysisPacket、DrilldownResult、规则化 Action、VerificationMetric 和 DeliveryPackage。
- 演示接口明确返回 `provider_called=false` 和 `agent_runtime_executed=false`；其角色时间线证明业务分工和数据流可以组装，不证明本轮运行了 MiniClaw AgentSession。
- 已在 project017 本机安装 7 个项目级界面开发 Skill，并通过 Codex 项目发现检查；该结论只证明开发工具可被发现。

## 当前不能声明

- 已导入或启用 project017 Plugin。当前业务工具来自 project-local Pi extension，不能把 Plugin Catalog 静态资产写成运行来源。
- 已通过内容增长严格单次派发冒烟，或已完成渠道线索归因、复盘策略和完整一主四专运行。
- 修复后的内容增长真实 Agent 路由已经通过；Profile 虽已落库，但 v2 在 Provider 推理前被阻断，Agent 契约未被评估。
- v3 冒烟等同于 30 条正式评测，或已经得到 Agent 通过率和 baseline/candidate 质量结论。
- 父级 `toolUses=3` 等于三次业务工具调用；业务调用次数以子 Agent `.output` 中两个显式 assistant `toolCall` 为权威来源。
- 最终回复出现时的 `platform_status=running` 可以被改写为终态；平台状态与已观察到的最终回复必须分别保留。
- 运行时价格映射为 0 证明免费；当前真实成本未知。
- 已使用真实电商数据，或提升 GMV、ROI、转化率、运营效率、成本或用户规模。
- project015 的静态检查、评测、Loader 或隔离启动结果属于 project017。
- MiniClaw/Pi Runtime、Pi Subagent、AgentSession、宿主界面和调度底座由本人从零研发。
- 本地确定性演示中的 Supervisor/专业角色/策略角色时间线等同于真实一主四专模型运行。
- 这些项目级 Skill 已进入 MiniClaw 运行时、被 Agent 调用，或可写成本人研发的业务能力；公开 GitHub 包也不会包含 `.agents/skills`。

## 归因边界

### 本人完成

后续简历只能把 project017 中实际完成并重新验证的内容写为本人工作，例如：

- 电商业务问题拆解、一主四专职责和五工具范围。
- Workflow/Pydantic/JSON Schema、run_id 和 evidence→finding→action→verification_metric 证据链。
- Python/Pandas 确定性工具、FastAPI/stdio MCP 接入和 synthetic fixtures。
- Pi extension ToolDefinition 映射、compatibility bridge 接入、非 Git 工作区的 isolation fail-closed 门控、父子尝试账本、角色级工具范围、失败语义和静态/无模型验证资产。
- 在 MiniClaw/Pi Runtime 上完成业务配置与 synthetic 一主一子冒烟，采集并审计脱敏轨迹。

### 平台整体架构

MiniClaw 的数据库、队列、认证、Plugin Catalog、Pi Agent Runtime、Pi Subagent、AgentSession、宿主界面和基础调度工具属于平台能力。项目只能描述为“基于 MiniClaw/Pi Runtime 进行业务接入、角色约束和运行验证”，不能写成个人从零研发平台底座。

### 尚待确认

内容增长严格路由修复后的有效重跑、Plugin 导入/启用、渠道线索归因、复盘策略、完整一主四专调度、30 条真实模型评测、LLM-as-Judge、真实业务阈值、真实成本/延迟 SLO 和经营收益仍须后续确认。Provider 与模型曾用于受控 synthetic 冒烟，但当前账户状态阻断新的推理，不能写成持续可用。

## 验证结果如何解释

| 结果 | 可以证明 | 不能证明 |
| --- | --- | --- |
| 49 项 Python 测试 | 契约、服务、HTTP、stdio MCP、演示编排、synthetic 上传、报告下载和离线评测执行器符合当前测试 | Agent 或模型质量 |
| 128 项静态检查 | Prompt、父级派发门控源码、配置、角色权限、版本、观测辅助页、v2 Provider 阻断边界和文档一致 | 本轮完成了模型推理或重跑了 Agent |
| 15 项 extension harness | extension 可加载、注册五工具并调用 MCP | Supervisor 实际调用 |
| 14 项 Loader harness | 同版本 Pi Loader 可发现和加载 extension | 真实子 Agent 路由与生命周期 |
| 25 项 compatibility bridge 检查 | 平台 Subagent 调度工具可经 project-local bridge 注册，主会话不含业务工具，并会在无模型验证中拒绝 worktree、锁止二次派发和标记错误 | 内容增长真实冒烟通过或已完成一主四专运行；Profile 后续落库也不能替代 Agent 轨迹 |
| v3 脱敏轨迹与 16 项评估 | Supervisor 已实际派发一个直播专业子 Agent，严格 synthetic 业务链路通过并保留两项观测差异 | 其他角色、完整多 Agent、30-case 或真实经营效果 |
| 内容增长 v1 脱敏轨迹与 19 项评估 | 内容增长专业子 Agent 的 inspect→analyze 子链完成；父级两次 Agent 尝试、失败披露错误和两项观测差异有证据 | 内容增长严格端到端冒烟通过、其他角色、完整多 Agent 或真实经营效果 |
| npm audit 0 | 当前锁文件依赖图在执行时无 npm 已知漏洞报告 | 永久无漏洞或整个平台依赖已审计 |
| 30/30 fixture preflight | 评测集、契约引用和 fixture 可供外部运行器使用 | 30 条 Agent 用例已经执行或通过 |
| 7/7 项目 Skill 发现 | Codex 可在 project017 中定位这些界面开发辅助 Skill | 界面已经实现、MiniClaw 已加载这些 Skill，或 Agent 运行质量已提升 |

## 数据与安全边界

- Python 负责确定性清洗、计算、阈值和判断；LLM 不凭空计算经营指标。
- 无稳定关联键时输出 `missing_evidence` 或 `blocked`，不做伪归因。
- 无成本字段时不计算 ROI。
- synthetic 数据必须保留 `synthetic=true` 或等价来源标签。
- 默认只读，不写 CRM、订单、线索、工单或外部消息系统。
- 不保存或输出不必要的手机号、订单号、用户身份、Provider Key 或 Session Secret。
- 副作用不确定时停止自动重试，通过 run_id 与日志核对。
- 后续真实模型重跑必须再次得到明确授权，不因本次文档同步自动发生。
- 公开 GitHub 包排除 `.agents/skills`、本地运行数据、密钥、数据库和日志；第三方 Skill 不作为项目源代码再分发。

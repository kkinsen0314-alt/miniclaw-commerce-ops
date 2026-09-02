# MiniClaw 电商运营数据分析多 Agent 工作台

## 项目定位

本项目面向电商运营负责人、内容运营、直播运营、渠道运营和销售转化团队，将短视频、直播、账号、渠道、线索、销售跟进和订单数据组织成可追溯、可评测的经营分析工作流。

目标业务链路：

`短视频曝光 → 互动点击 → 直播承接 → 线索进入 → 销售跟进 → 订单转化 → 经营复盘`

目标 Agent 结构为“一主四专”：

- `commerce_ops_supervisor`：规范目标、生成 run_id、调度专业 Agent、校验和汇总；不直接调用业务工具。
- `content_growth_analyst`：负责短视频、内容、账号和发布时段诊断。
- `live_conversion_analyst`：负责直播观看、互动、点击、留资、下单和成交漏斗诊断。
- `attribution_lead_analyst`：负责渠道、线索来源、负责人、跟进和订单关联分析。
- `commerce_review_strategist`：只读取通过门槛的诊断包，输出行动、责任岗位、时限和复验指标。

第一版严格限制为五个只读工具：

- `inspect_commerce_data`
- `analyze_short_video_data`
- `analyze_live_commerce_data`
- `analyze_attribution_and_leads`
- `drilldown_commerce_metric`

## 当前阶段

阶段 6 已完成两个受控单域的真实 synthetic 运行：直播转化 v3 严格冒烟通过；内容增长 v1 的专业子 Agent 业务链路完成，但 Supervisor 路由与最终报告契约失败。针对该失败的 authored Prompt 和 project-local compatibility bridge 已完成无模型根因修复，修复后 Profile 已通过官方 API 写入隔离运行数据库。内容增长 v2 随后只提交一次，但百炼在模型推理前返回 `Arrearage`，因此没有产生 Agent 或业务工具调用，严格派发契约仍未被重新验证。当前证据仍只覆盖分开的“一主一子”单域运行，不代表完整“一主四专”。

当前 GitHub 预览版已经提供可独立启动的项目功能演示。页面和 API 均来自 project017，支持内置三域样例、合成表格上传、诊断域切换、证据指标、维度钻取、角色工作流、行动复验和 JSON 报告下载。该稳定演示链路执行项目内确定性工具，不替代仍在完善的 MiniClaw 原生一主四专运行链路。

阶段 5 已完成：

- 30 条用例：normal 10、boundary 6、data_missing 6、adversarial 4、refusal 4。
- 内容增长、直播转化、渠道线索归因三个专业域，以及单域、双域和一主四专完整路由。
- 重复 dataset_id、超限文件、PDF、缺点击、缺订单、缺稳定关联键和 uncertain 七类专用 fixture。
- route、terminal_status、dispatched_agents、工具调用者/参数/次数、workflow/analysis/service run_id 和完整证据链采集。
- Prompt、模型、工具说明、上下文策略版本，以及 token、估算成本、工具耗时和端到端延迟记录；未知值保持 `null`。
- H01—H12 自动/半自动检查；H09、H10、H12 语义项必须由人工或 Judge 记录，不能用关键词自动判定。
- `preflight`、`score`、`compare` 三个离线命令和单条/整轮/回归 JSON 模板。

阶段 6 当前已完成：

- 在 project017 隔离运行目录中配置阿里云百炼与 `qwen3.7-plus-2026-05-26`，创建实际 AgentProfile、Workspace 和 AgentSession；敏感配置不进入文档或 artifacts。
- 通过 project-local Pi compatibility bridge 向 Supervisor 提供平台 Subagent 调度工具；业务五工具仍由 project017 Pi extension 桥接 stdio MCP，未依赖 Plugin 导入或启用。
- v2 冒烟已真实派发 `live-conversion-analyst`，但暴露出 inspect 参数和调用次数报告问题；该次结果保留为失败证据，没有改写为通过。
- v3 严格冒烟完成 `Agent ×1 → inspect ×1 → analyze_live ×1`，Supervisor 未直接调用业务工具，专业子 Agent 保留完整 service/analysis run_id 与 evidence→finding 引用。
- v3 输入与输出均明确 `synthetic=true`，未调用 drilldown，未使用真实经营数据，也未生成经营收益结论。
- 已对父级 `toolUses` 聚合计数和“最终回复已记录但状态仍 running”的差异做只读源码审计，并修正 project017 辅助页的终态观测口径；没有为此重新调用模型。
- 内容增长 v1 已真实派发 `content-growth-analyst`；子 Agent 显式业务链路为 `inspect ×1 → analyze_short_video ×1`，参数边界、service/analysis run_id 和 evidence→finding 均通过核验。
- 内容增长 v1 的 Supervisor 首次 `Agent` 调用错误携带 `isolation=worktree` 并失败，随后发起第二次 `Agent` 调用；最终回复遗漏该失败与重试并错误声称“符合全部约束”。因此严格端到端冒烟判定为失败；页面与 Codex 没有重提整条任务。
- 已在 authored Profile 中规定非 Git 项目必须省略 isolation、父级派发失败立即 `blocked` 且不得第二次派发；兼容桥同步移除 worktree 推荐，并在上游创建子 Agent 前确定性拒绝和锁止。
- 真实 `DefaultResourceLoader` 无模型门控验证为 `25/25`：带 worktree 的第一次调用和锁止后的第二次调用均未进入上游 Agent execute，`project017DispatchAudit` 保留父级尝试，运行态 tool result 标记为 error。
- 修复后 AgentProfile 已通过 MiniClaw 官方 API 落地为 version 2；四段 Prompt 哈希与 authored 模板一致。MiniClaw 自动补入的 `reasoning.effort=inherit` 作为平台默认字段单独保留，不再被误判为模板漂移。
- 内容增长 v2 使用新的会话、workflow 和 dataset 身份只提交一次；Provider 返回 HTTP 400 `Arrearage`，reported token 为 0，未生成 Supervisor 输出、`Agent` 调用或子 Agent 工具链，页面与 Codex 均未重提任务。
- Profile 同步辅助页修复了同源模板读取的 CSP 漏项，并将运行策略核验改为“项目要求字段必须一致、平台额外默认字段允许存在”。

当前验证结果：

- `128/128` MiniClaw 静态配置检查通过。
- `15/15` Pi extension API harness 检查通过。
- `14/14` Pi `DefaultResourceLoader` 检查通过，发现 1 个 project-scoped extension、0 个加载错误。
- `25/25` MiniClaw Subagent compatibility bridge 无模型检查通过。
- extension 与 Loader harness 均对 synthetic 数据调用 7 次工具：三个角色各自 inspect，再覆盖三类分析和一次 drilldown；没有自动重试，shutdown 已关闭 transport。
- extension 依赖锁定为 Pi `0.84.2`、MCP SDK `1.30.0`、TypeBox `1.3.7`；`npm audit` 在执行时为 0 vulnerabilities。
- 30/30 用例通过 fixture preflight，无待创建或不可运行 fixture。
- Python 完整回归为 49/49 通过。
- v3 运行评估共 16 项：14 项通过、0 项失败、2 项观测差异；strict business smoke 与 final reporting accuracy 均为 `pass`。
- v3 共记录 5 次模型请求、46,599 reported tokens；成本为 `null/unknown`，不能把运行时价格映射的 0 写成免费。
- 内容增长 v1 运行评估共 19 项：13 项通过、4 项失败、2 项观测差异；专业子 Agent 业务链路为 `pass`，strict end-to-end smoke 与 final reporting accuracy 为 `fail`。
- 内容增长 v1 共记录 6 次模型请求、65,235 reported tokens；成本仍为 `null/unknown`。两次 Supervisor `Agent` 尝试、一次 inspect 和一次短视频分析均保留在脱敏轨迹中。
- 内容增长 v2 的 Provider 请求在推理前被 `Arrearage` 拒绝；评估为 12 项中 4 pass、1 blocked、6 not_evaluated、1 difference。该结果既不是 Agent 契约通过，也不是 Agent 契约失败。

## 本地功能演示

当前已新增不依赖 Provider 的本地确定性演示 API：

- `GET /`：重定向到项目功能演示页。
- `GET /demo`：加载项目功能演示页。
- `GET /v1/demo/scenarios`：读取内置全链路演示场景。
- `POST /v1/demo/runs/sample`：运行短视频、直播和渠道线索三个业务域。
- `POST /v1/demo/runs/upload`：上传声明为 synthetic 的 CSV/XLS/XLSX/XLSM 文件。
- `GET /v1/demo/runs/{workflow_run_id}`：读取当前进程缓存结果。
- `GET /v1/demo/runs/{workflow_run_id}/report`：下载结构化 JSON 报告。

演示结果包含 DatasetManifest、AnalysisPacket、Evidence、Finding、DrilldownResult、DecisionPacket、Action、VerificationMetric、DeliveryPackage 和角色工作流时间线。默认样例实际产生 3 个分析包、3 次钻取、3 条复盘动作和 12 个步骤。

该接口固定返回 `mode=deterministic_demo`、`provider_called=false`、`agent_runtime_executed=false` 和 `synthetic=true`。角色时间线用于展示业务分工与证据流，不是新的 MiniClaw AgentSession 轨迹。详细接口见 `docs/DEMO-BACKEND-v1.md`。

演示页面已完成桌面与移动端布局，支持三域切换、合成数据上传、证据卡片、维度图表、角色工作流、行动复验和 JSON 下载。页面中的角色时间线表达项目业务分工，实际运行事实仍以返回结果和脱敏 runtime artifacts 为准。

### 启动演示

```powershell
cd D:\Workspace\project017-miniclaw-commerce-ops
python -m pip install -r requirements.txt
python -m uvicorn commerce_ops.app:app --host 127.0.0.1 --port 3022
```

浏览器打开 `http://127.0.0.1:3022/demo`。依赖安装只需在首次运行或依赖变化时执行。

## 本地界面开发辅助 Skill

项目本地 `.agents/skills` 当前包含：

- `fullstack-desktop`
- `frontend-design`
- `vercel-react-best-practices`
- `typescript-pro`
- `playwright-expert`
- `electron-best-practices`
- `sql-pro`

`npx.cmd --yes skills list --agent codex` 已发现 7/7 个 Skill。它们只用于界面开发、代码质量与浏览器验收，不属于 MiniClaw 运行能力，也不能作为 Agent、Provider 或经营效果已经验证的证据。公开 GitHub 包将排除 `.agents/skills`，避免把第三方开发资产或其再分发边界带入项目交付。

## 证据边界

静态与无模型阶段已验证的是：

- project017 静态配置与锁定 MiniClaw commit 的结构一致。
- Node 原生 TypeScript 可以加载 project017 extension。
- 同版本 Pi `DefaultResourceLoader` 可以发现 extension、注册五工具，并由验证 harness 完成 synthetic stdio MCP 调用。

阶段 6 的真实 synthetic 冒烟已经证明：

- 百炼/Qwen Provider 可由隔离 MiniClaw 运行配置实际调用。
- Supervisor 可真实派发 `live-conversion-analyst`，且业务工具调用者、inspect→analyze 顺序、参数边界、次数与 run_id 链可由脱敏轨迹核验。
- v3 strict business smoke 在 synthetic 直播样例范围内通过。
- `content-growth-analyst` 已真实运行，并在 synthetic 短视频样例上完成严格的 inspect→analyze 业务子链；但 Supervisor 单次派发与完整失败披露未通过，因此不能把内容增长 v1 写成严格冒烟通过。
- 修复后的桥已在无模型加载器中证明会拒绝 worktree 并锁住二次派发；修复后 Profile 也已落库，但内容增长 v2 在模型推理前被 Provider 账户状态阻断，因此仍不等于派发门控或内容增长严格冒烟已经通过。

当前仍没有：

- 导入或启用 Plugin；当前运行使用 project-local Pi extension 与 compatibility bridge。
- 通过内容增长严格端到端冒烟；运行渠道线索归因和复盘策略角色，或完成一主四专链路。
- 用真实模型运行 30 条评测用例、形成 baseline/candidate 质量结论或验证失败恢复全集。
- 使用真实电商数据，或验证 GMV、ROI、转化率、效率、成本等经营效果。

阶段 5 新增的 preflight 和执行器测试只证明评测资产、轨迹评分和回归逻辑可运行。v3 只是一条非正式 30-case 的单专业 Agent 冒烟，因此仍没有 30 条 Agent 通过率、baseline/candidate 质量结论或真实经营效果结论。

验证 harness 调用不是 Agent 调用。MiniClaw 的数据库、队列、认证、Plugin Catalog、Pi Agent Runtime 和 Pi Subagent 属于平台能力，不能写成 project017 个人从零研发成果。

## 来源边界

- `D:\Workspace\project014-miniclaw-deployment`：MiniClaw 平台源码与运行基线，只读。
- `D:\Workspace\project015-miniclaw-live-ops`：直播业务能力、MiniClaw 适配方法和历史验证证据，只读。
- `D:\Workspace\project017-miniclaw-commerce-ops`：新电商业务实现和验证产物的唯一写入项目。

当前平台来源保持在：

`main@3ff1c8d6a0707f4a9f0957ff411758e5e141583a`

project015 的检查、Loader、隔离启动和 Agent 评测资产不能直接写成 project017 已验证。

## 目录

```text
project017-miniclaw-commerce-ops/
├── .agents/        # 本机项目级开发 Skill；公开包排除
├── .pi/            # Subagent 配置、角色文件和 project017 Pi extension
├── artifacts/      # project017 重新生成的机器可读验证证据
├── commerce_ops/   # 电商运营确定性能力与适配层
├── config/         # 未写入数据库的 Profile/Workspace 请求模板
├── contracts/      # Workflow JSON Schema 与合成样例
├── data/           # synthetic fixtures；不放真实敏感业务数据
├── docs/           # Agent、工具、MiniClaw 接入和证据边界
├── evals/          # 30 条用例、fixture、评分规则和记录模板
├── integrations/   # 未导入、未启用的 Plugin/MCP 静态目录
├── runtime/        # 后续隔离运行目录；不得复制旧数据库和 Secret
├── scripts/        # 静态验证器
├── tests/          # project017 Python 测试
└── web/            # 本地功能演示页面、样式和交互
```

## 本地验证

```powershell
cd D:\Workspace\project017-miniclaw-commerce-ops
python -B scripts\verify-miniclaw-static-config.py --output artifacts\miniclaw-static-config-v5.json
node scripts\verify-miniclaw-subagent-bridge.mjs --output artifacts\miniclaw-subagent-bridge-validation-v2.json
python -B -m commerce_ops.tool_validation
python -B scripts\run-commerce-ops-evals.py preflight
python -B -m unittest discover -s tests -p "test_*.py" -v

cd .pi\extensions\commerce-ops-mcp
node validate-runtime.mjs --output ..\..\..\artifacts\pi-extension-runtime-v2.json
node validate-pi-resource-loader.mjs --output ..\..\..\artifacts\pi-default-resource-loader-v2.json
npm.cmd audit --json
```

上述 Python、Node 和静态验证命令本身只使用本项目 synthetic fixtures，不配置 Provider、不调用模型、不运行 Agent。真实模型冒烟已有独立脱敏 artifacts，后续重跑必须再次获得明确授权。

## 下一阶段

当前项目功能演示已经可独立启动。下一阶段先准备“第 13 期课程”跨表合成演示数据，再把页面运行入口逐步接入 MiniClaw 原生 Supervisor 与四个专业子 Agent，同时保留现有确定性链路作为稳定功能演示和故障隔离路径。

真实模型方向仍需先恢复百炼账户可用状态，再获得新的运行授权并使用全新会话身份执行内容增长；不能复用或覆盖本次 `Arrearage` 证据。通过后再运行渠道线索、复盘策略和完整一主四专链路，最后补充失败恢复与 30 条真实模型轨迹基线。

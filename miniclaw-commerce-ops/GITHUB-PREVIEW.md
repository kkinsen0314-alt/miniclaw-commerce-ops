# GitHub 预览版说明

## 版本定位

本压缩包是 MiniClaw 电商运营数据分析多 Agent 工作台的阶段性公开预览版，打包文件名为：

`miniclaw-commerce-ops-github-preview-2026-09-01.zip`

当前可以独立启动 project017 的本地功能演示，使用项目内合成数据或上传的合成表格完成三域确定性分析、证据展示、维度钻取、行动复验和 JSON 报告下载。

## 已包含

- `commerce_ops/`：FastAPI、Pandas、Pydantic 数据检查与经营分析能力。
- `web/`：项目功能演示页面、样式与交互。
- `.pi/`：一主四专角色配置、项目级 Pi extension 与 Subagent compatibility bridge 源码。
- `config/`、`contracts/`、`integrations/`：不含密钥的配置模板、Workflow 契约和静态接入资产。
- `data/fixtures/`：合成测试数据。
- `evals/`、`tests/`、`scripts/`：评测集、回归测试和验证脚本。
- `docs/`：架构、工具、证据边界与当前状态说明。
- 公开架构、接入与证据边界文档；原始运行材料不进入本预览包。

## 已排除

- Provider Key、Session Secret、`.env` 和其他凭据。
- MiniClaw 数据库、Session、运行日志、IPC 状态和本机运行数据。
- `node_modules`、Python 缓存、临时上传文件和其他可重新生成的依赖产物。
- `.agents/skills` 与 `skills-lock.json`；这些是开发辅助资产，不属于项目运行能力。
- 原始 artifacts、运行轨迹、Session 标识和内部验收快照。
- 旧标题截图和未筛选的内部迁移材料。
- project014/project015 正本、MiniClaw upstream 源码和任何真实敏感业务数据。

## 当前边界

- 直播转化已经完成一条真实模型“一主一子”synthetic 严格冒烟。
- 内容增长专业子链已经真实运行，但修复后的严格端到端链路仍被 Provider 账户状态阻断。
- 渠道归因、复盘策略和完整一主四专原生运行尚未完成。
- 本地 `/demo` 是 project017 的稳定业务功能演示入口，不是 MiniClaw 平台全部管理功能的镜像。
- 合成数据、静态检查、验证 harness 和局部 Agent 冒烟均不能作为真实经营效果证明。

## 本地启动

```powershell
python -m pip install -r requirements.txt
python -m uvicorn commerce_ops.app:app --host 127.0.0.1 --port 3022
```

浏览器打开 `http://127.0.0.1:3022/demo`。

## 验证

```powershell
python -B -m unittest discover -s tests -p "test_*.py" -v
node --check web\app.js
python -B scripts\run-commerce-ops-evals.py preflight
```

2026-09-02 打包前，Python 完整回归为 49/49，JavaScript 语法检查通过。

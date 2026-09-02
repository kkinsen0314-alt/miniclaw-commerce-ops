from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
from typing import Any


PLATFORM_COMMIT = "3ff1c8d6a0707f4a9f0957ff411758e5e141583a"
PLATFORM_ROOT = Path(
    "D:/Workspace/project014-miniclaw-deployment/upstream/miniclaw"
)
EXTENSION_NAME = "commerce-ops-mcp"
EXTENSION_PATH = (
    "D:/Workspace/project017-miniclaw-commerce-ops/"
    ".pi/extensions/commerce-ops-mcp/index.ts"
)
PI_TOOLS = {
    "commerce_ops_inspect_commerce_data",
    "commerce_ops_analyze_short_video_data",
    "commerce_ops_analyze_live_commerce_data",
    "commerce_ops_analyze_attribution_and_leads",
    "commerce_ops_drilldown_commerce_metric",
}
ROLE_TOOL_SCOPES = {
    "content-growth-analyst.md": {
        "commerce_ops_inspect_commerce_data",
        "commerce_ops_analyze_short_video_data",
        "commerce_ops_drilldown_commerce_metric",
    },
    "live-conversion-analyst.md": {
        "commerce_ops_inspect_commerce_data",
        "commerce_ops_analyze_live_commerce_data",
        "commerce_ops_drilldown_commerce_metric",
    },
    "attribution-lead-analyst.md": {
        "commerce_ops_inspect_commerce_data",
        "commerce_ops_analyze_attribution_and_leads",
        "commerce_ops_drilldown_commerce_metric",
    },
}
ROLE_CALLERS = {
    "content-growth-analyst.md": "content_growth_analyst",
    "live-conversion-analyst.md": "live_conversion_analyst",
    "attribution-lead-analyst.md": "attribution_lead_analyst",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} 缺少 YAML frontmatter")
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ValueError(f"{path} frontmatter 未闭合") from exc
    values: dict[str, Any] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, raw_value = line.partition(":")
        if not separator:
            raise ValueError(f"{path} frontmatter 行无法解析：{line}")
        value = raw_value.strip()
        if value.startswith(("\"", "[")):
            values[key.strip()] = json.loads(value)
        elif value in {"true", "false"}:
            values[key.strip()] = value == "true"
        elif value.isdigit():
            values[key.strip()] = int(value)
        else:
            values[key.strip()] = value
    return values, "\n".join(lines[end + 1 :]).strip()


def split_tool_scope(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(PLATFORM_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def validate(project_root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "pass" if condition else "fail",
                "detail": detail,
            }
        )

    expected_files = [
        ".pi/agents/attribution-lead-analyst.md",
        ".pi/agents/commerce-review-strategist.md",
        ".pi/agents/content-growth-analyst.md",
        ".pi/agents/live-conversion-analyst.md",
        ".pi/extensions/commerce-ops-mcp/index.ts",
        ".pi/extensions/commerce-ops-mcp/package-lock.json",
        ".pi/extensions/commerce-ops-mcp/package.json",
        ".pi/extensions/commerce-ops-mcp/validate-pi-resource-loader.mjs",
        ".pi/extensions/commerce-ops-mcp/validate-runtime.mjs",
        ".pi/extensions/commerce-ops-mcp/validation-shared.mjs",
        ".pi/extensions/miniclaw-subagents-bridge/index.ts",
        ".pi/subagents.json",
        "config/agent-profile-create.template.json",
        "config/workspace-create.template.json",
        "docs/AGENT-SPEC-v2.md",
        "docs/EVIDENCE-BOUNDARY.md",
        "docs/MINICLAW-INTEGRATION-v2.md",
        "docs/RUNTIME-OBSERVABILITY-v1.md",
        "docs/TOOL-CONTRACTS-v1.md",
        "integrations/miniclaw-plugin-marketplace/.claude-plugin/marketplace.json",
        "integrations/miniclaw-plugin-marketplace/plugins/commerce-ops/.claude-plugin/plugin.json",
        "integrations/miniclaw-plugin-marketplace/plugins/commerce-ops/.mcp.json",
        "artifacts/runtime/smoke-content-v2-dispatch-guard-redacted-trace.json",
        "artifacts/runtime/smoke-content-v2-dispatch-guard-assessment.json",
        "runtime/setup-helper/index.html",
        "runtime/setup-helper/serve.mjs",
        "runtime/setup-helper/smoke-content.html",
        "runtime/setup-helper/smoke.html",
        "scripts/verify-miniclaw-subagent-bridge.mjs",
    ]
    for relative in expected_files:
        check(
            f"file:{relative}",
            (project_root / relative).is_file(),
            "required phase-4 static asset exists",
        )

    profile = load_json(project_root / "config/agent-profile-create.template.json")
    check(
        "profile:schema-v2",
        profile.get("prompt_schema_version") == 2,
        "four-part prompt schema is explicit",
    )
    check(
        "profile:append-mode",
        profile.get("prompt_mode") == "append",
        "MiniClaw preset remains enabled",
    )
    check(
        "profile:preset-compatible",
        profile.get("include_claude_preset") is True,
        "append mode and preset flag are compatible",
    )
    check(
        "profile:provider-placeholder",
        profile.get("model_config_id") is None,
        "authored template does not embed the isolated runtime Provider ID",
    )
    check(
        "profile:four-prompts",
        all(
            profile.get(key)
            for key in (
                "identity_prompt",
                "soul_prompt",
                "agents_prompt",
                "tools_prompt",
            )
        ),
        "all four prompt sections are non-empty",
    )
    runtime_policy = profile.get("runtime_policy", {})
    check(
        "profile:managed-context",
        runtime_policy.get("context", {}).get("source") == "managed",
        "host Claude context is not inherited",
    )
    check(
        "profile:skills-disabled",
        runtime_policy.get("skills", {}).get("mode") == "disabled"
        and runtime_policy.get("skills", {}).get("ids") == []
        and runtime_policy.get("skills", {}).get("host", {}).get("mode")
        == "disabled"
        and runtime_policy.get("skills", {}).get("host", {}).get("ids") == [],
        "Profile does not import user or host skills",
    )
    check(
        "profile:mcp-disabled",
        runtime_policy.get("mcp", {}).get("mode") == "disabled"
        and runtime_policy.get("mcp", {}).get("ids") == [],
        "Plugin MCP is not selected as a Supervisor capability",
    )
    agents_prompt = profile.get("agents_prompt", "")
    tools_prompt = profile.get("tools_prompt", "")
    check(
        "profile:supervisor-dispatch-only",
        all(
            token in tools_prompt
            for token in (
                "Agent",
                "get_subagent_result",
                "steer_subagent",
                "不直接调用 commerce_ops",
            )
        ),
        "Supervisor prompt limits work to subagent dispatch and forbids direct business tools",
    )
    check(
        "profile:tool-attempt-audit",
        all(
            token in agents_prompt + tools_prompt
            for token in (
                "所有工具尝试",
                "Schema 参数校验失败",
                "全部 service_run_id",
                "不得报告 completed/pass",
                "成功调用数不能冒充总尝试数",
            )
        ),
        "Supervisor audits failed attempts, total attempts, and every available service run ID",
    )
    check(
        "profile:non-git-isolation-policy",
        all(
            token in agents_prompt
            for token in (
                "本项目不是 Git 仓库",
                "必须完全省略 isolation 参数",
                '禁止传 isolation="worktree"',
            )
        ),
        "Supervisor must omit worktree isolation for the non-Git project017 workspace",
    )
    check(
        "profile:parent-dispatch-fail-closed",
        all(
            token in agents_prompt + tools_prompt
            for token in (
                "父级 Agent 工具尝试",
                "当前分支立即 blocked",
                "不得再次调用 Agent",
                "父级 Agent 派发尝试与子级业务工具尝试",
            )
        ),
        "a parent dispatch failure blocks the branch and the final ledger merges parent and child attempts",
    )

    workspace = load_json(project_root / "config/workspace-create.template.json")
    check(
        "workspace:host",
        workspace.get("execution_mode") == "host",
        "Windows project path uses host execution",
    )
    check(
        "workspace:assistant",
        workspace.get("interaction_mode") == "assistant",
        "Workspace remains manually initiated",
    )
    check(
        "workspace:cwd",
        workspace.get("custom_cwd") == str(project_root),
        "custom cwd points to project017",
    )
    check(
        "workspace:profile-placeholder",
        workspace.get("agent_profile_id")
        == "REPLACE_WITH_CREATED_AGENT_PROFILE_ID",
        "database ID is not fabricated",
    )

    subagents = load_json(project_root / ".pi/subagents.json")
    check(
        "subagents:strict-files",
        subagents.get("strictAgentFiles") is True,
        "broken custom agent files fail startup",
    )
    check(
        "subagents:no-fallback",
        subagents.get("fallbackSubagent") == "none",
        "unknown roles fail closed",
    )
    check(
        "subagents:no-defaults",
        subagents.get("disableDefaultAgents") is True,
        "default full-tool roles are disabled",
    )
    check(
        "subagents:no-nesting",
        subagents.get("maxSubagentDepth") == 1,
        "specialists cannot create nested children",
    )
    check(
        "subagents:no-scheduling",
        subagents.get("schedulingEnabled") is False,
        "scheduled subagent runs remain disabled",
    )
    check(
        "subagents:foreground",
        subagents.get("widgetMode") == "background",
        "widget preference does not authorize background execution",
    )

    for filename, allowed_tools in ROLE_TOOL_SCOPES.items():
        meta, body = parse_frontmatter(project_root / ".pi/agents" / filename)
        actual_tools = split_tool_scope(str(meta.get("tools", "")))
        expected_tools = {"none"} | {
            f"ext:{EXTENSION_NAME}/{name}" for name in allowed_tools
        }
        denied_tools = split_tool_scope(str(meta.get("disallowed_tools", "")))
        other_domain_tools = PI_TOOLS - allowed_tools
        role_id = filename.removesuffix(".md")
        check(
            f"agent:{role_id}:tool-scope",
            actual_tools == expected_tools,
            "only the role-local inspect, domain analysis, and drilldown tools are exposed",
        )
        check(
            f"agent:{role_id}:extension-path",
            meta.get("extensions") == [EXTENSION_PATH],
            "role loads the project017 extension by explicit path",
        )
        check(
            f"agent:{role_id}:deny-scope",
            {"bash", "powershell", "write", "edit"}.issubset(denied_tools)
            and other_domain_tools.issubset(denied_tools),
            "write tools and other-domain analysis tools are denied",
        )
        check(
            f"agent:{role_id}:no-nesting",
            meta.get("allowed_subagents") == "none",
            "specialist cannot delegate",
        )
        check(
            f"agent:{role_id}:no-context-inheritance",
            meta.get("inherit_context") is False,
            "only the explicit task packet enters the child",
        )
        check(
            f"agent:{role_id}:prompt-replace",
            meta.get("prompt_mode") == "replace",
            "specialist prompt does not inherit the Supervisor system prompt",
        )
        caller = ROLE_CALLERS[filename]
        check(
            f"agent:{role_id}:inspect-first",
            ("先且只调用一次" in body or "先且只允许一次" in body)
            and "commerce_ops_inspect_commerce_data" in body
            and caller in body,
            "role-local MCP state is established before domain analysis",
        )
        check(
            f"agent:{role_id}:inspect-parameter-boundary",
            all(
                token in body
                for token in (
                    "workflow_run_id`、`caller_role`、`data_refs`、`requested_domains",
                    "根对象不得传 `synthetic`",
                    "`synthetic=true` 只能放在每个 `data_refs[]` 项内",
                )
            ),
            "inspect root fields and nested synthetic placement are explicit",
        )
        check(
            f"agent:{role_id}:inspect-validation-stop",
            all(
                token in body
                for token in (
                    "Schema 参数校验失败也计为一次 inspect 尝试",
                    "停止当前分支并返回 `blocked`",
                    "不得主动发起第二次 inspect",
                )
            ),
            "a schema validation failure consumes the only inspect attempt and stops the branch",
        )
        check(
            f"agent:{role_id}:attempt-reporting",
            all(
                token in body
                for token in (
                    "所有工具尝试（含失败尝试）",
                    "总尝试次数",
                    "全部 `service_run_id`",
                    "`analysis_run_id`",
                    "transport 自动重试与模型主动重新调用必须分开记录",
                )
            ),
            "specialist output retains failures, counts, transport distinction, and all run IDs",
        )
        check(
            f"agent:{role_id}:failure-boundary",
            all(token in body for token in ("partial", "blocked", "uncertain"))
            and "禁止自动重试" in body,
            "degraded states and no-blind-retry behavior are explicit",
        )

    review_meta, review_body = parse_frontmatter(
        project_root / ".pi/agents/commerce-review-strategist.md"
    )
    check(
        "agent:review:no-tools",
        review_meta.get("tools") == "none",
        "review role has no built-in or business tools",
    )
    check(
        "agent:review:no-extensions",
        review_meta.get("extensions") is False,
        "review role loads no extension",
    )
    check(
        "agent:review:no-nesting",
        review_meta.get("allowed_subagents") == "none",
        "review role cannot delegate",
    )
    check(
        "agent:review:action-chain",
        all(
            token in review_body
            for token in (
                "finding_refs",
                "evidence_refs",
                "owner_role",
                "verification_metric",
                "guardrails",
            )
        ),
        "review actions retain responsibility, evidence, verification, and guardrails",
    )

    marketplace = load_json(
        project_root
        / "integrations/miniclaw-plugin-marketplace/.claude-plugin/marketplace.json"
    )
    plugin = load_json(
        project_root
        / "integrations/miniclaw-plugin-marketplace/plugins/commerce-ops/.claude-plugin/plugin.json"
    )
    mcp = load_json(
        project_root
        / "integrations/miniclaw-plugin-marketplace/plugins/commerce-ops/.mcp.json"
    )
    check(
        "plugin:marketplace-name",
        marketplace.get("name") == "project017-commerce-ops",
        "Catalog marketplace is project-scoped",
    )
    check(
        "plugin:single-source",
        marketplace.get("plugins")
        == [
            {
                "name": "commerce-ops",
                "source": "./plugins/commerce-ops",
                "description": "数据检查、短视频、直播、渠道线索和受限钻取 MCP 声明。",
            }
        ],
        "marketplace declares one local Plugin source",
    )
    check(
        "plugin:manifest-name",
        plugin.get("name") == "commerce-ops",
        "Plugin directory and manifest names match",
    )
    server = mcp.get("commerce_ops", {})
    check(
        "plugin:mcp-command",
        server.get("command") == "python"
        and server.get("args") == ["-B", "-m", "commerce_ops.mcp_server"],
        "Plugin declares the project017 stdio MCP Server",
    )
    check(
        "plugin:mcp-cwd",
        server.get("cwd") == str(project_root),
        "stdio cwd points to project017",
    )
    check(
        "plugin:data-root",
        server.get("env", {}).get("COMMERCE_OPS_DATA_ROOT")
        == str(project_root / "data/fixtures"),
        "MCP input is limited to project017 synthetic fixtures",
    )

    package = load_json(project_root / ".pi/extensions/commerce-ops-mcp/package.json")
    package_lock = load_json(
        project_root / ".pi/extensions/commerce-ops-mcp/package-lock.json"
    )
    lock_packages = package_lock.get("packages", {})
    check(
        "extension:pi-host-pin",
        package.get("dependencies", {}).get("@earendil-works/pi-coding-agent")
        == "0.84.2"
        and lock_packages.get(
            "node_modules/@earendil-works/pi-coding-agent", {}
        ).get("version")
        == "0.84.2",
        "Pi host package is declared and locked to 0.84.2",
    )
    check(
        "extension:sdk-pin",
        package.get("dependencies", {}).get("@modelcontextprotocol/sdk")
        == "1.30.0"
        and lock_packages.get("node_modules/@modelcontextprotocol/sdk", {}).get(
            "version"
        )
        == "1.30.0",
        "MCP SDK is declared and locked to 1.30.0",
    )
    check(
        "extension:typebox-pin",
        package.get("dependencies", {}).get("typebox") == "1.3.7"
        and lock_packages.get("node_modules/typebox", {}).get("version")
        == "1.3.7",
        "TypeBox is declared and locked to the MiniClaw version",
    )
    extension_source = (
        project_root / ".pi/extensions/commerce-ops-mcp/index.ts"
    ).read_text(encoding="utf-8")
    registered = set(
        re.findall(r'name:\s*"(commerce_ops_[a-z_]+)"', extension_source)
    )
    check(
        "extension:five-tools",
        registered == PI_TOOLS,
        "Pi extension registers exactly the five contracted tools",
    )
    check(
        "extension:stdio-client",
        "StdioClientTransport" in extension_source
        and "Client" in extension_source,
        "official MCP client and stdio transport are used",
    )
    check(
        "extension:role-local-state",
        "let activeClient" in extension_source
        and "let activeTransport" in extension_source,
        "each extension instance owns one MCP client and transport",
    )
    check(
        "extension:synthetic-only",
        extension_source.count("synthetic: true") >= 5,
        "all five Pi-to-MCP mappings force synthetic execution",
    )
    check(
        "extension:no-retry",
        "automaticRetry: false" in extension_source,
        "tool details declare no automatic retry",
    )
    check(
        "extension:inspect-parameter-description",
        all(
            token in extension_source
            for token in (
                "根对象仅允许 workflow_run_id、caller_role、data_refs、requested_domains 和可选 max_rows_for_profile",
                "根对象不得传 synthetic",
                "synthetic=true 只能放在每个 data_refs[] 项内",
                "Schema 参数校验失败也计为一次工具尝试",
                "禁止用第二次调用隐藏失败尝试",
            )
        ),
        "inspect tool description exposes the strict root argument and attempt-count contract",
    )
    check(
        "extension:shutdown",
        'pi.on("session_shutdown"' in extension_source,
        "stdio transport cleanup is registered",
    )

    bridge_source = (
        project_root / ".pi/extensions/miniclaw-subagents-bridge/index.ts"
    ).read_text(encoding="utf-8")
    check(
        "bridge:pinned-upstream-delegation",
        PLATFORM_COMMIT in bridge_source
        and "@tintinweb/pi-subagents/dist/index.js" in bridge_source
        and "new Proxy(pi" in bridge_source
        and 'property === "registerTool"' in bridge_source,
        "project-local bridge delegates to the pinned compiled extension through a minimal registration proxy",
    )
    check(
        "bridge:isolation-fail-closed",
        all(
            token in bridge_source
            for token in (
                "PROJECT017_AGENT_DISPATCH_POLICY",
                "project017_agent_dispatch_fail_closed_v1",
                'hasOwnProperty.call(params, "isolation")',
                "isolation_argument_forbidden_in_non_git_project",
                "previous_agent_dispatch_blocked",
                "project017DispatchAudit",
                'pi.on("tool_call"',
                'pi.on("tool_result"',
                "isError: true",
            )
        ),
        "bridge blocks forbidden isolation, locks later dispatch, and preserves a parent-attempt audit payload",
    )
    check(
        "bridge:no-spawn-source-copy",
        len(bridge_source) < 12000
        and "createAgentSession" not in bridge_source
        and "manager.spawn" not in bridge_source
        and "spawnAndWait" not in bridge_source,
        "bridge does not copy the upstream AgentSession or spawn implementation",
    )

    platform_package = load_json(PLATFORM_ROOT / "package.json")
    runner_package = load_json(PLATFORM_ROOT / "container/agent-runner/package.json")
    platform_head = git_output("rev-parse", "HEAD")
    platform_status = git_output("status", "--short")
    check(
        "platform:commit",
        platform_head == PLATFORM_COMMIT,
        "read-only MiniClaw source remains at the declared commit",
    )
    check(
        "platform:clean",
        platform_status == "",
        "read-only MiniClaw source worktree remains clean",
    )
    check(
        "platform:pi-version",
        platform_package.get("dependencies", {}).get(
            "@earendil-works/pi-coding-agent"
        )
        == "0.84.2",
        "project017 Pi host pin matches the MiniClaw source",
    )
    check(
        "platform:subagents-version",
        runner_package.get("dependencies", {}).get("@tintinweb/pi-subagents")
        == "0.16.1",
        "frontmatter targets MiniClaw's pi-subagents 0.16.1 contract",
    )
    check(
        "platform:typebox-version",
        runner_package.get("dependencies", {}).get("typebox") == "1.3.7",
        "project017 schema dependency matches the MiniClaw runner",
    )
    pi_runtime_source = (
        PLATFORM_ROOT / "container/agent-runner/src/runtime/pi/pi-runtime.ts"
    ).read_text(encoding="utf-8")
    pi_index_source = (
        PLATFORM_ROOT / "container/agent-runner/src/pi-index.ts"
    ).read_text(encoding="utf-8")
    check(
        "platform:supervisor-extension-filter",
        "const selectedTools = options.allowedTools" in pi_runtime_source
        and "allowedTools: DEFAULT_ALLOWED_TOOLS" in pi_index_source
        and "commerce_ops_" not in pi_index_source,
        "MiniClaw source selects main-session tools without project017 business names",
    )

    subagent_manager_source = (
        PLATFORM_ROOT
        / "container/agent-runner/node_modules/@tintinweb/pi-subagents/src/agent-manager.ts"
    ).read_text(encoding="utf-8")
    subagent_runner_source = (
        PLATFORM_ROOT
        / "container/agent-runner/node_modules/@tintinweb/pi-subagents/src/agent-runner.ts"
    ).read_text(encoding="utf-8")
    platform_index_source = (PLATFORM_ROOT / "src/index.ts").read_text(
        encoding="utf-8"
    )
    check(
        "platform:tool-uses-activity-aggregate",
        subagent_manager_source.count(
            'if (activity.type === "end") record.toolUses++;'
        )
        >= 3
        and "tool_execution_end" in subagent_runner_source
        and "extension-error:" in subagent_runner_source,
        "pi-subagents toolUses counts activity-end events, including non-tool extension activity",
    )
    check(
        "platform:conversation-agent-idle-settlement",
        "updateAgentStatus(agentId, 'running');" in platform_index_source
        and "agent.kind === 'spawn' ? (hadError ? 'error' : 'completed') : 'idle'"
        in platform_index_source,
        "persistent conversation agents settle from running to idle in finally",
    )

    smoke_source = (
        project_root / "runtime/setup-helper/smoke.html"
    ).read_text(encoding="utf-8")
    check(
        "smoke:v3-unique-identity",
        all(
            token in smoke_source
            for token in (
                "运行验收-直播转化-v3-参数边界",
                "wf_runtime_smoke_live_v3_contract",
                "ds_live_runtime_smoke_v3_contract",
            )
        ),
        "third smoke uses unique session, workflow, and dataset identities",
    )
    check(
        "smoke:v3-attempt-contract",
        all(
            token in smoke_source
            for token in (
                "根对象禁止 synthetic",
                "Schema 参数校验失败也算一次 inspect 尝试",
                "禁止主动第二次调用 inspect",
                "失败尝试计入总次数",
                "全部 service_run_id",
            )
        ),
        "third smoke repeats the strict inspect boundary because the live Profile template is not applied",
    )
    check(
        "smoke:lifecycle-separation",
        all(
            token in smoke_source
            for token in (
                "platform_status=",
                "observed_execution_state=",
                "lifecycle_difference=",
                "不能互相改写",
            )
        ),
        "platform lifecycle and observed final reply state remain separate",
    )
    check(
        "smoke:lifecycle-settlement-grace",
        all(
            token in smoke_source
            for token in (
                "FINAL_REPLY_SETTLE_GRACE_MS = 20_000",
                "'idle'",
                "settlementGraceExpired",
                "platform_settled_after_final_reply",
                "正在只读等待平台状态",
            )
        ),
        "helper observes conversation-agent idle settlement before recording a lifecycle difference",
    )

    content_smoke_source = (
        project_root / "runtime/setup-helper/smoke-content.html"
    ).read_text(encoding="utf-8")
    check(
        "smoke:content-v2-unique-identity",
        all(
            token in content_smoke_source
            for token in (
                "运行验收-内容增长-v2-派发门控修复",
                "wf_runtime_smoke_content_v2_dispatch_guard",
                "ds_content_runtime_smoke_v2_dispatch_guard",
            )
        ),
        "post-fix content smoke uses a unique session, workflow, and dataset identity",
    )
    check(
        "smoke:content-v2-runtime-profile-guard",
        all(
            token in content_smoke_source
            for token in (
                "必须完全省略 isolation 参数",
                "不得再次调用 Agent",
                "project017 兼容桥",
                "qwen3.7-plus-2026-05-26",
            )
        ),
        "content smoke refuses submission unless the repaired Profile and authorized model are active",
    )
    check(
        "smoke:content-v2-single-submission-lock",
        all(
            token in content_smoke_source
            for token in (
                "miniclaw-content-smoke-v2-dispatch-guard-submission-started",
                "同名冒烟会话已存在且包含消息",
                "为避免不确定结果下重复计费",
                "不会自动重试",
            )
        ),
        "content smoke prevents task resubmission after a started or uncertain run",
    )

    setup_index_source = (
        project_root / "runtime/setup-helper/index.html"
    ).read_text(encoding="utf-8")
    setup_serve_source = (
        project_root / "runtime/setup-helper/serve.mjs"
    ).read_text(encoding="utf-8")
    check(
        "setup-helper:csp-allows-self-template",
        "connect-src 'self' http://127.0.0.1:3017" in setup_serve_source,
        "the setup helper can fetch its same-origin authored template and the local MiniClaw API",
    )
    check(
        "setup-helper:runtime-policy-subset-verification",
        all(
            token in setup_index_source
            for token in (
                "function isDeepSubset",
                "Object.entries(expected).every",
                "!isDeepSubset(existing.runtime_policy || null, expected.runtime_policy || null)",
            )
        ),
        "Profile verification requires authored policy fields while allowing platform-added defaults",
    )

    content_v2_trace = load_json(
        project_root
        / "artifacts/runtime/smoke-content-v2-dispatch-guard-redacted-trace.json"
    )
    content_v2_assessment = load_json(
        project_root
        / "artifacts/runtime/smoke-content-v2-dispatch-guard-assessment.json"
    )
    check(
        "runtime-evidence:content-v2-provider-block-boundary",
        content_v2_trace.get("result", {}).get("terminal_status_from_sdk_trace")
        == "blocked_provider_arrearage"
        and content_v2_trace.get("route", {}).get("supervisor_agent_tool_attempts")
        == 0
        and content_v2_assessment.get("overall_verdict")
        == "not_evaluated_provider_arrearage",
        "provider rejection is preserved separately from Agent routing and contract results",
    )

    integration_doc = (
        project_root / "docs/MINICLAW-INTEGRATION-v2.md"
    ).read_text(encoding="utf-8")
    evidence_doc = (
        project_root / "docs/EVIDENCE-BOUNDARY.md"
    ).read_text(encoding="utf-8")
    runtime_observability_doc = (
        project_root / "docs/RUNTIME-OBSERVABILITY-v1.md"
    ).read_text(encoding="utf-8")
    check(
        "docs:integration-boundary",
        all(
            token in integration_doc
            for token in (
                "Provider configured in isolated runtime: `true`",
                "Plugin imported: `false`",
                "AgentSession executed: `true`",
                "Supervisor plus one specialist executed: `true`",
                "Full one-main-four-specialist workflow executed: `false`",
                "静态/无模型 harness",
            )
        ),
        "integration guide separates harness, single-specialist runtime, and full-workflow evidence",
    )
    check(
        "docs:ownership-boundary",
        all(
            token in evidence_doc
            for token in ("本人完成", "平台整体架构", "尚待确认")
        ),
        "resume ownership categories remain explicit",
    )
    check(
        "docs:runtime-observability-authority",
        all(
            token in runtime_observability_doc
            for token in (
                "activity-end 聚合值",
                "显式 `toolCall`",
                "正常回收状态是 idle",
                "最多等待 20 秒",
                "不互相改写",
            )
        ),
        "runtime evidence uses explicit child calls and recognizes idle settlement",
    )

    failed = [item for item in checks if item["status"] == "fail"]
    return {
        "schema_version": "1.0",
        "validation_kind": "project017_miniclaw_static_configuration",
        "status": "pass" if not failed else "fail",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "source_platform_root": str(PLATFORM_ROOT),
        "source_platform_commit": PLATFORM_COMMIT,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
        "evidence_boundary": {
            "scope_note": "These fields describe actions performed by this static validator, not the total runtime state of project017.",
            "static_validation_only": True,
            "provider_configured_by_this_validator": False,
            "plugin_imported_by_this_validator": False,
            "plugin_enabled_by_this_validator": False,
            "database_written_by_this_validator": False,
            "agent_session_created_by_this_validator": False,
            "agent_executed_by_this_validator": False,
            "model_called_by_this_validator": False,
            "runtime_evidence_reexecuted_by_this_validator": False,
            "real_business_data_used_by_this_validator": False,
            "real_business_outcome_claimed_by_this_validator": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    report = validate(project_root)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    raise SystemExit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()

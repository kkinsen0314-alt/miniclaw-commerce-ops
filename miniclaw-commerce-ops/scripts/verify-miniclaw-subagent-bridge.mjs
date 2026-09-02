import { execFileSync } from "node:child_process";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT_ROOT = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(SCRIPT_ROOT, "..");
const PLATFORM_ROOT =
  "D:/Workspace/project014-miniclaw-deployment/upstream/miniclaw";
const PLATFORM_COMMIT = "3ff1c8d6a0707f4a9f0957ff411758e5e141583a";
const SUBAGENTS_VERSION = "0.16.1";
const PI_HOST_VERSION = "0.84.2";
const BRIDGE_ENTRY = path.join(
  PROJECT_ROOT,
  ".pi",
  "extensions",
  "miniclaw-subagents-bridge",
  "index.ts",
);
const BUSINESS_ENTRY = path.join(
  PROJECT_ROOT,
  ".pi",
  "extensions",
  "commerce-ops-mcp",
  "index.ts",
);
const PI_HOST_ENTRY = path.join(
  PROJECT_ROOT,
  ".pi",
  "extensions",
  "commerce-ops-mcp",
  "node_modules",
  "@earendil-works",
  "pi-coding-agent",
  "dist",
  "index.js",
);
const PI_RUNTIME_SOURCE = path.join(
  PLATFORM_ROOT,
  "container",
  "agent-runner",
  "src",
  "runtime",
  "pi",
  "pi-runtime.ts",
);
const PI_INDEX_SOURCE = path.join(
  PLATFORM_ROOT,
  "container",
  "agent-runner",
  "src",
  "pi-index.ts",
);
const SUBAGENTS_ROOT = path.join(
  PLATFORM_ROOT,
  "container",
  "agent-runner",
  "node_modules",
  "@tintinweb",
  "pi-subagents",
);
const SUBAGENTS_PACKAGE = path.join(SUBAGENTS_ROOT, "package.json");
const SUBAGENTS_ENTRY = path.join(SUBAGENTS_ROOT, "dist", "index.js");
const CUSTOM_AGENTS_ENTRY = path.join(
  SUBAGENTS_ROOT,
  "dist",
  "custom-agents.js",
);
const DISPATCH_TOOLS = [
  "Agent",
  "get_subagent_result",
  "steer_subagent",
];
const BUSINESS_TOOLS = [
  "commerce_ops_analyze_attribution_and_leads",
  "commerce_ops_analyze_live_commerce_data",
  "commerce_ops_analyze_short_video_data",
  "commerce_ops_drilldown_commerce_metric",
  "commerce_ops_inspect_commerce_data",
];
const EXPECTED_PROJECT_AGENTS = [
  "attribution-lead-analyst",
  "commerce-review-strategist",
  "content-growth-analyst",
  "live-conversion-analyst",
];

function parseArgs(argv) {
  const outputIndex = argv.indexOf("--output");
  if (outputIndex === -1) {
    return {
      output: path.join(
        PROJECT_ROOT,
        "artifacts",
        "miniclaw-subagent-bridge-validation-v2.json",
      ),
    };
  }
  const output = argv[outputIndex + 1];
  if (!output) throw new Error("--output 后必须提供文件路径");
  return { output: path.resolve(process.cwd(), output) };
}

function check(checks, checkId, condition, detail) {
  checks.push({
    check_id: checkId,
    status: condition ? "pass" : "fail",
    detail,
  });
  if (!condition) throw new Error(`${checkId}: ${detail}`);
}

function runGit(args) {
  return execFileSync("git", ["-C", PLATFORM_ROOT, ...args], {
    encoding: "utf8",
    windowsHide: true,
  }).trim();
}

function extractDefaultAllowedTools(source) {
  const block = source.match(/const DEFAULT_ALLOWED_TOOLS = \[([\s\S]*?)\];/);
  if (!block) throw new Error("无法从 pi-index.ts 解析 DEFAULT_ALLOWED_TOOLS");
  return [...block[1].matchAll(/'([^']+)'/g)].map((match) => match[1]);
}

function simulateMiniClawSelectedTools(allowedTools, customTools = []) {
  const aliases = {
    Bash: "bash",
    Read: "read",
    Write: "write",
    Edit: "edit",
    Glob: "find",
    Grep: "grep",
    Task: "Agent",
    TaskOutput: "get_subagent_result",
    TaskStop: "steer_subagent",
  };
  const builtins = new Set([
    "read",
    "bash",
    "edit",
    "write",
    "find",
    "grep",
    "ls",
  ]);
  const dispatch = new Set(DISPATCH_TOOLS);
  const customNames = new Set(customTools.map((tool) => tool.name));
  const expanded = allowedTools.flatMap((name) =>
    name === "mcp__miniclaw__*"
      ? [...customNames]
      : [aliases[name] ?? name],
  );
  return [...new Set(expanded)].filter(
    (name) =>
      builtins.has(name) || customNames.has(name) || dispatch.has(name),
  );
}

function extensionWithExactTools(extensions, expectedTools) {
  const expected = [...expectedTools].sort().join(",");
  return extensions.filter((extension) => {
    const actual = [...extension.tools.keys()].sort().join(",");
    return actual === expected;
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const checks = [];
  let tempRoot;

  check(
    checks,
    "source:platform-commit",
    runGit(["rev-parse", "HEAD"]) === PLATFORM_COMMIT,
    `project014 is pinned to ${PLATFORM_COMMIT}`,
  );
  check(
    checks,
    "source:platform-git-clean",
    runGit(["status", "--porcelain"]) === "",
    "project014 Git worktree is clean",
  );

  const packageJson = JSON.parse(
    await fs.readFile(SUBAGENTS_PACKAGE, "utf8"),
  );
  check(
    checks,
    "source:subagents-version",
    packageJson.name === "@tintinweb/pi-subagents" &&
      packageJson.version === SUBAGENTS_VERSION,
    `pi-subagents package is ${SUBAGENTS_VERSION}`,
  );
  check(
    checks,
    "source:subagents-pi-entry",
    packageJson.main === undefined &&
      packageJson.exports === undefined &&
      packageJson.pi?.extensions?.join(",") === "./src/index.ts",
    "pi-subagents exposes a Pi metadata entry but no ordinary package entry",
  );
  check(
    checks,
    "source:compiled-entry-exists",
    await fs
      .access(SUBAGENTS_ENTRY)
      .then(() => true)
      .catch(() => false),
    "the fixed baseline contains dist/index.js",
  );

  const runtimeRequire = createRequire(pathToFileURL(PI_RUNTIME_SOURCE));
  let packageResolution;
  let packageResolutionError;
  try {
    packageResolution = runtimeRequire.resolve("@tintinweb/pi-subagents");
  } catch (error) {
    packageResolutionError = error;
  }
  check(
    checks,
    "baseline:ordinary-package-resolution-fails",
    packageResolution === undefined &&
      packageResolutionError?.code === "MODULE_NOT_FOUND",
    "MiniClaw's current require.resolve path cannot resolve the package entry",
  );

  const bridgeSource = await fs.readFile(BRIDGE_ENTRY, "utf8");
  check(
    checks,
    "bridge:fixed-compiled-entry",
    bridgeSource.includes(pathToFileURL(SUBAGENTS_ENTRY).href) &&
      bridgeSource.includes(PLATFORM_COMMIT) &&
      bridgeSource.includes(SUBAGENTS_VERSION),
    "project017 bridge is pinned to the fixed MiniClaw and pi-subagents baseline",
  );
  check(
    checks,
    "bridge:no-third-party-source-copy",
    bridgeSource.length < 12000 &&
      bridgeSource.includes("new Proxy(pi") &&
      bridgeSource.includes('property === "registerTool"') &&
      !bridgeSource.includes("createAgentSession") &&
      !bridgeSource.includes("manager.spawn") &&
      !bridgeSource.includes("spawnAndWait"),
    "bridge wraps the installed compiled entry with a project-local policy and does not copy spawn/session implementation",
  );
  check(
    checks,
    "bridge:fail-closed-policy-source",
    [
      "PROJECT017_AGENT_DISPATCH_POLICY",
      "project017_agent_dispatch_fail_closed_v1",
      'hasOwnProperty.call(params, "isolation")',
      "isolation_argument_forbidden_in_non_git_project",
      "previous_agent_dispatch_blocked",
      "project017DispatchAudit",
      'pi.on("tool_call"',
      'pi.on("tool_result"',
      "isError: true",
    ].every((token) => bridgeSource.includes(token)),
    "bridge source contains the isolation guard, session lock, audit payload, and runtime error marking",
  );

  const piHostPackage = JSON.parse(
    await fs.readFile(
      path.join(
        PROJECT_ROOT,
        ".pi",
        "extensions",
        "commerce-ops-mcp",
        "node_modules",
        "@earendil-works",
        "pi-coding-agent",
        "package.json",
      ),
      "utf8",
    ),
  );
  check(
    checks,
    "dependency:pi-host-version",
    piHostPackage.version === PI_HOST_VERSION,
    `validation loader uses Pi host ${PI_HOST_VERSION}`,
  );

  const [{ DefaultResourceLoader, SettingsManager }, { loadCustomAgents }] =
    await Promise.all([
      import(pathToFileURL(PI_HOST_ENTRY).href),
      import(pathToFileURL(CUSTOM_AGENTS_ENTRY).href),
    ]);

  const originalCwd = process.cwd();
  try {
    process.chdir(PROJECT_ROOT);
    await fs.mkdir(path.join(PROJECT_ROOT, "runtime", "tmp"), {
      recursive: true,
    });
    tempRoot = await fs.mkdtemp(
      path.join(PROJECT_ROOT, "runtime", "tmp", "subagent-bridge-loader-"),
    );
    const agentDir = path.join(tempRoot, "agent");
    await fs.mkdir(agentDir, { recursive: true });
    const settingsManager = SettingsManager.create(PROJECT_ROOT, agentDir, {
      projectTrusted: true,
    });
    const resourceLoader = new DefaultResourceLoader({
      cwd: PROJECT_ROOT,
      agentDir,
      settingsManager,
      systemPrompt: "",
      noSkills: true,
      noPromptTemplates: true,
      noThemes: true,
      noContextFiles: true,
    });
    await resourceLoader.reload({ resolveProjectTrust: async () => true });
    const loaded = resourceLoader.getExtensions();
    check(
      checks,
      "loader:no-errors",
      loaded.errors.length === 0,
      "DefaultResourceLoader reports no extension load errors",
    );

    const dispatchExtensions = extensionWithExactTools(
      loaded.extensions,
      DISPATCH_TOOLS,
    );
    const businessExtensions = extensionWithExactTools(
      loaded.extensions,
      BUSINESS_TOOLS,
    );
    check(
      checks,
      "loader:single-dispatch-extension",
      dispatchExtensions.length === 1,
      "one project extension registers exactly the three dispatch tools",
    );
    check(
      checks,
      "loader:dispatch-extension-is-bridge",
      path.resolve(dispatchExtensions[0].path) === path.resolve(BRIDGE_ENTRY),
      "the dispatch tools are attributed to the project017 bridge entry",
    );
    const agentRegistration = dispatchExtensions[0].tools.get("Agent");
    const agentTool = agentRegistration?.definition;
    check(
      checks,
      "loader:agent-policy-injected",
      agentTool?.description.includes(
        "Project017 is not a Git repository",
      ) &&
        agentTool?.description.includes(
          "Omit the Agent isolation argument entirely",
        ) &&
        agentTool?.promptGuidelines?.some((line) =>
          line.includes("Final reporting must merge parent Agent attempts"),
        ),
      "loaded Agent definition carries the project017 dispatch and parent-child attempt-ledger policy",
    );
    check(
      checks,
      "loader:worktree-recommendation-removed",
      !agentTool?.description.includes('isolation: "worktree" runs') &&
        !agentTool?.description.includes(
          'Use isolation: "worktree" to run',
        ) &&
        agentTool?.parameters?.properties?.isolation?.description?.includes(
          "Forbidden in project017",
        ),
      "loaded Agent prose no longer recommends worktree and its schema field says to omit isolation",
    );

    const guardContext = {
      cwd: PROJECT_ROOT,
      sessionManager: {
        getSessionId: () => "project017-no-model-guard-validation",
      },
    };
    const firstGuardResult = await agentTool.execute(
      "project017-guard-call-1",
      {
        prompt: "No-model guard validation; this must not start an agent.",
        description: "validate isolation guard",
        subagent_type: "content-growth-analyst",
        isolation: "worktree",
      },
      undefined,
      undefined,
      guardContext,
    );
    const firstAudit = firstGuardResult.details?.project017DispatchAudit;
    check(
      checks,
      "guard:worktree-blocked-before-spawn",
      firstGuardResult.isError === true &&
        firstGuardResult.details?.status === "blocked" &&
        firstAudit?.dispatchLocked === true &&
        firstAudit?.parentAgentAttemptCount === 1 &&
        firstAudit?.attempts?.[0]?.reason ===
          "isolation_argument_forbidden_in_non_git_project",
      "manual ToolDefinition execution blocks isolation=worktree and records the first parent attempt without a runtime context",
    );

    const secondGuardResult = await agentTool.execute(
      "project017-guard-call-2",
      {
        prompt: "No-model guard validation; this must remain locked.",
        description: "validate session lock",
        subagent_type: "content-growth-analyst",
      },
      undefined,
      undefined,
      guardContext,
    );
    const secondAudit = secondGuardResult.details?.project017DispatchAudit;
    check(
      checks,
      "guard:second-dispatch-remains-locked",
      secondGuardResult.isError === true &&
        secondGuardResult.details?.status === "blocked" &&
        secondAudit?.dispatchLocked === true &&
        secondAudit?.parentAgentAttemptCount === 2 &&
        secondAudit?.attempts?.[1]?.reason ===
          "previous_agent_dispatch_blocked",
      "a second Agent call in the same extension session is blocked without delegating to upstream execution",
    );

    let toolResultGuard;
    for (const handler of dispatchExtensions[0].handlers.get("tool_result") ?? []) {
      const candidate = await handler(
        {
          type: "tool_result",
          toolName: "Agent",
          toolCallId: "project017-guard-call-1",
          input: { isolation: "worktree" },
          content: firstGuardResult.content,
          details: firstGuardResult.details,
          isError: false,
        },
        guardContext,
      );
      if (
        candidate?.isError === true &&
        candidate?.details?.project017DispatchAudit
      ) {
        toolResultGuard = candidate;
      }
    }
    check(
      checks,
      "guard:runtime-tool-result-marked-error",
      toolResultGuard?.isError === true &&
        toolResultGuard?.details?.project017DispatchAudit?.dispatchLocked ===
          true,
      "tool_result hook marks a blocked Agent result as an error and preserves the audit payload",
    );
    check(
      checks,
      "loader:single-business-extension",
      businessExtensions.length === 1,
      "one project extension still registers exactly the five commerce tools",
    );
    check(
      checks,
      "loader:business-extension-unchanged",
      path.resolve(businessExtensions[0].path) === path.resolve(BUSINESS_ENTRY),
      "the five business tools remain owned by commerce-ops-mcp",
    );

    const projectAgents = loadCustomAgents(PROJECT_ROOT, true);
    const projectAgentNames = [...projectAgents.entries()]
      .filter(([, agent]) => agent.source === "project")
      .map(([name]) => name)
      .sort();
    check(
      checks,
      "agents:strict-project-parse",
      projectAgentNames.join(",") === EXPECTED_PROJECT_AGENTS.join(","),
      "strict parser loads exactly the four project017 specialist agent files",
    );
    const professionalAgents = EXPECTED_PROJECT_AGENTS.filter(
      (name) => name !== "commerce-review-strategist",
    ).map((name) => projectAgents.get(name));
    check(
      checks,
      "agents:professional-extension-scope",
      professionalAgents.every(
        (agent) =>
          agent?.extensions?.length === 1 &&
          path.resolve(agent.extensions[0]) === path.resolve(BUSINESS_ENTRY) &&
          agent.extSelectors?.length === 3 &&
          (agent.builtinToolNames ?? []).every(
            (tool) => tool === "none" || !["bash", "read", "write", "edit"].includes(tool),
          ),
      ),
      "three professional agents retain explicit business extension allowlists and no usable built-in tools",
    );
    const reviewAgent = projectAgents.get("commerce-review-strategist");
    check(
      checks,
      "agents:review-tool-free",
      reviewAgent?.extensions === false &&
        (reviewAgent?.builtinToolNames ?? []).length === 0,
      "review strategist remains extension-free and tool-free",
    );

    const piIndexSource = await fs.readFile(PI_INDEX_SOURCE, "utf8");
    const defaultAllowedTools = extractDefaultAllowedTools(piIndexSource);
    const selectedMainTools = simulateMiniClawSelectedTools(
      defaultAllowedTools,
      [],
    );
    check(
      checks,
      "main-session:dispatch-tools-selected",
      DISPATCH_TOOLS.every((tool) => selectedMainTools.includes(tool)),
      "MiniClaw main-session selection includes all three dispatch tools",
    );
    check(
      checks,
      "main-session:no-business-tools-selected",
      BUSINESS_TOOLS.every((tool) => !selectedMainTools.includes(tool)),
      "MiniClaw main-session selection excludes all five commerce tools",
    );

    const report = {
      schema_version: "2.0",
      validation_kind:
        "project017_miniclaw_subagent_bridge_fail_closed_no_model",
      status: checks.every((item) => item.status === "pass")
        ? "pass"
        : "fail",
      generated_at: new Date().toISOString(),
      project_root: PROJECT_ROOT,
      source_platform: {
        root: PLATFORM_ROOT,
        commit: PLATFORM_COMMIT,
        git_clean: true,
        pi_subagents_version: SUBAGENTS_VERSION,
        ordinary_package_resolution: "MODULE_NOT_FOUND",
        bridged_compiled_entry: SUBAGENTS_ENTRY,
      },
      runtime: {
        scope_note:
          "These fields describe actions performed by this no-model validator, not the total runtime history of project017.",
        node_version: process.version,
        pi_host_version: PI_HOST_VERSION,
        loader: "DefaultResourceLoader",
        project_trust_resolved: true,
        model_runtime_created_by_this_validator: false,
        agent_session_created_by_this_validator: false,
        model_called_by_this_validator: false,
        provider_read_by_this_validator: false,
        sqlite_read_or_written_by_this_validator: false,
        mcp_transport_started_by_this_validator: false,
      },
      loader_result: {
        loaded_extension_count: loaded.extensions.length,
        load_error_count: loaded.errors.length,
        dispatch_extension_path: dispatchExtensions[0].path,
        business_extension_path: businessExtensions[0].path,
        dispatch_tools: [...DISPATCH_TOOLS].sort(),
        business_tools: [...BUSINESS_TOOLS].sort(),
      },
      main_session_policy_simulation: {
        source: "project014 pi-index.ts DEFAULT_ALLOWED_TOOLS plus pi-runtime.ts alias and filter semantics",
        default_allowed_tools: defaultAllowedTools,
        selected_tool_names: selectedMainTools,
        dispatch_tools_selected: true,
        business_tools_selected: false,
      },
      guard_validation: {
        policy_id: firstAudit.policyId,
        isolation_attempt_result: {
          status: firstGuardResult.details.status,
          is_error: firstGuardResult.isError,
          audit: firstAudit,
        },
        second_attempt_result: {
          status: secondGuardResult.details.status,
          is_error: secondGuardResult.isError,
          audit: secondAudit,
        },
        runtime_tool_result_hook_sets_error: toolResultGuard.isError,
        upstream_agent_execute_reached: false,
      },
      strict_project_agents: projectAgentNames,
      checks_total: checks.length,
      checks_passed: checks.filter((item) => item.status === "pass").length,
      checks_failed: checks.filter((item) => item.status === "fail").length,
      checks,
      evidence_boundary: {
        compatibility_bridge_loaded_by_this_validator: true,
        dispatch_tool_definitions_registered_by_this_validator: true,
        business_tool_definitions_registered_by_this_validator: true,
        main_session_tool_policy_simulated_from_fixed_source: true,
        specialist_agent_files_strictly_parsed_by_this_validator: true,
        isolation_guard_executed_without_agent_session: true,
        second_dispatch_lock_executed_without_agent_session: true,
        model_runtime_created_by_this_validator: false,
        agent_session_created_by_this_validator: false,
        subagent_spawned_by_this_validator: false,
        business_tool_called_by_this_validator: false,
        real_model_called_by_this_validator: false,
        real_business_data_used_by_this_validator: false,
        post_fix_multi_agent_execution_verified: false,
      },
      removal_condition:
        "Remove this bridge after MiniClaw resolves @tintinweb/pi-subagents through its pi.extensions metadata or another ordinary package entry; revalidate first to avoid duplicate registration.",
    };
    const serialized = `${JSON.stringify(report, null, 2)}\n`;
    await fs.mkdir(path.dirname(args.output), { recursive: true });
    await fs.writeFile(args.output, serialized, "utf8");
    process.stdout.write(serialized);
  } finally {
    process.chdir(originalCwd);
    if (tempRoot) {
      await fs.rm(tempRoot, { recursive: true, force: true });
    }
  }
}

main().catch((error) => {
  process.stderr.write(`${error.stack ?? error.message}\n`);
  process.exitCode = 1;
});

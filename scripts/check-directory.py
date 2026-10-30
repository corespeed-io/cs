"""Validate the self-contained package submitted to the OpenAI Directory."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plugins/corespeed-directory"
EXPECTED = {
    ".codex-plugin/plugin.json",
    ".mcp.json",
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "assets/app-icon.svg",
    "skills/corespeed-memory/SKILL.md",
    "skills/corespeed-memory/agents/openai.yaml",
}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


files = list(PACKAGE.rglob("*"))
require(not any(path.is_symlink() for path in files), "Directory package must not use symlinks")
actual = {path.relative_to(PACKAGE).as_posix() for path in files if path.is_file()}
require(actual == EXPECTED, f"Directory package file inventory changed: {actual ^ EXPECTED}")

manifest = json.loads((PACKAGE / ".codex-plugin/plugin.json").read_text())
require(manifest["name"] == "corespeed", "Preserve the existing Directory plugin identity")
require(manifest["skills"] == "./skills/", "Bundle the dedicated memory skill")
require(manifest["mcpServers"] == "./.mcp.json", "Directory requires the root MCP file")
for field in ("composerIcon", "logo"):
    relative = manifest["interface"][field]
    require(relative.startswith("./"), f"{field} must be package-local")
    require((PACKAGE / relative).is_file(), f"Missing asset: {relative}")

server = json.loads((PACKAGE / ".mcp.json").read_text())
require(
    server == {"mcpServers": {"corespeed": {
        "type": "http",
        "url": "https://api.corespeed.io/mcp/plugin/chatgpt-memory",
    }}},
    "The Directory package must use the memory-only OAuth server without credentials",
)
market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
sources = {plugin["name"]: plugin["source"]["path"] for plugin in market["plugins"]}
require(sources["corespeed"] == "./plugins/corespeed-directory", "Codex must install the reviewed package")
require(sources["corespeed-cli"] == "./plugins/corespeed-cli", "Keep standalone CLI installation available")

review = manifest["extensions"]["com.openai"]["review"]["test_cases"]
require(len(review["positive"]) == 5 and len(review["negative"]) == 3, "Expected five positive and three negative cases")
prompts = manifest["interface"]["defaultPrompt"]
if isinstance(prompts, str):
    prompts = [prompts]
require(
    isinstance(prompts, list) and len(prompts) <= 3 and all(isinstance(p, str) and p for p in prompts),
    "Expected a nonempty prompt string or at most three nonempty prompts",
)
require(0 < len(manifest["interface"]["shortDescription"]) <= 30, "Directory subtitle exceeds 30 characters")
print("Directory package: self-contained memory skill, fixed OAuth endpoint; standalone CLI retained")

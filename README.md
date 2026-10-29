# CoreSpeed for coding agents

[CoreSpeed](https://corespeed.io) gives an agent one MCP server,
`https://api.corespeed.io/mcp`, that carries the tools of every app your
organization has connected (Notion, Slack, GitHub, X, Linear, and more),
long-term memory shared across agents, a Drive every tool reads and writes,
media generation and understanding, live web search, and public social data,
all billed to one wallet with spend caps and an audit trail.

This repository holds the CoreSpeed plugin for Claude Code, Codex and Cursor,
and the agent skills it bundles. The `cs` command-line tool is published to npm as
[`@corespeed/cs`](https://www.npmjs.com/package/@corespeed/cs).

## Claude Code

```bash
claude plugin marketplace add corespeed-io/cs
claude plugin install corespeed@corespeed
```

Inside Claude Code the same is `/plugin marketplace add corespeed-io/cs`, then
`/plugin install corespeed@corespeed`. Start a new session, run `/mcp`, pick
the CoreSpeed server, and authenticate in the browser.

## Codex

```bash
codex plugin marketplace add corespeed-io/cs
codex plugin add corespeed@corespeed
```

Start a new Codex task. When CoreSpeed shows **Authentication required**,
select **Authenticate** (or open **Settings → MCP servers → CoreSpeed**) and
finish the sign-in in the browser. In the ChatGPT desktop app the plugin
appears under the **CoreSpeed** marketplace once it has been added.

Codex installs the self-contained `plugins/corespeed-directory/` package.
It uses `https://api.corespeed.io/mcp/plugin/chatgpt-memory`: nine memory
operations, current identity and completion of memory write approvals. Its
`corespeed-memory` skill guides recall, saving, correction, memory links and
deletion. New memories are private unless you ask to share them. This is the
package prepared for OpenAI Directory review; it contains no general CLI or
HTTP API skill and does not operate connected apps or files. It requires the
memory endpoint to be deployed before installation or submission. The current
OpenAI portal cannot change an existing MCP server URL through a package
upload; contact OpenAI support to migrate the existing listing first. See the
[submission guide](https://developers.openai.com/plugins/deploy/submission#update-your-published-plugin).

Claude Code keeps the full server and the existing CLI/API skills in
`plugins/corespeed/`. Cursor keeps that package's earlier fixed endpoint.

## Codex, CLI only

```bash
codex plugin marketplace add corespeed-io/cs
codex plugin add corespeed-cli@corespeed
```

This plugin registers no MCP server. Its `cs-cli` skill has the agent install
the `cs` command-line tool, sign in once in the browser, and then find and call
CoreSpeed tools from the shell (`cs mcp search`, `cs mcp get`, `cs mcp call`),
and move files in and out of the organization's Drive (`cs drive put`,
`cs drive get`). Pick it when Codex cannot load your organization's full tool
list, or when you want every call to go through the shell. It remains
available separately from the repository marketplace. It is not part of the
Directory memory package, and its availability here is not an OpenAI approval.

## Cursor and Grok Bot

In Cursor, open **Customize**, search the Marketplace for **CoreSpeed**, and
install it. Pick the CoreSpeed MCP server and sign in in the browser when
Cursor asks. Grok Bot loads plugins from the Cursor Marketplace, so the same
plugin works there.

Cursor reads the legacy package's root `.mcp.json`, so its server is the plugin
surface `https://api.corespeed.io/mcp/plugin/chatgpt`: shared memory and
connector discovery, a list no organization's connector count can grow past
what Cursor loads. A connected app's tools and the organization's Drive are
reached through the bundled `cs-cli` skill (`cs mcp call`, `cs drive`).

To try this repository before a Marketplace release, copy `plugins/corespeed`
to `~/.cursor/plugins/local/corespeed` and reload the window.

## The `cs` CLI

```bash
npm install -g @corespeed/cs
cs login
```

`cs` signs you in through the browser, mints `sk-cs-` API keys for CI, switches
organizations, connects apps, and calls tools from a terminal. See the
[CLI docs](https://corespeed.io/docs/cli).

## What the plugins contain

| Plugin | Part | What it does |
| --- | --- | --- |
| Codex `corespeed` (`plugins/corespeed-directory/`) | MCP and `corespeed-memory` skill | Eleven individually exposed memory, identity and approval operations; no app connections, files or generic executor. |
| Claude/Cursor legacy `corespeed` (`plugins/corespeed/`) | MCP server | Browser sign-in (OAuth 2.1 + PKCE), never a pasted key. Claude Code: the full `https://api.corespeed.io/mcp`. Cursor and earlier Codex installs: the plugin surface `https://api.corespeed.io/mcp/plugin/chatgpt` (memory, connector discovery). |
| Claude/Cursor legacy `corespeed` | `cs-cli` skill | Using the `cs` CLI: sign-in, finding and calling tools from a shell, memory, files in the Drive, API keys, organizations, connectors, remote MCP servers, credit. |
| Claude/Cursor legacy `corespeed` | `cs-api` skill | Calling CoreSpeed over HTTP from code and CI: credentials, `tools/list` and `tools/call`, error codes, credits. |
| `corespeed-cli` | `cs-cli` skill | The same skill, and nothing else: no MCP server is registered. |

The public Directory upload is **only `plugins/corespeed-directory/`**, with
the manifest at its root under `.codex-plugin/`. Do not upload this entire
repository or the legacy `plugins/corespeed/` package. Run
`python3 scripts/check-directory.py` before packaging. CI checks the exact
file inventory so a broader skill cannot enter the upload accidentally.

Standalone CLI installation remains your choice, using npm or the separate
`corespeed-cli` plugin above. The memory plugin neither requires nor installs
it and does not use it to complete an unavailable or denied operation. CLI
sign-in is separate; plugin credentials are not copied.

If you added CoreSpeed to your client by hand earlier (`claude mcp add`,
`codex mcp add`, or an entry in Cursor's `mcp.json`), remove that entry
before installing the plugin, so every tool is registered once.

Sign-in happens at `login.corespeed.io`, and the plugins' only servers are
`https://api.corespeed.io/mcp`, `https://api.corespeed.io/mcp/plugin/chatgpt`,
and `https://api.corespeed.io/mcp/plugin/chatgpt-memory`.
Anything else claiming to be CoreSpeed is not this plugin.

## Other clients

Copilot in VS Code, Claude.ai, ChatGPT, and any client that speaks
Streamable HTTP with MCP authorization connect with the URL alone. Per-client
setup is at https://corespeed.io/docs/mcp.

## Links

- Docs: https://corespeed.io/docs
- Dashboard: https://app.corespeed.io
- Pricing: https://corespeed.io/pricing
- Support: support@corespeed.io
- Security reports: see [SECURITY.md](SECURITY.md)

## License

[Apache-2.0](LICENSE)

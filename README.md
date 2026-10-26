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

In Codex the plugin's server (the root `.mcp.json`, the one file the OpenAI
Plugins Directory accepts) is `https://api.corespeed.io/mcp/plugin/chatgpt`: a
fixed, small tool list — shared memory and connector discovery — that no
organization's connector count can push past Codex's catalog limit. Claude Code
gets the full `https://api.corespeed.io/mcp` from `.mcp.claude.json`, which its
manifest declares and which replaces the root entry by name. The agent
finds an app with `manage__connectors_search`, hands you a link to connect it,
calls a connected app's tools through the bundled `cs-cli` skill
(`cs mcp search`, `cs mcp get`, `cs mcp call`), and moves files in and out
of the organization's Drive with `cs drive`.

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
list, or when you want every call to go through the shell. It is the plugin
meant for the OpenAI Plugins Directory.

## Cursor and Grok Bot

In Cursor, open **Customize**, search the Marketplace for **CoreSpeed**, and
install it. Pick the CoreSpeed MCP server and sign in in the browser when
Cursor asks. Grok Bot loads plugins from the Cursor Marketplace, so the same
plugin works there.

Cursor reads the same root `.mcp.json` as Codex, so its server is the plugin
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
| `corespeed` | MCP server | Browser sign-in (OAuth 2.1 + PKCE), never a pasted key. Claude Code: the full `https://api.corespeed.io/mcp`. Codex and Cursor: the plugin surface `https://api.corespeed.io/mcp/plugin/chatgpt` (memory, connector discovery). |
| `corespeed` | `cs-cli` skill | Using the `cs` CLI: sign-in, finding and calling tools from a shell, memory, files in the Drive, API keys, organizations, connectors, remote MCP servers, credit. |
| `corespeed` | `cs-api` skill | Calling CoreSpeed over HTTP from code and CI: credentials, `tools/list` and `tools/call`, error codes, credits. |
| `corespeed-cli` | `cs-cli` skill | The same skill, and nothing else: no MCP server is registered. |

If you added CoreSpeed to your client by hand earlier (`claude mcp add`,
`codex mcp add`, or an entry in Cursor's `mcp.json`), remove that entry
before installing the plugin, so every tool is registered once.

Sign-in happens at `login.corespeed.io`, and the plugins' only servers are
`https://api.corespeed.io/mcp` and `https://api.corespeed.io/mcp/plugin/chatgpt`.
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

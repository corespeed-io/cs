# CoreSpeed for coding agents

[CoreSpeed](https://corespeed.io) gives an agent one MCP server,
`https://api.corespeed.io/mcp`, that carries the tools of every app your
organization has connected (Notion, Slack, GitHub, X, Linear, and more),
long-term memory shared across agents, media generation and understanding,
live web search, and public social data, all billed to one wallet with spend
caps and an audit trail.

This repository holds the CoreSpeed plugin for Claude Code and Codex, and the
agent skills it bundles. The `cs` command-line tool is published to npm as
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

## The `cs` CLI

```bash
npm install -g @corespeed/cs
cs login
```

`cs` signs you in through the browser, mints `sk-cs-` API keys for CI, switches
organizations, connects apps, and calls tools from a terminal. See the
[CLI docs](https://corespeed.io/docs/cli).

## What the plugin contains

| Part | What it does |
| --- | --- |
| MCP server | `https://api.corespeed.io/mcp` with browser sign-in (OAuth 2.1 + PKCE). You never paste an API key. |
| `cs-cli` skill | Using the `cs` CLI: sign-in, API keys, organizations, connectors, remote MCP servers, credit. |
| `cs-api` skill | Calling CoreSpeed over HTTP from code and CI: credentials, `tools/list` and `tools/call`, error codes, credits. |

If you added CoreSpeed to your client by hand earlier (`claude mcp add` or
`codex mcp add`), remove that entry before installing the plugin, so every
tool is registered once.

Sign-in happens at `login.corespeed.io`, and the plugin's only server is
`https://api.corespeed.io/mcp`. Anything else claiming to be CoreSpeed is not
this plugin.

## Other clients

Cursor, Copilot in VS Code, Claude.ai, ChatGPT, and any client that speaks
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

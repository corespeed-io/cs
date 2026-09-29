---
name: cs-cli
description: Use when a task needs the CoreSpeed CLI (cs, npm package @corespeed/cs) — signing in from a terminal, minting or rotating sk-cs- API keys for CI, switching organizations, connecting apps, registering an organization's own MCP servers, checking credit, or calling CoreSpeed tools from a shell. Triggers on "cs login", "cs keys create", "cs switch", "cs token", "cs mcp search", "cs mcp get", "cs mcp call", "cs connectors", "cs remote", "cs usage", "cs mcp-config", or "@corespeed/cs".
---

# CoreSpeed CLI (`cs`)

`cs` runs every command against the same CoreSpeed MCP server your agents use,
under a member session stored on this machine. It needs Node.js 20 or Bun and
has no runtime dependencies. With this plugin installed, the agent already
reaches CoreSpeed through its own browser sign-in; reach for `cs` when a human
is at a terminal, when a CI job needs an API key, or to check what an agent
will see.

The canonical reference is https://corespeed.io/docs/cli. When this skill and
the docs disagree, the docs win.

## Install

```bash
npm install -g @corespeed/cs     # or: pnpm add -g, yarn global add, bun install -g
npx @corespeed/cs --help         # run once without installing (bunx works too)
```

Run the install command again to update.

## Sign in

```bash
cs login                  # opens the browser; prints the URL if it cannot
cs login --org <org-id>   # sign in to one organization
```

Sign-in needs a human in a browser; an agent cannot complete it. A member of
several organizations picks one at the terminal; without a terminal the
default is used. After that the stored session refreshes itself, so it is once
per machine, not once per command. Until then every command exits `3` with
``Error: not logged in; run `cs login` ``.

On a machine reached over SSH, forward a fixed callback port and open the
printed URL in your local browser:

```bash
ssh -L 8765:127.0.0.1:8765 you@devbox
CS_LOGIN_PORT=8765 cs login
```

`cs logout` removes the stored session. The browser keeps its own sign-in, so
signing in as someone else means signing out on the dashboard first.

## Commands

| Command | What it does |
| --- | --- |
| `cs login [--org <id>]` | Browser sign-in; stores a member session |
| `cs logout` | Remove the stored session |
| `cs whoami` | Signed-in user, active organization, and the others you belong to |
| `cs switch [<org-id>]` | Change the active organization without signing in again |
| `cs token` | Print a fresh session JWT (five minutes) for one request |
| `cs keys create <name>` | Mint an `sk-cs-` key; the secret is printed once |
| `cs keys list` | Keys as JSON (id, name, last four characters, cap, usage), never the secret |
| `cs keys rotate <id>` | Revoke and replace under a new id; name, cap, and usage carry over |
| `cs keys revoke <id>` | Invalidate a key; it then answers `401 invalid_api_key` |
| `cs mcp-config` | An `mcpServers` entry carrying the five-minute session token |
| `cs mcp search <words…> [--limit <n>] [--json]` | Rank your tools for a task, one line each: name, `read-only`/`destructive` hints, first sentence |
| `cs mcp get <tool> [--json]` | One tool in full: description, input schema verbatim, its connector's accounts, a call to start from |
| `cs mcp call <tool> [json] [--raw]` | Call it as you and print the result; `--raw` prints the `CallToolResult` as it arrived |
| `cs mcp list [--json]` | Every tool, one line each; `--json` prints their definitions |
| `cs connectors list` | Connectors offered to you, with status and account aliases |
| `cs connectors connect <id>` | Open the connect flow in the browser |
| `cs connectors disconnect <id> [--account <alias>]` | Remove a connected account |
| `cs connectors accounts list\|rename\|remove` | Manage connected accounts and their aliases |
| `cs remote add\|list\|show\|refresh\|remove` | The organization's own MCP servers, as `org__<slug>__*` tools; writes need an org admin |
| `cs usage` | Available credit and plan |

## Find a tool and call it

An organization can have more than a thousand tools, so work in three steps
instead of listing them all:

```bash
cs mcp search search tweets            # rank tools for the task
cs mcp get twitter__search_posts       # the one you picked: schema and accounts
cs mcp call twitter__search_posts '{"query": "from:corespeed", "account": "@corespeed"}'
```

Search matches tool names, descriptions and argument names and descriptions, so
describe the task. A connector's tools exist only once it is connected. `get`
prints the input schema exactly as the tool declares it; for a tool that takes
`account`, it lists the connector's accounts — `account` is required when there
is more than one.

`call` prints the tool's result: its `structuredContent` when it returns one,
else its content with JSON pretty-printed. When the tool also returned text
that is more than a copy of `structuredContent`, `stderr` says so; `--raw` shows
it. `media__understand` keeps its answer in that text, so read it with `--raw`.
Numbers arrive exactly as the server sent them.

## A key for CI

The CLI itself takes no API key and is not part of a CI job. Mint a key once,
store it as the job's secret, and send it directly:

```bash
cs keys create ci-deploy          # copy the sk-cs- secret now; it is shown once
```

The job then sends `Authorization: Bearer <key>` on `POST
https://api.corespeed.io/mcp`; the `cs-api` skill has the request shape and
error codes. The CLI creates keys without a spend cap or expiry; set both at
https://app.corespeed.io/keys.

## Session tokens are short-lived

`cs token` and `cs mcp-config` hand out the session's own access token, which
lives five minutes. That is right for a request you are making now and wrong
for anything that stays configured: give a lasting configuration an API key,
or let the client sign in through the browser itself.

The session is stored under `~/.config/cs` (or `$CS_CONFIG_DIR`). Treat that
directory as a credential: never commit it or print its contents.

## Output and exit codes

Results go to `stdout`; prompts, warnings, and errors go to `stderr`, so
`cs token`, `cs keys list` and `cs mcp call` pipe cleanly. Failures print
`Error: <message>`. `cs mcp call` prints the tool's result whatever it says, and
its exit code then says whether the tool did what it was asked.

| Exit | Meaning | Move |
| --- | --- | --- |
| `0` | Success | |
| `1` | Usage error, or the request was refused (not found, conflict, invalid input) — for `cs mcp call`, the tool answered `isError`, does not exist, or refused the arguments | Fix the command; `cs --help`; for a tool, `cs mcp get <tool>` |
| `3` | Not signed in, or the session was rejected | A human runs `cs login`; for an organization with its own SSO or MFA, `cs login --org <id>` |
| `4` | The account cannot do this now: no active organization, payment required, suspended, or admin role needed — including a metered tool call refused for the organization's standing | Act on the message; credit is at https://app.corespeed.io/billing |
| `5` | CoreSpeed unreachable, rate-limited, or answering badly | Retry later |
| `6` | A `cs mcp call` is waiting for a human's approval and has not run | Run the `cs mcp call manage__approval_wait '{"approval_id": "…"}'` printed on `stderr` right away — the request expires if nobody waits on it; do not retry the original call |

| Variable | Purpose |
| --- | --- |
| `CS_CONFIG_DIR` | Where the session is stored; a separate directory keeps a separate sign-in |
| `CS_LOGIN_PORT` | Fixed sign-in callback port, for signing in over SSH |
| `DO_NOT_TRACK=1` | Send a bare `cs` user agent |

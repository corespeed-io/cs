---
name: cs-cli
description: Use when a task needs the CoreSpeed CLI (cs, npm package @corespeed/cs) — signing in from a terminal, finding a CoreSpeed tool for a task and calling it from a shell (cs mcp search, cs mcp get, cs mcp call), searching or saving shared memory, uploading a local file to the organization's Drive or downloading one from it (cs drive put, cs drive get), minting or rotating sk-cs- API keys for CI, switching organizations, connecting apps, registering an organization's own MCP servers, or checking credit. Triggers on "cs login", "cs mcp search", "cs mcp call", "cs drive", "cs keys create", "cs switch", "cs token", "cs connectors", "cs remote", "cs usage", "cs mcp-config", or "@corespeed/cs".
---

# CoreSpeed CLI (`cs`)

`cs` runs every command against the same CoreSpeed MCP server your agents use,
under a member session stored on this machine. It needs Node.js 20 or Bun and
has no runtime dependencies.

If your client has the full CoreSpeed MCP server
(`https://api.corespeed.io/mcp`), call its tools directly. The Codex plugin's
server (`https://api.corespeed.io/mcp/plugin/chatgpt`) carries memory and
connector discovery only, so there a connected app's tools are called with
`cs`. Use `cs` as well when there is no MCP server, when a client cannot load a
large tool list, when a human is at a terminal, or when a CI job needs an API
key.

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

## Calling tools from a shell

Three commands, in this order. Do not guess a tool's name or arguments:
search for it, read its schema, then call it.

```bash
cs mcp search remember a decision       # best matches first, one line each; --limit <n>, --json
cs mcp get memory__remember             # description, input schema, and a call to start from
cs mcp call memory__remember '{"memory": "Staging deploys go through bart.", "scope": "shared"}'
```

`cs mcp call` prints the tool's result on stdout: its `structuredContent` as
JSON when it has one, otherwise its content blocks, text as text (JSON text
re-indented) and anything else summarised. To parse the result as JSON in
every case, pass `--raw`: it prints the whole `CallToolResult` as it arrived.
The exit code says what the tool did (table below), so check it before
reading the output. `cs mcp list` prints every tool you can
call, one line each; `--json` prints their definitions.

Tool names are `<prefix>__<tool>`: `memory__*` is shared memory, `drive__*`
the organization's file system, `media__*` media generation and
understanding, `web__*` live web search and scraping, `social__*` public
social data, `mail__*` agent mail where it is on, `manage__*` your account
and keys, and each app your organization has connected has its own prefix.
A prefix that is not in `cs mcp list` is switched off for you or not
connected; it is not missing from the CLI.

### Memory

CoreSpeed memory is long-term and shared across the agents in your
organization. At the start of a non-trivial task, search it with two or three
short queries before planning. After significant work, save the durable
decisions and conventions.

```bash
cs mcp call memory__search '{"query": "deploy process", "limit": 5}'
cs mcp call memory__remember '{"memory": "Staging deploys go through bart, never wrangler directly.", "scope": "shared"}'
```

### Drive

The organization's Drive is where files live: every file a tool takes or
makes has a path there, like `reports/q3.pdf`, private to you or shared with
the organization. Bytes never travel through tool arguments, so `cs mcp call`
alone cannot move a local file; `cs drive` does, with a local file on one
end:

```bash
cs drive put ./q3.pdf reports/q3.pdf          # upload; a new version if the path exists
cs drive put ./README.md docs/readme.md --access org   # a new path every member sees
cs drive get reports/q3.pdf ~/Downloads/      # download by path, drv_* file id or dver_* version id
cs drive get notes/todo.md -                  # bytes to stdout
cs drive ls reports/                          # a folder; --recursive, --json
cs drive mv tmp/uploads/x.png shots/x.png     # rename or move; out of tmp/ keeps it
cs drive share reports/q3.pdf link            # private | org | link | public; --rotate
cs drive rm reports/old.pdf                   # not reversible
cs drive usage                                # kept bytes against the plan
```

`put` prints the stored file (`path`, `file_id`, `version_id`, `size_bytes`,
`sha256`); `get` prints one line naming where the bytes went. Text up to
1 MiB can also be stored straight from arguments with
`cs mcp call drive__put '{"path": "notes/a.md", "text": "..."}'`, and the
other Drive tools (the change feed, S3 credentials for rclone or the AWS CLI)
are `cs mcp call drive__…`. Anything under `tmp/` expires after 7 days.

### Approvals

Some write calls need a human's approval first. The command then exits `6`
and prints on stderr the exact command to run next:

```
cs mcp call manage__approval_wait '{"approval_id": "…"}'
```

Run it right away. It waits for the decision and prints the original tool's
result; a request nobody waits on expires.

## In Codex

Codex runs shell commands in a sandbox that has no network by default, in
both `workspace-write` and `read-only` mode. `cs` needs the network, so the
sandbox blocks it and Codex asks whether to run the command outside the
sandbox. Approve it, or allow network for the workspace once in
`~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

Do not change the user's sandbox settings yourself; ask.

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
| `cs mcp search <words…> [--limit <n>] [--json]` | Find tools for a task, best match first, one line each; `--json` prints the matches' definitions |
| `cs mcp get <tool> [--json]` | One tool in full: description, input schema, a call to start from; `--json` prints its definition verbatim |
| `cs mcp call <tool> [json] [--raw]` | Call a tool and print its result; exits non-zero when the tool did not do what it was asked |
| `cs mcp list [--json]` | Every tool, one line each; `--json` prints their definitions |
| `cs drive put <file> <path> [--mime <type>] [--access private\|org]` | Upload a local file to a Drive path; a new version when the path exists |
| `cs drive get <path\|file_id\|version_id> [<file> \| -]` | Download a Drive file to a local file (its own name by default) or stdout |
| `cs drive ls [<prefix>] [--recursive] [--json]` | List a folder, or everything under a prefix |
| `cs drive mv <from> <to>` | Rename or move a file; leaving `tmp/` keeps it |
| `cs drive rm <path>` | Delete a file and every version of it |
| `cs drive share <path> private\|org\|link\|public [--rotate]` | Who can see a file; `link` and `public` answer a `share_url` |
| `cs drive usage` | Kept bytes against the plan, and what sits under `tmp/` |
| `cs connectors list` | Connectors offered to you, with status and account aliases |
| `cs connectors connect <id>` | Open the connect flow in the browser |
| `cs connectors disconnect <id> [--account <alias>]` | Remove a connected account |
| `cs connectors accounts list\|rename\|remove` | Manage connected accounts and their aliases |
| `cs remote add\|list\|show\|refresh\|remove` | The organization's own MCP servers, as `org__<slug>__*` tools; writes need an org admin |
| `cs usage` | Available credit and plan |

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
`cs token` and `cs keys list` pipe cleanly. Failures print `Error: <message>`.

| Exit | Meaning | Move |
| --- | --- | --- |
| `0` | Success | |
| `1` | Usage error, or the request was refused (not found, conflict, invalid input) | Fix the command; `cs --help` |
| `3` | Not signed in, or the session was rejected | A human runs `cs login`; for an organization with its own SSO or MFA, `cs login --org <id>` |
| `4` | The account cannot do this now: no active organization, payment required, suspended, or admin role needed | Act on the message; credit is at https://app.corespeed.io/billing |
| `5` | CoreSpeed unreachable, rate-limited, or answering badly | Retry later |
| `6` | The tool call waits for a human's approval and has not run | Run the `cs mcp call manage__approval_wait …` command printed on stderr, right away |

| Variable | Purpose |
| --- | --- |
| `CS_CONFIG_DIR` | Where the session is stored; a separate directory keeps a separate sign-in |
| `CS_LOGIN_PORT` | Fixed sign-in callback port, for signing in over SSH |
| `DO_NOT_TRACK=1` | Send a bare `cs` user agent |

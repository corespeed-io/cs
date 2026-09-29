---
name: cs-api
description: Use when calling CoreSpeed over HTTP from code, CI, or a headless agent — the MCP endpoint at api.corespeed.io/mcp, sk-cs- and sk-csa- API keys, browser sign-in tokens, tool discovery, credits and spend caps, or a CoreSpeed error code such as missing_authorization, invalid_api_key, jwt_session_required, no_active_org, payment_required, key_spend_limit_exceeded, needs_reauth, or rate_limit_exceeded.
---

# Calling CoreSpeed over HTTP

CoreSpeed is one authenticated MCP server, `https://api.corespeed.io/mcp`,
that carries the tools of the apps an organization has connected, long-term
memory, media generation and understanding, live web search, and public social
data. An agent with this plugin installed already has it as an MCP server; this
skill is for code that talks to it directly: a service, a CI job, a script, or
a client without OAuth.

CoreSpeed is not an LLM gateway. It does not proxy model calls, so do not point
an Anthropic or OpenAI SDK base URL at it.

The canonical reference is https://corespeed.io/docs (index for agents:
https://corespeed.io/llms.txt). When this skill and the docs disagree, the docs
win.

## Credentials

Every request resolves to one principal inside one organization, and that pair
decides which tools, accounts, and memories the response contains.

| Credential | Who is calling | Use it for |
| --- | --- | --- |
| Browser sign-in (MCP OAuth token) | A member, from an OAuth-capable client | Interactive agents. Accepted on `POST /mcp` only |
| `sk-cs-…` API key | The member who created it | CI, services, clients without OAuth |
| `sk-csa-…` agent key | An agent principal with its own identity | Unattended agents; reaches the organization's shared accounts only |
| Session JWT | A member, from the `cs` CLI or the dashboard | One-off scripts (`cs token`); lives five minutes |

Send any of them as `Authorization: Bearer <token>`. `x-api-key: <key>` also
works for the two key types. Pick one header, not both.

Keys come from https://app.corespeed.io/keys, `cs keys create <name>`, or the
`manage__keys_create` tool under a signed-in session. Read the key from an
environment variable or a secret store; never print, log, or commit it. Give
every key a monthly spend cap in the dashboard.

## Calling `/mcp`

The transport is Streamable HTTP and stateless: one JSON-RPC message per
`POST`, no batches, no `GET /mcp` stream. `Accept` must list both
`application/json` and `text/event-stream`; the answer is a JSON body.

```ts
const res = await fetch("https://api.corespeed.io/mcp", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.CORESPEED_API_KEY}`,
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
  },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "memory__search_memory",
      arguments: { query: "rollout window" },
    },
  }),
});

const { result } = await res.json();
if (result.isError) throw new Error(result.content[0].text);
```

`tools/list` is the same request with `"method": "tools/list"` and
`"params": {}`. Samples in curl, Python, and Go are at
https://corespeed.io/docs/reference/mcp/tools-call.

Tool names are `<capability>__<operation>`: `memory__*`, `media__*`, `web__*`,
`social__*`, `manage__*`, `<connector>__*` for each connected app, and
`org__<slug>__*` for the organization's own MCP servers.

Discover, never hard-code. `tools/list` returns exactly what this caller can
invoke right now, with input schemas:

- A missing tool is a decision, not a bug: the capability is off for this
  caller or the app is not connected. Connections are made at
  https://app.corespeed.io/connectors.
- A listed tool is not necessarily healthy: a connector account in
  `needs_reauth` still lists its tools, and they fail until it is
  reauthorized.
- A listed tool is not necessarily permitted: the account-management
  `manage__*` tools (keys, agents, accounts, `whoami`, `switch_org`) are listed
  for API keys but answer `jwt_session_required`. Run them from the dashboard,
  the `cs` CLI, or a browser-signed-in client.

To give a media tool a local file, call `media__create_upload` with the exact
`mime_type` and `size_bytes`, `PUT` the raw bytes to the returned `upload_url`
with every returned header within ten minutes, then pass the returned
`file_uri` to `media__understand` or `media__generate`.

## Reading results and errors

A call fails at one of two layers.

An HTTP failure (`4xx`/`5xx`) means the request was refused. The body is
`{"error": {"type", "code", "message"}}`; branch on `error.code`.

A tool failure is HTTP `200` with `result.isError: true`. Always check
`result.isError`, then `result.structuredContent.error.code`. Billing holds and
session refusals put the JSON envelope in the text block instead.

| Code | Meaning | What to do |
| --- | --- | --- |
| `missing_authorization` (401) | No credential header | Send one. On `/mcp` the `WWW-Authenticate` header starts OAuth for clients that support it |
| `invalid_jwt` (401) | The bearer JWT failed verification | Re-run the sign-in, or `cs token` for a session JWT |
| `invalid_api_key` (401) | Key unknown, revoked, or expired | Replace it; do not retry |
| `jwt_session_required` | A session-only tool or route was called with an API key | Use a signed-in session |
| `no_active_org` | Signed in, but no organization yet | Open https://app.corespeed.io once, then sign in again |
| `payment_required` | Organization wallet on a billing hold | An org admin adds credit at https://app.corespeed.io/billing |
| `key_spend_limit_exceeded` | This key hit its monthly cap | Raise the cap or wait for the month to roll over |
| `org_suspended` / `agent_suspended` | Administrative or agent suspension | Adding credit does not clear it; resume the agent or contact support |
| `not_connected` / `needs_reauth` | The connector account is missing or must be reauthorized | Connect or reauthorize it in the dashboard; do not rotate the CoreSpeed key |
| `ambiguous_account` | Several accounts connected | Pass `account` with one of `error.aliases` |
| `rate_limit_exceeded` (429) | Too many requests in the 60-second window | Wait for `Retry-After`, then retry |
| `platform_db_unavailable` (503) | CoreSpeed failed closed on a transient state | Retry with backoff |
| `endpoint_not_found` (404) | Unknown path | Use `POST /mcp` |

Do not retry authentication, billing, or suspension codes unchanged. Retry
only the transient ones. Check before retrying a write that answered
`upstream_unreachable` or `cancelled`: the change may already have been
applied. Every code is listed at https://corespeed.io/docs/reference/errors.

## Credits

Metered calls are priced in credits (1,000 credits = $1) and drawn from the
organization wallet. Memory and discovery are free. A billing hold or a key's
spend cap is checked before a metered tool runs; discovery, account reads, and
key management keep working through a hold. Prices are at
https://corespeed.io/pricing.

## Checks when something fails

1. `GET https://api.corespeed.io/health` needs no credential and answers
   `{"status":"ok"}`.
2. The request is a `POST /mcp` with both `Accept` values and
   `Content-Type: application/json`.
3. The credential header is set and is the right kind for the call (a session
   for `manage__*`, a key or OAuth token for everything else).
4. `tools/list` with the same credential contains the tool.
5. Branch on the `code`, not the message text.

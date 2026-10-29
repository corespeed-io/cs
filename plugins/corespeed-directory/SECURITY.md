# Security

Report a vulnerability in this plugin, its skills, or the CoreSpeed service by
email to **support@corespeed.io** with "Security" in the subject. Please do not
open a public issue for it.

Include what you found, how to reproduce it, and what an attacker could do with
it.

## What this repository ships

The plugin is configuration and Markdown. It registers one MCP server,
`https://api.corespeed.io/mcp`, and authenticates it with the client's own
OAuth sign-in against `login.corespeed.io`. It contains no executable code, no
hooks, and no credentials, and it never asks for an API key.

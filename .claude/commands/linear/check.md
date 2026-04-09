# Check Linear MCP connections

Verify that all Linear MCP servers in `.mcp.json` are connected and responding.

## Steps

### 1. Find configured servers

Read `.mcp.json` and list every MCP server entry whose name contains "linear".

If no Linear servers are found, tell the user to copy `.mcp.json.example` to `.mcp.json` and configure it.

### 2. Test each server

For each Linear server found, call its `list_teams` tool to confirm it responds.

Report the result as a table:

| Server | Status | Workspace |
|:-------|:-------|:----------|
| linear-org1 | Connected | Foo Corp |
| linear-org2 | Connected | Bar Corp |

If a server fails, show the error and suggest checking:

- The API key is set in `~/.env`
- The env var name in `.mcp.json` matches the key name in `~/.env`
- Run `/mcp` to see the server status

### 3. Summary

End with a one-line summary: "N of M Linear servers connected."

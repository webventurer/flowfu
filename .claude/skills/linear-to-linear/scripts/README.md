# linear_client.py

A small, vendored Python client for the Linear GraphQL API. Built to
power the `linear-to-linear` and `trello-to-linear` migration skills,
but reusable in any Python script that needs to create issues,
projects, labels, or attachments in Linear without going through the
Linear MCP.

## Vendor contract

<mark>**Copy the file, no support, no versioning, no PyPI.** If you copy `linear_client.py` into your project, you own your copy. It is not a published package. There are no releases, no changelog, no semver guarantees. When Linear's API changes, we update `linear_client.py` in this repo — it is your job to pull the update into your vendored copy (or fix it yourself).</mark>

This is a deliberate choice. The alternative — a published SDK with a
support contract — costs more in ceremony than it would save in
convenience for the small number of scripts that will ever use this.

## What it provides

- `graphql(api_key, query, variables)` — raw client with retries and
  proper error handling (`LinearError` on HTTP or GraphQL errors).
- `resolve_by_name(api_key, entity, name)` — convenience for turning
  names into IDs.
- `resolve_states(api_key, team_id)` — workflow states by team.
- `require_env(name)` — env var helper.
- `normalize_quotes(text)` — fold smart quotes to straight quotes.
- `LinearError` — the exception raised on any failure.

### Mutations (all return the created/updated node id as a string)

- `create_issue(api_key, team_id, project_id, state_id, title, description, label_ids=None)`
- `update_issue(api_key, issue_id, title=None, description=None, state_id=None, label_ids=None)`
- `create_attachment(api_key, issue_id, title, url, subtitle=None, metadata=None)`
- `create_project(api_key, team_id, name, description=None, content=None)`
- `update_project(api_key, project_id, description=None, content=None)`
- `create_project_update(api_key, project_id, body, health)`
- `create_project_link(api_key, project_id, url, label)`
- `create_label(api_key, name, color=None, team_id=None)`
- `delete_issue(api_key, issue_id)`
- `delete_project(api_key, project_id)`
- `delete_label(api_key, label_id)`

### Queries

- `list_issues(api_key, team_id=None, project_id=None)` — auto-paginates. Returns list of dicts: `id`, `identifier`, `title`, `description`.
- `list_projects(api_key, team_id=None)` — auto-paginates. Returns list of dicts: `id`, `name`, `teams`. Filter by team client-side if `team_id` is passed.
- `list_labels(api_key, team_id=None)` — auto-paginates. Returns list of dicts: `id`, `name`, `color`, `team`. Filter by team client-side if `team_id` is passed.

## API contract

- **IDs only.** Mutation helpers accept entity IDs, not names. Use
  `resolve_by_name()` first if you start from a name.
- **Returns an ID string.** Every create/update helper returns the
  created or updated node's id.
- **Raises `LinearError` on failure.** Connection errors (after
  retries), HTTP errors, and 200 responses with a GraphQL `errors`
  payload all raise `LinearError` with the operation name and error
  messages. Never logs API keys.
- **Retries only connection errors and timeouts.** GraphQL errors are
  raised, not retried.

## Usage

```python
from linear_client import create_issue, resolve_by_name, require_env

api_key = require_env("LINEAR_API_KEY")
team_id = resolve_by_name(api_key, "teams", "Webventurer")
project_id = resolve_by_name(api_key, "projects", "stride")
state_id = resolve_by_name(api_key, "workflowStates", "Backlog")

issue_id = create_issue(
    api_key,
    team_id=team_id,
    project_id=project_id,
    state_id=state_id,
    title="Investigate flaky test",
    description="The auth test fails 1 in 50 runs.",
)
print(f"Created {issue_id}")
```

## `linear_api.py` shim

`scripts/linear_api.py` is a deprecated shim kept for one release so
existing callers (phase scripts, third-party vendored copies) keep
working. New code should import from `linear_client` directly. The
shim will be removed in a future release.

## Skill-specific loaders

`load_source_cards` and `load_target_issues_file` live in
`skill_io.py`. They know the shape of the export/match JSON files that
`linear-to-linear` produces and are not part of the reusable client.

"""Tests for linear_client.

Most tests hit a real Linear API and are gated by LINEAR_E2E=1. The
error-handling test is mocked and runs unconditionally.

Run with:
    python -m pytest tools/tests/
    LINEAR_E2E=1 python -m pytest tools/tests/
"""

import os
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the tools directory to the path so we can import linear_client
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from linear_client import (  # noqa: E402
    LinearError,
    create_attachment,
    create_issue,
    create_label,
    create_project,
    create_project_link,
    create_project_update,
    delete_issue,
    delete_label,
    delete_project,
    graphql,
    list_issues,
    list_labels,
    list_projects,
    require_env,
    resolve_by_name,
    resolve_states,
    update_issue,
    update_project,
)

LIVE = os.environ.get("LINEAR_E2E") == "1"
API_KEY_ENV = os.environ.get(
    "LINEAR_TEST_API_KEY_ENV", "LINEAR_PLAYGROUND_API_KEY"
)
TEAM_NAME = os.environ.get("LINEAR_TEST_TEAM", "Playground")

live_only = pytest.mark.skipif(
    not LIVE, reason="Live Linear tests require LINEAR_E2E=1"
)


def suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture
def api_key():
    return require_env(API_KEY_ENV)


@pytest.fixture
def team_id(api_key):
    return resolve_by_name(api_key, "teams", TEAM_NAME)


@pytest.fixture
def state_id(api_key, team_id):
    states = resolve_states(api_key, team_id)
    return states["Backlog"]["id"]


@pytest.fixture
def scratch_project(api_key, team_id):
    name = f"sdk-test-project-{suffix()}"
    project_id = create_project(
        api_key,
        team_id,
        name=name,
        description="test summary",
        content="# test content",
    )
    yield project_id
    try:
        delete_project(api_key, project_id)
    except LinearError:
        pass


@live_only
def test_create_and_delete_issue(api_key, team_id, scratch_project, state_id):
    title = f"sdk-test-issue-{suffix()}"
    issue_id = create_issue(
        api_key,
        team_id=team_id,
        project_id=scratch_project,
        state_id=state_id,
        title=title,
        description="test body",
    )
    try:
        assert isinstance(issue_id, str)
        assert len(issue_id) > 0
    finally:
        delete_issue(api_key, issue_id)


@live_only
def test_create_project_with_fields(api_key, team_id):
    name = f"sdk-test-project-fields-{suffix()}"
    project_id = create_project(
        api_key, team_id, name=name, description="short", content="## long"
    )
    try:
        assert isinstance(project_id, str)
    finally:
        delete_project(api_key, project_id)


@live_only
def test_update_project(api_key, scratch_project):
    new_id = update_project(
        api_key,
        scratch_project,
        description="updated summary",
        content="## updated content",
    )
    assert new_id == scratch_project


@live_only
def test_create_project_update(api_key, scratch_project):
    update_id = create_project_update(
        api_key, scratch_project, body="status check", health="onTrack"
    )
    assert isinstance(update_id, str)


@live_only
def test_create_project_link(api_key, scratch_project):
    link_id = create_project_link(
        api_key, scratch_project, url="https://example.com", label="Docs"
    )
    assert isinstance(link_id, str)


@live_only
def test_create_and_delete_label(api_key):
    name = f"sdk-test-label-{suffix()}"
    label_id = create_label(api_key, name=name, color="#ff00ff")
    try:
        assert isinstance(label_id, str)
    finally:
        delete_label(api_key, label_id)


@live_only
def test_update_issue(api_key, team_id, scratch_project, state_id):
    title = f"sdk-test-update-{suffix()}"
    issue_id = create_issue(
        api_key,
        team_id=team_id,
        project_id=scratch_project,
        state_id=state_id,
        title=title,
        description="original",
    )
    try:
        returned = update_issue(api_key, issue_id, description="updated")
        assert returned == issue_id
        fetched = [
            i
            for i in list_issues(api_key, project_id=scratch_project)
            if i["id"] == issue_id
        ]
        assert fetched and fetched[0]["description"] == "updated"
    finally:
        delete_issue(api_key, issue_id)


@live_only
def test_list_issues_filters_by_project(
    api_key, team_id, scratch_project, state_id
):
    title = f"sdk-test-list-{suffix()}"
    issue_id = create_issue(
        api_key,
        team_id=team_id,
        project_id=scratch_project,
        state_id=state_id,
        title=title,
        description="test",
    )
    try:
        issues = list_issues(api_key, project_id=scratch_project)
        assert any(i["id"] == issue_id for i in issues)
        assert all(isinstance(i.get("title"), str) for i in issues)
    finally:
        delete_issue(api_key, issue_id)


@live_only
def test_list_projects_returns_projects(api_key):
    projects = list_projects(api_key)
    assert isinstance(projects, list)
    assert projects, "expected at least one project in the test workspace"
    assert all("id" in p and "name" in p for p in projects)


@live_only
def test_list_labels_returns_labels(api_key):
    name = f"sdk-test-label-{suffix()}"
    label_id = create_label(api_key, name=name, color="#00ff00")
    try:
        labels = list_labels(api_key)
        assert any(lbl["id"] == label_id for lbl in labels)
    finally:
        delete_label(api_key, label_id)


@live_only
def test_create_attachment(api_key, team_id, scratch_project, state_id):
    title = f"sdk-test-issue-att-{suffix()}"
    issue_id = create_issue(
        api_key,
        team_id=team_id,
        project_id=scratch_project,
        state_id=state_id,
        title=title,
        description="test body",
    )
    try:
        attachment_id = create_attachment(
            api_key,
            issue_id=issue_id,
            title="Reference",
            url="https://example.com/ref",
        )
        assert isinstance(attachment_id, str)
    finally:
        delete_issue(api_key, issue_id)


@live_only
def test_graphql_raises_linear_error_on_bad_query(api_key):
    with pytest.raises(LinearError) as excinfo:
        graphql(api_key, "{ nonexistentField }")
    assert "nonexistentField" in str(excinfo.value) or "400" in str(
        excinfo.value
    )


def test_graphql_raises_linear_error_on_errors_payload():
    """Unit test with a mocked response — runs without LINEAR_E2E."""

    class FakeResp:
        status_code = 200
        text = ""

        def json(self):
            return {
                "data": None,
                "errors": [{"message": "something broke"}],
            }

    with patch("linear_client.requests.post", return_value=FakeResp()):
        with pytest.raises(LinearError) as excinfo:
            graphql("fake-key", "mutation DoThing { doThing }")
    assert "something broke" in str(excinfo.value)
    assert "DoThing" in str(excinfo.value)

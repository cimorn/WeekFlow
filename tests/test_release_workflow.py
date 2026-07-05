from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_workflow_builds_and_publishes_electron_windows_assets():
    workflow_text = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "build-windows:" in workflow_text
    assert "publish-release:" in workflow_text
    assert "branches:" in workflow_text
    assert "- main" in workflow_text
    assert "workflow_dispatch:" in workflow_text
    assert "tag:" in workflow_text
    assert "actions/setup-node@v6" in workflow_text
    assert "node-version: \"24\"" in workflow_text
    assert "corepack enable" in workflow_text
    assert "pnpm install --frozen-lockfile" in workflow_text
    assert "pnpm run electron:pack" in workflow_text
    assert "python -m pytest tests -q" in workflow_text
    assert "gh release create" in workflow_text
    assert "gh release upload" in workflow_text
    assert 'GH_REPO: ${{ github.repository }}' in workflow_text
    assert 'GH_TOKEN: ${{ github.token }}' in workflow_text
    assert '--repo "$GH_REPO"' in workflow_text
    assert "dist/WeekFlow-V*.zip" in workflow_text
    assert "dist/WeekFlow-V*.exe" not in workflow_text
    assert "dist/WeekFlow-*.exe" not in workflow_text
    assert "dist/WeekFlow-*.zip" not in workflow_text
    assert "dist/WeekFlow.exe" not in workflow_text
    assert "dist/WeekFlow.zip" not in workflow_text
    assert "gh release delete-asset" in workflow_text
    assert "--yes" in workflow_text
    assert 'TAG_NAME="latest"' in workflow_text
    assert "PACKAGE_VERSION=" in workflow_text
    assert 'TITLE="WeekFlow-V$PACKAGE_VERSION"' in workflow_text
    assert "WeekFlow Latest" not in workflow_text
    assert '--title "$TITLE"' in workflow_text
    assert 'gh release edit "$TAG_NAME" --repo "$GH_REPO" --title "$TITLE"' in workflow_text
    assert 'if [[ "$TAG_NAME" == "latest" ]]' in workflow_text
    assert 'gh api --method PATCH "repos/$GH_REPO/git/refs/tags/$TAG_NAME"' in workflow_text
    assert '-f sha="$GITHUB_SHA" -F force=true' in workflow_text
    assert "actions/checkout@v5" in workflow_text
    assert "actions/setup-python@v6" in workflow_text
    assert "actions/upload-artifact@v6" in workflow_text
    assert "actions/download-artifact@v6" in workflow_text
    assert "build-macos:" not in workflow_text
    assert ".scripts/build_exe.ps1" not in workflow_text
    assert ".scripts/package_release.ps1" not in workflow_text
    assert ".scripts/build_macos_app.sh" not in workflow_text
    assert ".scripts/package_macos_release.sh" not in workflow_text
    assert "app/*.exe" not in workflow_text
    assert "app/*.zip" not in workflow_text
    assert "dist/*.exe" not in workflow_text


def test_ci_workflow_uses_node24_ready_actions():
    workflow_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "actions/checkout@v5" in workflow_text
    assert "actions/setup-python@v6" in workflow_text

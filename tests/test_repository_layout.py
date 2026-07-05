from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def test_repository_layout_matches_open_source_cleanup_plan():
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    gitignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace")

    assert (ROOT / "docs" / "README.en.md").exists()
    assert (ROOT / ".scripts").exists()
    assert not (ROOT / "README.en.md").exists()
    assert not (ROOT / "app").exists()
    assert not (ROOT / "assets").exists()
    assert not (ROOT / "releases").exists()
    assert not (ROOT / "scripts").exists()
    assert (ROOT / "src" / "weekflow_logo.ico").exists()
    assert not (ROOT / "docs" / "CODEX_THREAD_HANDOFF.md").exists()
    assert not (ROOT / "docs" / "RELEASE_NOTES_26.03.21.md").exists()
    assert not (ROOT / "docs" / "superpowers").exists()
    tracked_files = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert not any(path.startswith("src/") and path.endswith(".egg-info") for path in tracked_files)
    assert ".github/" not in gitignore_text
    assert ".scripts/" not in gitignore_text
    assert ".gitignore" not in gitignore_text
    assert ".gitattributes" not in gitignore_text
    assert "dist/" in gitignore_text
    assert "tests/" not in gitignore_text
    assert "build_exe.ps1" not in readme_text
    assert "package_release.ps1" not in readme_text


def test_readme_stays_user_focused_and_image_based():
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    english_text = (ROOT / "docs" / "README.en.md").read_text(encoding="utf-8", errors="replace")

    assert "自动发布" not in readme_text
    assert "从源码运行" not in readme_text
    assert "pnpm run electron:pack" not in readme_text
    assert "Automatic Release" not in english_text
    assert "Run From Source" not in english_text
    assert "pnpm run electron:pack" not in english_text
    assert "https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/01-home.png" in readme_text
    assert "https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/05-preview.png" in readme_text

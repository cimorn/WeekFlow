from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_build_script_uses_versioned_app_icon():
    ico_icon_path = ROOT / "src" / "weekflow_logo.ico"
    build_script = (ROOT / ".scripts" / "build_exe.ps1").read_text(encoding="utf-8")

    assert ico_icon_path.exists()
    assert "--icon" in build_script
    assert "src\\weekflow_logo.ico" in build_script or "src/weekflow_logo.ico" in build_script
    assert "--onefile" not in build_script
    assert "dist\\WeekFlow\\data" in build_script
    assert "dist\\WeekFlow\\data\\figs" not in build_script


def test_release_packaging_uses_folder_mode_app_bundle():
    packaging_script = (ROOT / ".scripts" / "package_release.ps1").read_text(encoding="utf-8")

    assert "$appDir = $distDir" in packaging_script
    assert "WeekFlow.exe not found in dist. Build the app first." in packaging_script
    assert "Copy-Item -LiteralPath $_.FullName -Destination $bundleDir -Recurse -Force" in packaging_script
    assert "dist\\WeekFlow\\WeekFlow.exe" not in packaging_script
    assert "data\\figs" not in packaging_script
    assert "data" in packaging_script


def test_release_packaging_scripts_include_icon_file():
    windows_script = (ROOT / ".scripts" / "package_release.ps1").read_text(encoding="utf-8")
    macos_script = (ROOT / ".scripts" / "package_macos_release.sh").read_text(encoding="utf-8")

    assert "weekflow_logo.ico" in windows_script
    assert "weekflow_logo.ico" in macos_script

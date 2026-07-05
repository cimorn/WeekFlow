import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_electron_package_declares_runtime_and_build_scripts():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert package["version"] == "26.07.04"
    assert 'version = "26.07.04"' in pyproject_text
    assert package["main"] == "electron/main.cjs"
    assert package["scripts"]["electron:dev"] == "electron ."
    assert ".scripts/build_electron_bridge.ps1" in package["scripts"]["electron:bridge"]
    assert ".scripts/build_electron_bridge.ps1" in package["scripts"]["electron:pack"]
    assert ".scripts/run_electron_builder.ps1" in package["scripts"]["electron:pack"]
    assert ".scripts/finalize_electron_dist.ps1" in package["scripts"]["electron:pack"]
    assert package["scripts"]["electron:dist"] == package["scripts"]["electron:pack"]
    assert "electron" in package["devDependencies"]
    assert "electron-builder" in package["devDependencies"]
    assert "rcedit" in package["devDependencies"]
    assert package["build"]["win"]["icon"] == "src/weekflow_logo.ico"
    assert package["build"]["win"]["signAndEditExecutable"] is False
    assert any(
        resource.get("from") == "data" and resource.get("to") == "data"
        for resource in package["build"]["extraFiles"]
    )
    assert (ROOT / "data" / ".keep").exists()
    finalizer = (ROOT / ".scripts" / "finalize_electron_dist.ps1")
    assert finalizer.exists()
    finalizer_text = finalizer.read_text(encoding="utf-8")
    assert 'dist-electron\\win-unpacked' in finalizer_text
    assert '$distDir = Join-Path $root "dist"' in finalizer_text
    assert '$appDir = Join-Path $distDir "WeekFlow"' not in finalizer_text
    assert "ConvertFrom-Json" in finalizer_text
    assert '$versionedExeName = "WeekFlow-V$version.exe"' in finalizer_text
    assert '$zipPath = Join-Path $distDir "WeekFlow-V$version.zip"' in finalizer_text
    assert 'WeekFlow.zip' not in finalizer_text
    assert 'Copy-Item -Path (Join-Path $sourceResolved "*") -Destination $distDir' in finalizer_text
    assert 'Finalized app is missing WeekFlow.exe' in finalizer_text
    assert 'Rename-Item (Join-Path $distDir "WeekFlow.exe") $versionedExeName -Force' in finalizer_text
    assert 'Finalized app is missing $versionedExeName' in finalizer_text
    assert 'node_modules\\rcedit\\bin\\rcedit-x64.exe' in finalizer_text
    assert '--set-icon $iconPath' in finalizer_text
    assert 'rcedit failed with exit code' in finalizer_text
    assert '$zipEntries = Get-ChildItem -LiteralPath $distDir -Force' in finalizer_text
    assert 'Compress-Archive -Path $zipEntries.FullName -DestinationPath $zipPath' in finalizer_text
    assert "Remove-Item -LiteralPath $intermediateResolved -Recurse -Force" in finalizer_text

    bridge_builder = (ROOT / ".scripts" / "build_electron_bridge.ps1")
    assert bridge_builder.exists()
    bridge_builder_text = bridge_builder.read_text(encoding="utf-8")
    assert "src\\WeekFlow\\electron_bridge.py" in bridge_builder_text
    assert '"--onefile"' in bridge_builder_text
    assert '"WeekFlowBridge"' in bridge_builder_text
    assert '"dist\\bridge"' in bridge_builder_text
    assert "Electron bridge build did not create" in bridge_builder_text
    assert "Remove-Item -LiteralPath $workPath -Recurse -Force" in bridge_builder_text

    electron_builder = (ROOT / ".scripts" / "run_electron_builder.ps1")
    assert electron_builder.exists()
    electron_builder_text = electron_builder.read_text(encoding="utf-8")
    assert "WEEKFLOW_NODE" in electron_builder_text
    assert "node_modules\\electron-builder\\cli.js" in electron_builder_text
    assert "codex-runtimes" in electron_builder_text


def test_electron_main_uses_python_bridge_and_secure_preload():
    main_text = (ROOT / "electron" / "main.cjs").read_text(encoding="utf-8")
    preload_text = (ROOT / "electron" / "preload.cjs").read_text(encoding="utf-8")

    assert "WeekFlow.electron_bridge" in main_text
    assert "ipcMain.handle('bridge:command'" in main_text
    assert "contextIsolation: true" in main_text
    assert "nodeIntegration: false" in main_text
    assert "function appIconPath()" in main_text
    assert "path.join(app.getAppPath(), 'src', 'weekflow_logo.ico')" in main_text
    assert "icon: appIconPath()" in main_text
    assert "PYTHONIOENCODING" in main_text
    assert "contextBridge.exposeInMainWorld('weekflow'" in preload_text
    assert "bridge:command" in preload_text
    assert "dialog:exportBackup" in main_text
    assert "exportBackupDialog" in preload_text


def test_electron_main_disables_native_menu_bar():
    main_text = (ROOT / "electron" / "main.cjs").read_text(encoding="utf-8")

    assert "Menu.setApplicationMenu(null)" in main_text
    assert "autoHideMenuBar: true" in main_text


def test_electron_main_reuses_existing_window_on_second_launch():
    main_text = (ROOT / "electron" / "main.cjs").read_text(encoding="utf-8")

    assert "const gotSingleInstanceLock = app.requestSingleInstanceLock()" in main_text
    assert "if (!gotSingleInstanceLock)" in main_text
    assert "app.quit()" in main_text
    assert "app.on('second-instance'" in main_text
    assert "focusMainWindow()" in main_text
    assert "function focusMainWindow()" in main_text
    assert "mainWindow.isMinimized()" in main_text
    assert "mainWindow.restore()" in main_text
    assert "mainWindow.show()" in main_text
    assert "mainWindow.focus()" in main_text


def test_electron_renderer_contains_expected_editor_regions():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")

    for region in [
        "basic-form-grid",
        "results-feeling-grid",
        "project-workspace",
        "markdown-preview",
    ]:
        assert region in html

    assert "createReport" in app_js
    assert "replaceReport" in app_js
    assert "saveCurrent" in app_js
    assert "project-workflow-step" in styles


def test_electron_renderer_uses_project_name_header_and_short_tab_labels():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")

    assert '<strong id="reportTitle">WeekFlow</strong>' in html
    assert "未命名周报" not in html
    assert "基本信息 / AI" not in html
    assert "成果 / 感受" not in html
    assert '<button data-section="basic" class="active">基本信息</button>' in html
    assert '<button data-section="results">成果感受</button>' in html
    assert "currentReport.topic?.trim() || 'WeekFlow'" in app_js


def test_electron_renderer_moves_save_and_preview_to_top_navigation():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")

    topbar = html.split('<header class="topbar">', 1)[1].split("</header>", 1)[0]

    assert '<aside class="action-rail"' not in html
    assert 'id="saveBtn"' in topbar
    assert 'id="openPreviewBtn"' in topbar
    assert topbar.index('id="saveBtn"') < topbar.index('id="openPreviewBtn"')
    assert 'class="top-action-group"' in html
    assert 'id="fileActions"' in html


def test_electron_renderer_removes_top_secondary_buttons_and_helper_copy():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")

    topbar = html.split('<header class="topbar">', 1)[1].split("</header>", 1)[0]
    basic_page = html.split('id="page-basic"', 1)[1].split('id="page-results"', 1)[0]
    results_page = html.split('id="page-results"', 1)[1].split('id="page-projects"', 1)[0]

    assert 'id="saveAsBtn"' not in topbar
    assert 'id="polishBtn"' not in topbar
    assert 'id="testAiBtn"' not in topbar
    assert 'id="aiActions"' not in topbar
    assert "另存新版" not in html

    assert "编号会用于保存文件和周报标题" not in html
    assert "免费或试用模型通常也需要自己的 API Key" not in html
    assert "一条只写一个结果" not in html
    assert "写复盘、判断" not in html
    assert "摘要进入周报三列表格" not in html
    assert "这里显示最终周报样式" not in html
    assert "<p" not in html

    assert 'id="testAiBtn"' in basic_page
    assert 'id="polishBtn"' not in basic_page
    assert 'id="polishBtn"' in results_page
    assert 'id="testAiBtn"' not in results_page
    assert "const saveAsButton = $('saveAsBtn')" in app_js


def test_electron_basic_page_integrates_info_ai_and_inline_actions():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")

    basic_page = html.split('id="page-basic"', 1)[1].split('id="page-results"', 1)[0]

    assert basic_page.count('class="section-block') == 1
    assert 'class="section-block basic-integrated-panel"' in basic_page
    assert '<input id="reportIdInput" type="hidden" />' in basic_page
    assert 'class="identity-title"' not in basic_page
    assert 'class="title-field"' not in basic_page
    assert "<strong>周报信息</strong>" not in basic_page
    assert "<h1>名称</h1>" not in basic_page
    assert "<span>名称</span>" not in basic_page
    assert "<span>标题</span>" in basic_page
    assert "<strong>AI 接入</strong>" in basic_page
    assert "<span>可选</span>" in basic_page
    assert 'aria-label="名称"' not in basic_page
    assert 'aria-label="标题"' in basic_page
    assert "<span>总结</span>" in basic_page
    assert "<h2>AI 配置</h2>" not in basic_page
    assert "AI 配置" not in basic_page
    assert '<button id="testAiBtn" class="test-ai-action" type="button">测试 AI</button>' in basic_page
    assert '<button id="summaryPolishBtn" type="button">AI 润色总结</button>' in basic_page
    assert 'class="basic-form-grid"' in basic_page
    assert 'class="name-field"' in basic_page
    assert 'id="aiProviderInput"' not in basic_page
    assert 'class="provider-field"' not in basic_page
    assert 'class="base-url-field"' in basic_page
    assert 'class="test-ai-action"' in basic_page
    assert 'class="ai-optional-title"' in basic_page
    assert 'class="basic-info-fields"' not in basic_page
    assert 'class="basic-ai-fields"' not in basic_page
    assert 'class="basic-ai-grid"' not in basic_page
    assert basic_page.index('id="topicInput"') < basic_page.index('id="aiBaseUrlInput"') < basic_page.index('id="summaryInput"')
    assert "System Prompt" not in basic_page
    assert 'id="aiPromptInput"' not in basic_page
    assert "AI 润色本周感受" not in basic_page
    assert "一句话总结" not in basic_page
    assert ">主题<" not in basic_page

    assert '<aside class="action-rail"' not in html
    assert 'id="statusBar"' not in html
    assert "summaryPolishBtn" in app_js
    assert "provider: 'openai_compatible'" in app_js
    assert "aiProviderInput" not in app_js
    assert "section_key: 'basic_info'" in app_js
    assert ".basic-integrated-panel" in styles
    assert ".basic-form-grid" in styles
    assert "grid-template-columns: repeat(12, minmax(0, 1fr))" in styles
    assert "--accent: #2563eb" in styles
    assert ".basic-form-grid .name-field input" in styles
    assert "border: 1px solid var(--line)" in styles
    assert "grid-column: 1 / span 6" in styles
    assert "grid-column: 7 / -1" in styles
    assert "grid-row: 4" in styles
    assert ".basic-ai-grid" not in styles
    assert ".action-rail" not in styles


def test_electron_ai_actions_show_immediate_progress_state():
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")

    assert "async function runAiAction" in app_js
    assert "button.disabled = true" in app_js
    assert "setStatus(progressMessage)" in app_js
    assert "AI 正在测试连接..." in app_js
    assert "AI 正在润色总结..." in app_js
    assert "AI 正在润色本周感受..." in app_js


def test_electron_renderer_starts_from_data_file_library():
    html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")

    assert 'id="startScreen"' in html
    assert 'id="reportLibrary"' in html
    assert 'id="startOpenReportBtn"' in html
    assert 'id="newStemInput"' in html
    assert 'id="newReportForm"' in html
    assert "新建并进入" not in html
    assert "新建文件" in html
    assert 'id="exportBackupBtn"' in html
    assert "listReports" in app_js
    assert "exportDataBackup" in app_js
    assert "loadLibrary" in app_js
    assert "openReportFromDialog" in app_js
    assert "$('startOpenReportBtn').addEventListener('click', openReportFromDialog)" in app_js
    assert "data 文件夹里还没有周报数据。可以打开已有 JSON 文件，或新建一个文件。" in app_js
    assert "await bridge('createReport', { report_id: '1', topic: '' })" not in app_js

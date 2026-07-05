const DEFAULT_AI = {
  provider: 'openai_compatible',
  config: {
    base_url: '',
    api_key: '',
    model: '',
    system_prompt: '你是周报润色助手。请保留事实、数字和结构，只优化措辞，让表达更清晰、专业、简洁。',
  },
};

let state = null;
let currentSection = 'basic';
let projectMode = 'overview';
let selectedProjectIndex = 0;
let selectedImageIndex = -1;
let selectedRecordIndex = -1;
let renderTimer = null;
let transientStatus = '';
let libraryReports = [];
let editorOpen = false;

const $ = (id) => document.getElementById(id);
const api = createWeekflowApi();

function emptyReport() {
  return {
    schema_version: 2,
    report_id: '',
    cycle: '',
    topic: '',
    one_line_summary: '',
    preview_theme: 'report',
    overview: { mainline: '', mainlines: [], judgment: '', focus: '' },
    projects: [emptyProject()],
    achievements: [],
    todos: [],
    feeling: '',
    ai: clone(DEFAULT_AI),
  };
}

function emptyProject() {
  return { name: '', summary: '', issue: '', next_step: '', result_images: [], records: [] };
}

function emptyRecord() {
  return { date: '', time: '', name: '', change: '', result: '' };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function createWeekflowApi() {
  if (window.weekflow) return window.weekflow;

  let localReport = emptyReport();
  let localDirty = true;
  let localStem = 'weekly-report';

  return {
    async command(type, payload = {}) {
      if (type === 'createReport') {
        localReport = emptyReport();
        localReport.report_id = payload.report_id || '1';
        localReport.topic = payload.topic || '';
        localStem = payload.stem || localReport.report_id || 'weekly-report';
        localDirty = true;
      } else if (type === 'replaceReport') {
        localReport = clone(payload.report || emptyReport());
        localDirty = true;
      } else if (type === 'saveCurrent' || type === 'saveAsNamed') {
        if (payload.stem) localStem = payload.stem;
        localDirty = false;
      } else if (type === 'listReports') {
        return { ok: true, state: makeLocalState(localReport, localDirty, '', [], localStem) };
      } else if (type === 'testAi') {
        return { ok: true, state: makeLocalState(localReport, localDirty, '浏览器预览模式：请在 Electron 中测试真实 AI。') };
      } else if (type === 'polish') {
        if (payload.section_key === 'basic_info') {
          localReport.one_line_summary = localReport.one_line_summary || '已生成本周核心总结。';
        } else if (payload.section_key === 'feeling') {
          localReport.feeling = localReport.feeling || '本周推进节奏更清晰，下一步继续聚焦交付和验证。';
        }
        localDirty = true;
      }
      return { ok: true, state: makeLocalState(localReport, localDirty, '', [], localStem) };
    },
    async openReportDialog() {
      return null;
    },
    async pickImageDialog() {
      return null;
    },
    async exportBackupDialog() {
      return null;
    },
    async openPreviewWindow(html) {
      const win = window.open('', '_blank', 'width=980,height=720');
      if (win) {
        win.document.open();
        win.document.write(html || renderLocalHtml(renderLocalMarkdown(localReport)));
        win.document.close();
      }
      return true;
    },
  };
}

function makeLocalState(localReport, isDirty, aiMessage = '', availableReports = [], currentStem = 'weekly-report') {
  const markdown = renderLocalMarkdown(localReport);
  return {
    report: clone(localReport),
    title: localReport.report_id ? `Week ${localReport.report_id}` : '未命名周报',
    markdown,
    preview_html: renderLocalHtml(markdown),
    is_dirty: isDirty,
    default_directory: '',
    current_json_path: null,
    current_markdown_path: null,
    current_stem: currentStem || localReport.report_id || 'weekly-report',
    available_reports: availableReports,
    ai_test_message: aiMessage,
  };
}

function renderLocalMarkdown(localReport) {
  const lines = [
    `# Week ${localReport.report_id || ''}`.trim(),
    '',
    localReport.topic ? `主题：${localReport.topic}` : '',
    localReport.one_line_summary ? `> ${localReport.one_line_summary}` : '',
    '',
    '## 本周成果',
    ...(localReport.achievements || []).map((item) => `- ${item}`),
    '',
    '## 项目进展',
    ...(localReport.projects || []).map((project) => `- ${project.name || '未命名项目'}：${project.summary || '暂无进展'}；下一步：${project.next_step || '待补充'}`),
    '',
    '## 待跟进',
    ...(localReport.todos || []).map((item) => `- ${item.done ? '[x]' : '[ ]'} ${item.text}`),
    '',
    '## 本周感受',
    localReport.feeling || '',
  ];
  return lines.filter((line, index, arr) => line || arr[index - 1]).join('\n');
}

function renderLocalHtml(markdown) {
  const body = escapeHtml(markdown)
    .replace(/^# (.*)$/gm, '<h1>$1</h1>')
    .replace(/^## (.*)$/gm, '<h2>$1</h2>')
    .replace(/^- (.*)$/gm, '<li>$1</li>')
    .replace(/\n/g, '<br />');
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>body{font-family:Microsoft YaHei UI, sans-serif;line-height:1.7;color:#18324c;padding:32px;}h1,h2{color:#12375a;}li{margin:6px 0;}</style></head><body>${body}</body></html>`;
}

function report() {
  return state?.report || emptyReport();
}

function currentProject() {
  const projects = report().projects || [];
  return projects[selectedProjectIndex] || null;
}

function normalizeSelection() {
  const currentReport = report();
  if (!Array.isArray(currentReport.projects)) currentReport.projects = [];
  if (!currentReport.projects.length) currentReport.projects.push(emptyProject());
  selectedProjectIndex = clamp(selectedProjectIndex, 0, currentReport.projects.length - 1);

  const project = currentProject();
  const imageCount = project?.result_images?.length || 0;
  const recordCount = project?.records?.length || 0;
  selectedImageIndex = imageCount ? clamp(selectedImageIndex, -1, imageCount - 1) : -1;
  selectedRecordIndex = recordCount ? clamp(selectedRecordIndex, -1, recordCount - 1) : -1;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function setStatus(message) {
  transientStatus = message;
  const node = $('statusBar');
  if (node) node.textContent = message;
  const inlineNode = $('aiInlineStatus');
  if (inlineNode) inlineNode.textContent = message || '';
}

async function bridge(type, payload = {}, options = {}) {
  const result = await api.command(type, payload);
  if (!result.ok) {
    const message = result.error?.message || '操作失败';
    setStatus(message);
    throw new Error(message);
  }
  state = result.state;
  libraryReports = state.available_reports || [];
  transientStatus = state.ai_test_message || '';
  normalizeSelection();
  if (type === 'createReport' || type === 'openReport' || options.openEditor) {
    editorOpen = true;
  }
  if (editorOpen) {
    render();
  } else {
    renderStartScreen();
  }
  return state;
}

async function loadLibrary() {
  editorOpen = false;
  await bridge('listReports', {}, { openEditor: false });
}

function renderStartScreen() {
  const shell = document.querySelector('.app-shell');
  shell?.classList.toggle('library-mode', !editorOpen);
  $('reportTitle').textContent = 'WeekFlow';
  document.title = 'WeekFlow';
  const hint = $('dataDirectoryHint');
  if (hint && state?.default_directory) {
    hint.textContent = `${state.default_directory}\\data`;
  }
  renderReportLibrary();
}

function setBackupStatus(message) {
  const node = $('backupStatus');
  if (node) node.textContent = message || '';
}

function renderReportLibrary() {
  const container = $('reportLibrary');
  if (!container) return;
  if (!libraryReports.length) {
    container.innerHTML = '<div class="empty-library">data 文件夹里还没有周报数据。可以打开已有 JSON 文件，或新建一个文件。</div>';
    return;
  }
  container.innerHTML = libraryReports.map((item) => {
    const title = item.topic?.trim() || item.stem || item.name;
    const reportId = item.report_id ? `编号：${item.report_id}` : '编号：未填写';
    const fileName = `文件：data/${item.name}`;
    return `
      <div class="report-file-row">
        <div>
          <p class="report-file-title">${escapeHtml(title)}</p>
          <div class="report-file-meta">${escapeHtml(fileName)} · ${escapeHtml(reportId)}</div>
        </div>
        <button type="button" data-open-report-path="${escapeAttr(item.path)}">打开</button>
      </div>
    `;
  }).join('');
}

function updateReport(mutator, shouldRender = true) {
  const nextReport = clone(report());
  mutator(nextReport);
  state = {
    ...(state || {}),
    report: nextReport,
    is_dirty: true,
  };
  normalizeSelection();
  if (shouldRender) render();
  updateStatusText();
  queueReplaceReport();
}

function updateCurrentProject(mutator, shouldRender = true) {
  updateReport((nextReport) => {
    if (!Array.isArray(nextReport.projects)) nextReport.projects = [];
    if (!nextReport.projects.length) nextReport.projects.push(emptyProject());
    mutator(nextReport.projects[selectedProjectIndex]);
  }, shouldRender);
}

function queueReplaceReport() {
  window.clearTimeout(renderTimer);
  renderTimer = window.setTimeout(() => {
    bridge('replaceReport', { report: report() }).catch((error) => {
      console.error(error);
      setStatus(error.message);
    });
  }, 420);
}

function render() {
  if (!state) return;
  document.querySelector('.app-shell')?.classList.toggle('library-mode', false);
  const currentReport = report();
  renderChrome(currentReport);
  renderPageVisibility();
  renderBasic(currentReport);
  renderResults(currentReport);
  renderProjects(currentReport);
  renderTodos(currentReport);
  renderPreview(currentReport);
  updateStatusText();
}

function renderChrome(currentReport) {
  $('reportTitle').textContent = currentReport.topic?.trim() || 'WeekFlow';
  document.title = currentReport.topic?.trim() || 'WeekFlow';
  document.querySelectorAll('#sectionTabs button').forEach((button) => {
    button.classList.toggle('active', button.dataset.section === currentSection);
  });
}

function renderPageVisibility() {
  document.querySelectorAll('.page').forEach((page) => {
    page.classList.toggle('active', page.id === `page-${currentSection}`);
  });
}

function renderBasic(currentReport) {
  setValue('reportIdInput', currentReport.report_id);
  setValue('topicInput', currentReport.topic);
  setValue('summaryInput', currentReport.one_line_summary);

  const ai = currentReport.ai || clone(DEFAULT_AI);
  const config = ai.config || {};
  setValue('aiBaseUrlInput', config.base_url);
  setValue('aiKeyInput', config.api_key);
  setValue('aiModelInput', config.model);
  const aiPromptInput = $('aiPromptInput');
  if (aiPromptInput) {
    setValue('aiPromptInput', config.system_prompt || DEFAULT_AI.config.system_prompt);
  }
}

function renderResults(currentReport) {
  renderAchievements(currentReport.achievements || []);
  setValue('feelingInput', currentReport.feeling);
}

function renderAchievements(items) {
  const container = $('achievementsList');
  if (!items.length) {
    container.innerHTML = '<div class="empty-state">还没有成果，先在上方添加一条。</div>';
    return;
  }
  container.innerHTML = items.map((item, index) => `
    <div class="list-row" data-index="${index}">
      <input data-achievement-index="${index}" value="${escapeAttr(item)}" />
      <button data-remove-achievement="${index}">删除</button>
    </div>
  `).join('');
  container.querySelectorAll('input[data-achievement-index]').forEach((input) => {
    input.addEventListener('input', (event) => {
      const index = Number(event.target.dataset.achievementIndex);
      updateReport((nextReport) => {
        nextReport.achievements[index] = event.target.value;
      }, false);
    });
  });
  container.querySelectorAll('button[data-remove-achievement]').forEach((button) => {
    button.addEventListener('click', () => {
      const index = Number(button.dataset.removeAchievement);
      updateReport((nextReport) => nextReport.achievements.splice(index, 1));
    });
  });
}

function renderProjects(currentReport) {
  renderProjectList(currentReport.projects || []);
  renderProjectModeTabs();
  renderProjectPanes();
}

function renderProjectList(projects) {
  const container = $('projectList');
  container.innerHTML = projects.map((project, index) => {
    const title = project.name?.trim() || `未命名项目 ${index + 1}`;
    const summary = project.summary?.trim() || '暂无本周推进';
    const next = project.next_step?.trim() || '下一步待补充';
    const meta = `${project.records?.length || 0} 条流水 · ${project.result_images?.length || 0} 张图片`;
    return `
      <div class="project-row ${index === selectedProjectIndex ? 'active' : ''}" data-project-index="${index}">
        <div class="project-index">${index + 1}</div>
        <div>
          <div class="project-name">${escapeHtml(title)}</div>
          <div class="project-summary-line">${escapeHtml(summary)}</div>
          <div class="project-next-line">${escapeHtml(next)}</div>
          <div class="project-meta">${escapeHtml(meta)}</div>
        </div>
      </div>
    `;
  }).join('');
  container.querySelectorAll('[data-project-index]').forEach((row) => {
    row.addEventListener('click', () => {
      selectedProjectIndex = Number(row.dataset.projectIndex);
      selectedImageIndex = -1;
      selectedRecordIndex = -1;
      render();
    });
  });
}

function renderProjectModeTabs() {
  document.querySelectorAll('#projectModeTabs button').forEach((button) => {
    button.classList.toggle('active', button.dataset.projectMode === projectMode);
  });
  document.querySelectorAll('.project-pane').forEach((pane) => {
    const mode = pane.id.replace('project', '').toLowerCase();
    pane.classList.toggle('active', mode === projectMode);
  });
}

function renderProjectPanes() {
  const project = currentProject() || emptyProject();
  renderProjectOverview(project);
  setValue('projectNameInput', project.name);
  setValue('projectSummaryInput', project.summary);
  setValue('projectNextInput', project.next_step);
  setValue('projectResultInput', project.issue);
  renderProjectImages(project);
  renderRecords(project);
}

function renderProjectOverview(project) {
  $('projectOverview').innerHTML = `
    <div class="project-overview">
      <div class="overview-title">
        <h2>${escapeHtml(project.name || '未命名项目')}</h2>
        <div class="overview-badges">
          <span>${project.records?.length || 0} 条流水</span>
          <span>${project.result_images?.length || 0} 张图片</span>
        </div>
      </div>
      <div class="overview-grid">
        <section class="overview-item">
          <h3>本周推进</h3>
          <p>${escapeHtml(project.summary || '还没有填写。切到“填写进展”补充本周实际推进。')}</p>
        </section>
        <section class="overview-item">
          <h3>下一步</h3>
          <p>${escapeHtml(project.next_step || '还没有填写。建议写清谁来做、什么时候验证。')}</p>
        </section>
        <section class="overview-item">
          <h3>结果沉淀</h3>
          <p>${escapeHtml(project.issue || '还没有结果说明。交付链接、截图说明、最终结论都放这里。')}</p>
        </section>
      </div>
    </div>
  `;
}

function renderProjectImages(project) {
  const images = project.result_images || [];
  const container = $('projectImages');
  if (!images.length) {
    container.innerHTML = '<div class="empty-state">暂无图片。先保存周报后可导入截图。</div>';
    return;
  }
  container.innerHTML = images.map((image, index) => `
    <div class="image-row ${index === selectedImageIndex ? 'active' : ''}" data-image-index="${index}">
      ${escapeHtml(image)}
    </div>
  `).join('');
  container.querySelectorAll('[data-image-index]').forEach((row) => {
    row.addEventListener('click', () => {
      selectedImageIndex = Number(row.dataset.imageIndex);
      renderProjectImages(project);
    });
  });
}

function renderRecords(project) {
  const records = project.records || [];
  const body = $('recordsBody');
  if (!records.length) {
    body.innerHTML = '<tr><td colspan="5" class="empty-cell">暂无流水，点击“新增记录”后填写。</td></tr>';
    return;
  }
  body.innerHTML = records.map((record, index) => `
    <tr data-record-index="${index}" class="${index === selectedRecordIndex ? 'active' : ''}">
      <td><input data-record-field="date" value="${escapeAttr(record.date || '')}" placeholder="7/1" /></td>
      <td><input data-record-field="time" value="${escapeAttr(record.time || '')}" placeholder="10:30" /></td>
      <td><input data-record-field="name" value="${escapeAttr(record.name || '')}" placeholder="会议 / 验收" /></td>
      <td><input data-record-field="change" value="${escapeAttr(record.change || '')}" placeholder="发生了什么" /></td>
      <td><input data-record-field="result" value="${escapeAttr(record.result || '')}" placeholder="结论或结果" /></td>
    </tr>
  `).join('');
}

function renderTodos(currentReport) {
  const todos = currentReport.todos || [];
  const container = $('todoList');
  if (!todos.length) {
    container.innerHTML = '<div class="empty-state">没有待跟进事项。</div>';
    return;
  }
  container.innerHTML = todos.map((item, index) => `
    <div class="list-row todo-row" data-index="${index}">
      <input type="checkbox" data-todo-done="${index}" ${item.done ? 'checked' : ''} />
      <input data-todo-text="${index}" value="${escapeAttr(item.text)}" />
      <button data-remove-todo="${index}">删除</button>
    </div>
  `).join('');
  container.querySelectorAll('[data-todo-done]').forEach((checkbox) => {
    checkbox.addEventListener('change', (event) => {
      const index = Number(event.target.dataset.todoDone);
      updateReport((nextReport) => {
        nextReport.todos[index].done = event.target.checked;
      }, false);
    });
  });
  container.querySelectorAll('[data-todo-text]').forEach((input) => {
    input.addEventListener('input', (event) => {
      const index = Number(event.target.dataset.todoText);
      updateReport((nextReport) => {
        nextReport.todos[index].text = event.target.value;
      }, false);
    });
  });
  container.querySelectorAll('[data-remove-todo]').forEach((button) => {
    button.addEventListener('click', () => {
      const index = Number(button.dataset.removeTodo);
      updateReport((nextReport) => nextReport.todos.splice(index, 1));
    });
  });
}

function renderPreview(currentReport) {
  setValue('previewThemeInput', currentReport.preview_theme || 'report');
  $('markdownOutput').value = state.markdown || '';
  $('previewFrame').srcdoc = state.preview_html || renderLocalHtml(state.markdown || '');
}

function updateStatusText() {
  const statusNode = $('statusBar');
  const inlineNode = $('aiInlineStatus');
  if (inlineNode) {
    inlineNode.textContent = transientStatus || '';
  }
  if (transientStatus) {
    if (statusNode) statusNode.textContent = transientStatus;
    return;
  }
  if (statusNode) statusNode.textContent = state?.is_dirty ? '有未保存修改' : '已保存';
}

function setValue(id, value) {
  const node = $(id);
  if (!node) return;
  const nextValue = value ?? '';
  if (node.value !== nextValue) node.value = nextValue;
}

function sectionPayload() {
  const sectionMap = {
    basic: 'basic_info',
    results: 'overview',
    projects: 'projects',
    todos: 'todos',
    preview: 'preview',
  };
  return {
    section_key: sectionMap[currentSection] || 'preview',
    project_index: currentSection === 'projects' ? selectedProjectIndex : null,
  };
}

function bindInputs() {
  $('reportIdInput').addEventListener('input', (event) => updateReport((nextReport) => {
    nextReport.report_id = event.target.value;
  }, false));
  $('topicInput').addEventListener('input', (event) => updateReport((nextReport) => {
    nextReport.topic = event.target.value;
  }, false));
  $('summaryInput').addEventListener('input', (event) => updateReport((nextReport) => {
    nextReport.one_line_summary = event.target.value;
  }, false));
  $('feelingInput').addEventListener('input', (event) => updateReport((nextReport) => {
    nextReport.feeling = event.target.value;
  }, false));
  $('aiBaseUrlInput').addEventListener('input', (event) => updateAiConfig('base_url', event.target.value));
  $('aiKeyInput').addEventListener('input', (event) => updateAiConfig('api_key', event.target.value));
  $('aiModelInput').addEventListener('input', (event) => updateAiConfig('model', event.target.value));
  const aiPromptInput = $('aiPromptInput');
  if (aiPromptInput) {
    aiPromptInput.addEventListener('input', (event) => updateAiConfig('system_prompt', event.target.value));
  }
  $('previewThemeInput').addEventListener('change', (event) => updateReport((nextReport) => {
    nextReport.preview_theme = event.target.value;
  }, false));

  $('projectNameInput').addEventListener('input', (event) => updateCurrentProject((project) => {
    project.name = event.target.value;
  }, false));
  $('projectSummaryInput').addEventListener('input', (event) => updateCurrentProject((project) => {
    project.summary = event.target.value;
  }, false));
  $('projectNextInput').addEventListener('input', (event) => updateCurrentProject((project) => {
    project.next_step = event.target.value;
  }, false));
  $('projectResultInput').addEventListener('input', (event) => updateCurrentProject((project) => {
    project.issue = event.target.value;
  }, false));
}

function updateAiConfig(key, value) {
  updateReport((nextReport) => {
    nextReport.ai = nextReport.ai || clone(DEFAULT_AI);
    nextReport.ai.provider = 'openai_compatible';
    nextReport.ai.config = nextReport.ai.config || clone(DEFAULT_AI.config);
    nextReport.ai.config[key] = value;
  }, false);
}

async function openReportFromDialog() {
  const path = await api.openReportDialog();
  if (path) await bridge('openReport', { path });
}

async function runAiAction(button, progressMessage, command, payload, successMessage) {
  if (button.disabled) return;
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = progressMessage.replace(/^AI 正在/, '');
  setStatus(progressMessage);
  try {
    await bridge(command, payload);
    if (successMessage) setStatus(successMessage);
  } catch (error) {
    setStatus(error?.message || 'AI 操作失败，请检查接口配置。');
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

function bindActions() {
  $('refreshLibraryBtn').addEventListener('click', () => loadLibrary());
  $('startOpenReportBtn').addEventListener('click', openReportFromDialog);
  $('exportBackupBtn').addEventListener('click', async () => {
    const path = await api.exportBackupDialog();
    if (!path) return;
    const nextState = await bridge('exportDataBackup', { path });
    setBackupStatus(`已导出：${nextState.backup_path || path}`);
  });
  $('reportLibrary').addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-open-report-path]');
    if (!button) return;
    await bridge('openReport', { path: button.dataset.openReportPath });
  });
  $('newReportForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const stem = $('newStemInput').value.trim();
    if (!stem) {
      setStatus('请先填写文件名');
      $('newStemInput').focus();
      return;
    }
    const reportId = $('newReportIdInput').value.trim() || stem;
    const topic = $('newTopicInput').value.trim();
    await bridge('createReport', { stem, report_id: reportId, topic });
    await bridge('saveCurrent');
  });

  $('sectionTabs').addEventListener('click', (event) => {
    const button = event.target.closest('button[data-section]');
    if (!button) return;
    currentSection = button.dataset.section;
    render();
  });

  $('projectModeTabs').addEventListener('click', (event) => {
    const button = event.target.closest('button[data-project-mode]');
    if (!button) return;
    projectMode = button.dataset.projectMode;
    render();
  });

  $('newReportBtn').addEventListener('click', async () => {
    await loadLibrary();
  });
  $('openReportBtn').addEventListener('click', openReportFromDialog);
  $('saveBtn').addEventListener('click', () => bridge('saveCurrent'));
  const saveAsButton = $('saveAsBtn');
  if (saveAsButton) {
    saveAsButton.addEventListener('click', () => {
      const stem = window.prompt('请输入新文件名，不含扩展名', state?.current_stem || report().report_id || 'weekly-report');
      if (stem) bridge('saveAsNamed', { stem });
    });
  }
  $('polishBtn').addEventListener('click', () => runAiAction(
    $('polishBtn'),
    'AI 正在润色本周感受...',
    'polish',
    { section_key: 'feeling', project_index: null },
    '已润色本周感受',
  ));
  $('summaryPolishBtn').addEventListener('click', () => runAiAction(
    $('summaryPolishBtn'),
    'AI 正在润色总结...',
    'polish',
    { section_key: 'basic_info', project_index: null },
    '已润色总结',
  ));
  $('testAiBtn').addEventListener('click', () => runAiAction(
    $('testAiBtn'),
    'AI 正在测试连接...',
    'testAi',
    {},
    '',
  ));
  $('openPreviewBtn').addEventListener('click', async () => {
    if (api.openPreviewWindow) {
      await api.openPreviewWindow(state?.preview_html || '');
    } else {
      window.open('', '_blank');
    }
  });

  $('addAchievementBtn').addEventListener('click', () => {
    const value = $('achievementInput').value.trim();
    if (!value) return;
    updateReport((nextReport) => nextReport.achievements.push(value));
    $('achievementInput').value = '';
  });
  $('addTodoBtn').addEventListener('click', () => {
    const value = $('todoInput').value.trim();
    if (!value) return;
    updateReport((nextReport) => nextReport.todos.push({ done: false, text: value }));
    $('todoInput').value = '';
  });
  $('addProjectBtn').addEventListener('click', () => updateReport((nextReport) => {
    nextReport.projects.push(emptyProject());
    selectedProjectIndex = nextReport.projects.length - 1;
    projectMode = 'progress';
  }));
  $('deleteProjectBtn').addEventListener('click', () => updateReport((nextReport) => {
    if (selectedProjectIndex >= 0) nextReport.projects.splice(selectedProjectIndex, 1);
    if (!nextReport.projects.length) nextReport.projects.push(emptyProject());
    selectedProjectIndex = clamp(selectedProjectIndex, 0, nextReport.projects.length - 1);
  }));
  $('moveProjectUpBtn').addEventListener('click', () => moveProject(-1));
  $('moveProjectDownBtn').addEventListener('click', () => moveProject(1));
  $('addRecordBtn').addEventListener('click', () => updateCurrentProject((project) => {
    project.records = project.records || [];
    project.records.push(emptyRecord());
    selectedRecordIndex = project.records.length - 1;
  }));
  $('deleteRecordBtn').addEventListener('click', () => updateCurrentProject((project) => {
    if (selectedRecordIndex >= 0) project.records.splice(selectedRecordIndex, 1);
    selectedRecordIndex = -1;
  }));
  $('addProjectImageBtn').addEventListener('click', async () => {
    const path = await api.pickImageDialog();
    if (path) await bridge('importProjectImage', { project_index: selectedProjectIndex, source_path: path });
  });
  $('removeProjectImageBtn').addEventListener('click', async () => {
    const project = currentProject();
    if (!project || selectedImageIndex < 0) return;
    await bridge('removeProjectImage', {
      project_index: selectedProjectIndex,
      relative_path: project.result_images[selectedImageIndex],
    });
  });

  $('recordsBody').addEventListener('click', (event) => {
    const row = event.target.closest('tr[data-record-index]');
    if (!row) return;
    selectedRecordIndex = Number(row.dataset.recordIndex);
    renderRecords(currentProject() || emptyProject());
  });
  $('recordsBody').addEventListener('input', (event) => {
    const input = event.target.closest('input[data-record-field]');
    if (!input) return;
    const row = input.closest('tr[data-record-index]');
    const index = Number(row.dataset.recordIndex);
    const field = input.dataset.recordField;
    updateCurrentProject((project) => {
      project.records[index][field] = input.value;
    }, false);
  });
}

function moveProject(delta) {
  updateReport((nextReport) => {
    const target = selectedProjectIndex + delta;
    if (selectedProjectIndex < 0 || target < 0 || target >= nextReport.projects.length) return;
    const temp = nextReport.projects[selectedProjectIndex];
    nextReport.projects[selectedProjectIndex] = nextReport.projects[target];
    nextReport.projects[target] = temp;
    selectedProjectIndex = target;
  });
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, '&#096;');
}

async function boot() {
  bindInputs();
  bindActions();
  await loadLibrary();
}

boot().catch((error) => {
  console.error(error);
  setStatus(error.message);
});

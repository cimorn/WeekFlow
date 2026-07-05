const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const readline = require('readline');

let mainWindow = null;
let previewWindow = null;
let bridge = null;
let bridgeLines = null;
const pendingBridgeCalls = [];

const gotSingleInstanceLock = app.requestSingleInstanceLock();

if (!gotSingleInstanceLock) {
  app.quit();
}

function projectRoot() {
  return app.isPackaged ? process.resourcesPath : path.resolve(__dirname, '..');
}

function packagedBridgePath() {
  return path.join(process.resourcesPath, 'bridge', 'WeekFlowBridge.exe');
}

function appIconPath() {
  return path.join(app.getAppPath(), 'src', 'weekflow_logo.ico');
}

function appDefaultDirectory() {
  return app.isPackaged ? path.dirname(process.execPath) : projectRoot();
}

function backupFileName() {
  const now = new Date();
  const stamp = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, '0'),
    String(now.getDate()).padStart(2, '0'),
    '-',
    String(now.getHours()).padStart(2, '0'),
    String(now.getMinutes()).padStart(2, '0'),
    String(now.getSeconds()).padStart(2, '0'),
  ].join('');
  return `WeekFlow-data-backup-${stamp}.zip`;
}

function startBridge() {
  if (bridge) return;

  const cwd = projectRoot();
  const defaultDirectory = appDefaultDirectory();
  const env = { ...process.env };
  env.PYTHONIOENCODING = 'utf-8';

  let command;
  let args;
  if (app.isPackaged) {
    command = packagedBridgePath();
    args = [defaultDirectory];
  } else {
    command = process.env.WEEKFLOW_PYTHON || 'python';
    env.PYTHONPATH = path.join(cwd, 'src');
    args = ['-m', 'WeekFlow.electron_bridge', defaultDirectory];
  }

  bridge = spawn(command, args, {
    cwd,
    env,
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });

  bridgeLines = readline.createInterface({ input: bridge.stdout });
  bridgeLines.on('line', (line) => {
    const pending = pendingBridgeCalls.shift();
    if (!pending) return;
    try {
      pending.resolve(JSON.parse(line));
    } catch (error) {
      pending.reject(error);
    }
  });

  bridge.stderr.on('data', (chunk) => {
    console.error(`[WeekFlow bridge] ${chunk.toString()}`);
  });

  bridge.on('exit', (code) => {
    bridge = null;
    while (pendingBridgeCalls.length) {
      pendingBridgeCalls.shift().reject(new Error(`Python bridge exited with code ${code}`));
    }
  });
}

function callBridge(message) {
  startBridge();
  return new Promise((resolve, reject) => {
    pendingBridgeCalls.push({ resolve, reject });
    bridge.stdin.write(`${JSON.stringify(message)}\n`, 'utf8', (error) => {
      if (error) {
        pendingBridgeCalls.pop();
        reject(error);
      }
    });
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 860,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: '#eef3f8',
    title: 'WeekFlow',
    icon: appIconPath(),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function focusMainWindow() {
  if (!mainWindow || mainWindow.isDestroyed()) {
    createWindow();
    return;
  }
  if (mainWindow.isMinimized()) mainWindow.restore();
  mainWindow.show();
  mainWindow.focus();
}

function openPreviewWindow(html) {
  if (!previewWindow || previewWindow.isDestroyed()) {
    previewWindow = new BrowserWindow({
      width: 980,
      height: 720,
      minWidth: 720,
      minHeight: 560,
      backgroundColor: '#ffffff',
      icon: appIconPath(),
      title: 'WeekFlow 预览',
      autoHideMenuBar: true,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
      },
    });
    previewWindow.on('closed', () => {
      previewWindow = null;
    });
  }
  previewWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html || '')}`);
  previewWindow.focus();
  return true;
}

if (gotSingleInstanceLock) {
  app.whenReady().then(() => {
    Menu.setApplicationMenu(null);
    ipcMain.handle('bridge:command', (_event, message) => callBridge(message));
    ipcMain.handle('dialog:openReport', async () => {
      const result = await dialog.showOpenDialog(mainWindow, {
        title: '打开周报 JSON',
        defaultPath: path.join(appDefaultDirectory(), 'data'),
        filters: [{ name: 'WeekFlow JSON', extensions: ['json'] }],
        properties: ['openFile'],
      });
      return result.canceled ? null : result.filePaths[0];
    });
    ipcMain.handle('dialog:pickImage', async () => {
      const result = await dialog.showOpenDialog(mainWindow, {
        title: '选择结果图片',
        filters: [{ name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'webp', 'bmp'] }],
        properties: ['openFile'],
      });
      return result.canceled ? null : result.filePaths[0];
    });
    ipcMain.handle('dialog:exportBackup', async () => {
      const result = await dialog.showSaveDialog(mainWindow, {
        title: '导出数据备份',
        defaultPath: path.join(appDefaultDirectory(), backupFileName()),
        filters: [{ name: 'Zip backup', extensions: ['zip'] }],
      });
      return result.canceled ? null : result.filePath;
    });
    ipcMain.handle('preview:open', (_event, html) => openPreviewWindow(html));
    createWindow();
  });

  app.on('second-instance', () => {
    focusMainWindow();
  });

  app.on('window-all-closed', () => {
    if (bridge) bridge.kill();
    if (process.platform !== 'darwin') app.quit();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
}

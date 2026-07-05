const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('weekflow', {
  command(type, payload = {}) {
    return ipcRenderer.invoke('bridge:command', { type, payload });
  },
  openReportDialog() {
    return ipcRenderer.invoke('dialog:openReport');
  },
  pickImageDialog() {
    return ipcRenderer.invoke('dialog:pickImage');
  },
  exportBackupDialog() {
    return ipcRenderer.invoke('dialog:exportBackup');
  },
  openPreviewWindow(html) {
    return ipcRenderer.invoke('preview:open', html);
  },
});

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('overlayAPI', {
  platform: process.platform,
  resizeWindow: (width, height) => ipcRenderer.invoke('resize-window', width, height),
  getWindowSize: () => ipcRenderer.invoke('get-window-size')
});

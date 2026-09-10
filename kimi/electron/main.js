const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 420,
    height: 620,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'overlay', 'index.html'));
  mainWindow.setAlwaysOnTop(true, 'screen-saver');
}

app.whenReady().then(() => {
  createWindow();

  // Register IPC handler for resizing
  ipcMain.handle('resize-window', (event, width, height) => {
    console.log(`[IPC] Resizing window to ${width}x${height}`);
    if (mainWindow && width >= 300 && width <= 1200 && height >= 400 && height <= 1000) {
      mainWindow.setSize(width, height);
      return { success: true, width, height };
    }
    return { success: false };
  });

  // Register IPC handler for getting current size
  ipcMain.handle('get-window-size', () => {
    if (mainWindow) {
      const [w, h] = mainWindow.getSize();
      return { width: w, height: h };
    }
    return { width: 420, height: 620 };
  });

  // Register Alt+Shift+D to toggle overlay visibility
  globalShortcut.register('Alt+Shift+D', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

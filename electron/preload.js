const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('overlayAPI', {
  searchItems: async (query) => {
    const res = await fetch(`http://127.0.0.1:5000/api/search?q=${encodeURIComponent(query)}`);
    return await res.json();
  },
  getItemDetail: async (id) => {
    const res = await fetch(`http://127.0.0.1:5000/api/items/${id}`);
    return await res.json();
  },
  getRecipeBreakdown: async (id, qty = 1) => {
    const res = await fetch(`http://127.0.0.1:5000/api/recipes/breakdown/${id}?qty=${qty}`);
    return await res.json();
  }
});

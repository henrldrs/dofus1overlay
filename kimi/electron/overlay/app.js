const API_BASE = 'http://localhost:5000/api';
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const itemDetails = document.getElementById('itemDetails');
const welcome = document.getElementById('welcome');

let debounceTimer;
searchInput.addEventListener('input', (e) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => handleSearch(e.target.value), 300);
});

async function handleSearch(query) {
  if (!query || query.length < 2) {
    searchResults.classList.add('hidden');
    itemDetails.classList.add('hidden');
    welcome.classList.remove('hidden');
    return;
  }
  
  welcome.classList.add('hidden');
  itemDetails.classList.add('hidden');
  searchResults.classList.remove('hidden');
  
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  const data = await res.json();
  
  searchResults.innerHTML = data.map(item => `
    <div class="result-item" onclick="showItem(${item.id})">
      <strong>${item.name}</strong> <span style="color:#888">[Lvl ${item.level}]</span>
    </div>
  `).join('');
}

async function showItem(itemId) {
  searchResults.classList.add('hidden');
  itemDetails.classList.remove('hidden');
  
  const res = await fetch(`${API_BASE}/items/${itemId}`);
  const data = await res.json();
  
  // Calculate recipe tree
  const calcRes = await fetch(`${API_BASE}/calculate?item_id=${itemId}&quantity=1`);
  const calcData = await calcRes.json();

  itemDetails.innerHTML = `
    <h3>${data.name} <span style="color:#888; font-size:14px">[Lvl ${data.level}]</span></h3>
    <p style="color:#aaa; font-size:12px">${data.type}</p>
    <h4>Stats</h4>
    ${Object.entries(data.stats).map(([k, v]) => `<div class="stat-row"><span>${k}</span><span>+${v}</span></div>`).join('')}
    
    <h4>Recipe (1x)</h4>
    <ul style="padding-left: 20px;">
      ${data.recipe.map(r => `<li class="recipe-item" onclick="showItem(${r.ingredient_id})">${r.quantity}x ${r.ingredient_name}</li>`).join('') || '<li>None</li>'}
    </ul>

    <h4>Total Resources Needed (1x)</h4>
    <ul style="padding-left: 20px; color: #2ecc71;">
      ${calcData.resources.map(r => `<li>${r.quantity}x ${r.name}</li>`).join('') || '<li>None</li>'}
    </ul>

    <button onclick="backToSearch()" style="margin-top:10px; padding:5px 10px; background:#444; color:#fff; border:none; cursor:pointer;">Back</button>
  `;
}

function backToSearch() {
  itemDetails.classList.add('hidden');
  welcome.classList.remove('hidden');
  searchInput.value = '';
}
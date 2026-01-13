/* floor-finder.js - Feature for finding locations without knowing the floor
   This is an ADDITIVE feature that doesn't modify existing logic
*/

// Global state for floor finder
let floorFinderActive = false;

/**
 * Search for a location across all floors
 * @param {string} query - The search query
 * @returns {Array} - Array of matching nodes with floor information
 */
function searchAcrossAllFloors(query) {
    if (!query || !nodes) return [];

    query = query.trim().toLowerCase();

    // Search through all nodes regardless of floor
    const matches = nodes.filter(n => {
        // Exclude corridors from cross-floor search
        if ((n.type || '').toLowerCase() === 'corridor') return false;

        const label = (n.name || n.id || '').toLowerCase();
        return label.includes(query);
    });

    // Sort by relevance (exact matches first, then by floor order)
    matches.sort((a, b) => {
        const aLabel = (a.name || a.id || '').toLowerCase();
        const bLabel = (b.name || b.id || '').toLowerCase();

        // Exact matches first
        if (aLabel === query && bLabel !== query) return -1;
        if (bLabel === query && aLabel !== query) return 1;

        // Then by floor order
        const aFloorIdx = FLOOR_ORDER.indexOf(a.floor);
        const bFloorIdx = FLOOR_ORDER.indexOf(b.floor);
        return aFloorIdx - bFloorIdx;
    });

    return matches.slice(0, 25); // Limit results
}

/**
 * Render cross-floor search results
 * @param {string} role - 'start' or 'end'
 * @param {Array} results - Array of node results
 */
function renderCrossFloorResults(role, results) {
    const container = role === 'start' ? $('#startResults') : $('#endResults');
    container.innerHTML = '';

    if (!results || !results.length) {
        container.innerHTML = '<div class="text-xs text-slate-400 p-2">No locations found</div>';
        return;
    }

    results.forEach(n => {
        const div = document.createElement('div');
        div.className = 'result-item';

        // Highlight floor information prominently
        const floorLabel = { 'G': 'Ground', '1': 'First', '2': 'Second', '3': 'Third' }[n.floor] || n.floor;

        div.innerHTML = `
      <div class="result-name">${n.name || n.id}</div>
      <div class="result-meta">
        <span class="font-semibold text-navy">${floorLabel} Floor</span> • ${n.type}
      </div>
    `;

        div.addEventListener('click', () => {
            if (role === 'start') {
                $('#startSearch').value = n.name || n.id;
                $('#startSearch').dataset.nodeId = n.id;
            } else {
                $('#endSearch').value = n.name || n.id;
                $('#endSearch').dataset.nodeId = n.id;
            }

            // Automatically switch to the floor where the location is
            if (currentFloor !== n.floor) {
                setFloor(n.floor);
            }

            container.innerHTML = '';
            floorFinderActive = false;
            updateFloorFinderUI(role, false);
        });

        container.appendChild(div);
    });
}

/**
 * Toggle floor finder mode for a search input
 * @param {string} role - 'start' or 'end'
 */
function toggleFloorFinder(role) {
    floorFinderActive = !floorFinderActive;
    updateFloorFinderUI(role, floorFinderActive);

    if (floorFinderActive) {
        const input = role === 'start' ? $('#startSearch') : $('#endSearch');
        const query = input.value;

        if (query) {
            const results = searchAcrossAllFloors(query);
            renderCrossFloorResults(role, results);
        }
    }
}

/**
 * Update UI to show floor finder is active
 * @param {string} role - 'start' or 'end'
 * @param {boolean} active - Whether floor finder is active
 */
function updateFloorFinderUI(role, active) {
    const button = role === 'start' ? $('#startFloorFinder') : $('#endFloorFinder');

    if (active) {
        button.classList.add('bg-gold', 'text-white');
        button.classList.remove('border', 'text-slate-600');
        button.title = 'Searching all floors';
    } else {
        button.classList.remove('bg-gold', 'text-white');
        button.classList.add('border', 'text-slate-600');
        button.title = 'Search all floors';
    }
}

/**
 * Initialize floor finder feature
 * Call this after the main app initializes
 */
function initFloorFinder() {
    // Add floor finder buttons to the UI
    const startSearchContainer = $('#startSearch').parentElement;
    const endSearchContainer = $('#endSearch').parentElement;

    // Create button for start search
    const startButton = document.createElement('button');
    startButton.id = 'startFloorFinder';
    startButton.className = 'absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded border text-xs text-slate-600 hover:bg-slate-50';
    startButton.innerHTML = '🔍 All Floors';
    startButton.title = 'Search all floors';
    startButton.type = 'button';

    // Create button for end search
    const endButton = document.createElement('button');
    endButton.id = 'endFloorFinder';
    endButton.className = 'absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 rounded border text-xs text-slate-600 hover:bg-slate-50';
    endButton.innerHTML = '🔍 All Floors';
    endButton.title = 'Search all floors';
    endButton.type = 'button';

    // Make input containers relative for absolute positioning
    const startInputWrapper = document.createElement('div');
    startInputWrapper.className = 'relative';
    const startInput = $('#startSearch');
    startInput.parentNode.insertBefore(startInputWrapper, startInput);
    startInputWrapper.appendChild(startInput);
    startInputWrapper.appendChild(startButton);

    const endInputWrapper = document.createElement('div');
    endInputWrapper.className = 'relative';
    const endInput = $('#endSearch');
    endInput.parentNode.insertBefore(endInputWrapper, endInput);
    endInputWrapper.appendChild(endInput);
    endInputWrapper.appendChild(endButton);

    // Add event listeners
    startButton.addEventListener('click', (e) => {
        e.preventDefault();
        toggleFloorFinder('start');
    });

    endButton.addEventListener('click', (e) => {
        e.preventDefault();
        toggleFloorFinder('end');
    });

    // Modify existing input handlers to support cross-floor search
    const originalStartHandler = $('#startSearch').oninput;
    $('#startSearch').addEventListener('input', (e) => {
        if (floorFinderActive) {
            const results = searchAcrossAllFloors(e.target.value);
            renderCrossFloorResults('start', results);
        }
    });

    const originalEndHandler = $('#endSearch').oninput;
    $('#endSearch').addEventListener('input', (e) => {
        if (floorFinderActive) {
            const results = searchAcrossAllFloors(e.target.value);
            renderCrossFloorResults('end', results);
        }
    });
}

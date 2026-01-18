// Configuration - Use the correct endpoint defined in main.py
const BACKEND_IP = "localhost:8000"; 
const ws = new WebSocket(`ws://${BACKEND_IP}/ws/alerts`);

ws.onopen = () => {
    console.log("Connected to nwHacks 2026 Bridge Alert System");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Incoming Data:", data);
    
    // Handle Wandering Alerts (New Priority Logic)
    if (data.type === "WANDERING_DETECTED") {
        const banner = document.getElementById('alert-banner');
        if (banner) {
            banner.classList.remove('hidden');
            // Show for 15 seconds as per your original logic
            setTimeout(() => banner.classList.add('hidden'), 15000);
        }
    } 
    
    // Handle Face Recognitions (Existing Logic)
    if (data.type === "DETECTION") {
        addVisitorEntry(data.name, data.relationship);
    }
};

ws.onclose = () => {
    console.warn("WebSocket connection closed. Check if backend/main.py is running.");
};

/**
 * Adds a visitor record to the dashboard UI
 */
function addVisitorEntry(name, relation) {
    const log = document.getElementById('visitor-log');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = "visitor-entry flex items-center justify-between p-4 bg-white/50 rounded-xl border border-white/40 shadow-sm mb-2";
    
    entry.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 font-bold">
                ${name ? name[0] : '?'}
            </div>
            <div>
                <p class="font-bold text-slate-800">${name || 'Unknown'}</p>
                <p class="text-xs text-slate-500 uppercase font-semibold">${relation || 'Visitor'}</p>
            </div>
        </div>
        <span class="text-xs font-medium text-slate-400">
            ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
        </span>
    `;
    
    log.prepend(entry);
    
    // Clean up empty state message
    const emptyMsg = log.querySelector('p.italic');
    if (emptyMsg) emptyMsg.remove();
}

/**
 * Joystick Control for Camera Pan/Tilt
 */
const joystickZone = document.getElementById('joystick-zone');
if (joystickZone) {
    const joystick = nipplejs.create({
        zone: joystickZone,
        mode: 'static',
        position: { right: '50%', bottom: '50%' },
        color: '#3b82f6',
        size: 100
    });

    joystick.on('move', (evt, data) => {
        // Result-Driven Tip: You will eventually need to fetch/POST this 
        // to your Pi's bridge_node.py to actually move the motors.
        if (data.angle) {
            console.log("Moving camera angle:", Math.round(data.angle.degree));
        }
    });
}
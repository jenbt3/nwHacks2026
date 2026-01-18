const BACKEND_IP = "localhost:8000"; // Replace with your Pi's IP for testing
const ws = new WebSocket(`ws://${BACKEND_IP}/ws/caregiver`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === "WANDERING_DETECTED") {
        const banner = document.getElementById('alert-banner');
        banner.classList.remove('hidden');
        setTimeout(() => banner.classList.add('hidden'), 15000);
    } 
    
    if (data.type === "DETECTION") {
        addVisitorEntry(data.name, data.relationship);
    }
};

function addVisitorEntry(name, relation) {
    const log = document.getElementById('visitor-log');
    const entry = document.createElement('div');
    entry.className = "visitor-entry flex items-center justify-between p-4 bg-white/50 rounded-xl border border-white/40 shadow-sm";
    entry.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 font-bold">
                ${name[0]}
            </div>
            <div>
                <p class="font-bold text-slate-800">${name}</p>
                <p class="text-xs text-slate-500 uppercase font-semibold">${relation}</p>
            </div>
        </div>
        <span class="text-xs font-medium text-slate-400">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
    `;
    log.prepend(entry);
    if (log.querySelector('p.italic')) log.querySelector('p.italic').remove();
}

// Joystick Control

const joystick = nipplejs.create({
    zone: document.getElementById('joystick-zone'),
    mode: 'static',
    position: { right: '50%', bottom: '50%' },
    color: '#3b82f6',
    size: 100
});

joystick.on('move', (evt, data) => {
    // Throttling or debounce here for servo motor performance
    console.log("Moving camera:", data.angle.degree);
});
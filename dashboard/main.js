// --- FULL main.js ---
const BACKEND_HOST = "10.19.132.171:8000"; // Laptop IP
const PI_IP = "192.168.x.x"; // CHANGE TO YOUR PI'S IP
const PI_STREAM_URL = `http://${PI_IP}:8000/video_feed`;

let ws;
let reconnectInterval = 5000;

function connect() {
    ws = new WebSocket(`ws://${BACKEND_HOST}/ws/alerts`);

    ws.onopen = () => {
        const status = document.getElementById('status-indicator');
        if (status) { status.innerText = "ONLINE"; status.style.color = "#10b981"; }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "WANDERING_DETECTED") {
            const banner = document.getElementById('alert-banner');
            if (banner) {
                banner.classList.remove('hidden');
                banner.querySelector('p').innerText = data.message || "Patient near exit!";
            }
        } 
        if (data.type === "DETECTION") { addVisitorEntry(data.name, data.relation); }
    };

    ws.onclose = () => {
        const status = document.getElementById('status-indicator');
        if (status) { status.innerText = "OFFLINE - RETRYING"; status.style.color = "#ef4444"; }
        setTimeout(connect, reconnectInterval);
    };
}

function addVisitorEntry(name, relation) {
    const log = document.getElementById('visitor-log');
    if (!log) return;
    const entry = document.createElement('div');
    entry.className = "visitor-entry flex justify-between items-center p-4 bg-white/50 rounded-xl border border-white/20 mb-2";
    entry.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">${name ? name[0] : '?'}</div>
            <div>
                <p class="font-bold text-slate-800">${name || 'Unknown'}</p>
                <p class="text-xs text-slate-500 uppercase font-semibold">${relation || 'Visitor'}</p>
            </div>
        </div>
        <span class="text-xs font-medium text-slate-400">${new Date().toLocaleTimeString()}</span>`;
    log.prepend(entry);
}

const enrollForm = document.getElementById('enroll-form');
if (enrollForm) {
    enrollForm.onsubmit = async (e) => {
        e.preventDefault();
        const img = document.getElementById('main-stream');
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth || 640;
        canvas.height = img.naturalHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const payload = {
            name: document.getElementById('name').value,
            relation: document.getElementById('relationship_type').value,
            memory_anchor: document.getElementById('anchor').value,
            image_base64: canvas.toDataURL('image/jpeg') 
        };

        try {
            await fetch(`http://${BACKEND_HOST}/people/enroll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            alert("Visitor Enrolled!");
            e.target.reset();
        } catch (err) { alert("Enrollment failed. Check backend."); }
    };
}

const joystickZone = document.getElementById('joystick-zone');
if (joystickZone && typeof nipplejs !== 'undefined') {
    const manager = nipplejs.create({ zone: joystickZone, mode: 'static', size: 100 });
    manager.on('move', (evt, data) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: "CAMERA_CONTROL",
                direction: data.angle.degree,
                distance: data.force
            }));
        }
    });
    manager.on('end', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "CAMERA_CONTROL", direction: 0, distance: 0 }));
        }
    });
}
connect();
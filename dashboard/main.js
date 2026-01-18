const BACKEND_IP = "localhost:8000"; 
let ws;
let reconnectInterval = 5000;

/**
 * WebSocket Management: Handles real-time alerts and detection logs
 */
function connect() {
    ws = new WebSocket(`ws://${BACKEND_IP}/ws/alerts`);

    ws.onopen = () => {
        const status = document.getElementById('status-indicator');
        if (status) {
            status.innerText = "ONLINE";
            status.style.color = "#10b981";
        }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Handle Wandering Alerts
        if (data.type === "WANDERING_DETECTED") {
            const banner = document.getElementById('alert-banner');
            if (banner) {
                banner.classList.remove('hidden');
                banner.querySelector('p').innerText = data.message || "Patient near exit!";
                // High priority alerts stay visible until dismissed; others fade
                if (data.priority !== "HIGH") {
                    setTimeout(() => banner.classList.add('hidden'), 10000);
                }
            }
        } 
        
        // Handle New Face Detections
        if (data.type === "DETECTION") {
            // Using 'relation' to match the updated backend schema
            addVisitorEntry(data.name, data.relation);
        }
    };

    ws.onclose = () => {
        const status = document.getElementById('status-indicator');
        if (status) {
            status.innerText = "OFFLINE - RETRYING";
            status.style.color = "#ef4444";
        }
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
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                ${name ? name[0] : '?'}
            </div>
            <div>
                <p class="font-bold text-slate-800">${name || 'Unknown'}</p>
                <p class="text-xs text-slate-500 uppercase font-semibold">${relation || 'Visitor'}</p>
            </div>
        </div>
        <span class="text-xs font-medium text-slate-400">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
    `;
    
    log.prepend(entry);
    const emptyMsg = log.querySelector('p.italic');
    if (emptyMsg) emptyMsg.remove();
}

/**
 * Enrollment Logic: Captures frame from the stream and sends to /people/enroll
 */
const enrollForm = document.getElementById('enroll-form');
if (enrollForm) {
    enrollForm.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('enroll-btn');
        btn.innerText = "PROCESSING...";
        btn.disabled = true;

        // Capture current frame from the main-stream <img>
        const img = document.getElementById('main-stream');
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth || 640;
        canvas.height = img.naturalHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const payload = {
            name: document.getElementById('name').value,
            relation: document.getElementById('relationship_type').value, // Maps to backend 'relation'
            memory_anchor: document.getElementById('anchor').value,
            image_base64: canvas.toDataURL('image/jpeg') 
        };

        try {
            const response = await fetch(`http://${BACKEND_IP}/people/enroll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert("Visitor Enrolled! Face vector synchronized.");
                e.target.reset();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (err) {
            console.error("Enrollment failed:", err);
            alert("Connection error. Is the backend running?");
        } finally {
            btn.innerText = "SECURE IDENTITY";
            btn.disabled = false;
        }
    };
}

/**
 * Joystick Functionality for Pan-Tilt Control
 */
const joystickZone = document.getElementById('joystick-zone');
if (joystickZone && typeof nipplejs !== 'undefined') {
    const manager = nipplejs.create({
        zone: joystickZone,
        mode: 'static',
        position: { right: '50%', bottom: '50%' },
        color: '#3b82f6',
        size: 100
    });

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

// Start services
connect();
// Configuration
const BACKEND_IP = "localhost:8000"; 
let ws;
let reconnectInterval = 5000;

/**
 * WebSocket Management: Real-time alerts, detection logs, and camera control
 */
function connect() {
    ws = new WebSocket(`ws://${BACKEND_IP}/ws/alerts`);

    ws.onopen = () => {
        console.log("Connected to Cognitive Bridge System");
        const status = document.getElementById('status-indicator');
        if (status) {
            status.innerText = "ONLINE";
            status.style.color = "#10b981";
        }
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // 1. Handle Wandering Alerts
        if (data.type === "WANDERING_DETECTED") {
            const banner = document.getElementById('alert-banner');
            if (banner) {
                banner.classList.remove('hidden');
                banner.querySelector('p').innerText = data.message || "Patient near exit!";
                
                // Keep critical (High Priority) alerts visible until manually dismissed
                if (data.priority !== "HIGH") {
                    setTimeout(() => banner.classList.add('hidden'), 10000);
                }
            }
        } 
        
        // 2. Handle Recognition/Detection Logs
        if (data.type === "DETECTION") {
            // Updated to use relationship_type to match models.py
            addVisitorEntry(data.name, data.relationship_type);
        }
    };

    ws.onclose = () => {
        console.warn("Connection Lost. Retrying in 5s...");
        const status = document.getElementById('status-indicator');
        if (status) {
            status.innerText = "OFFLINE - RETRYING";
            status.style.color = "#ef4444";
        }
        setTimeout(connect, reconnectInterval);
    };
}

/**
 * Adds a visitor record to the dashboard UI log
 */
function addVisitorEntry(name, relation) {
    const log = document.getElementById('visitor-log');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = "flex justify-between items-center p-4 bg-white/50 rounded-xl border border-white/20 mb-2";
    
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
        <span class="text-xs font-medium text-slate-400">
            ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
        </span>
    `;
    
    log.prepend(entry);
    
    const emptyMsg = log.querySelector('p.italic');
    if (emptyMsg) emptyMsg.remove();
}

/**
 * Enrollment Logic: Sends data to backend and notifies user
 */
document.getElementById('enroll-form').onsubmit = async (e) => {
    e.preventDefault();
    
    // In a production setup, this would be a real face embedding
    const mockEncoding = "base64_encoded_vector_here"; 

    const payload = {
        name: document.getElementById('name').value,
        relationship_type: document.getElementById('relationship_type').value, 
        memory_anchor: document.getElementById('anchor').value,
        encoding: mockEncoding
    };

    try {
        const response = await fetch(`http://${BACKEND_IP}/people/enroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Visitor Enrolled! Note: Restart the Raspberry Pi to sync new face data.");
            e.target.reset();
        } else {
            const error = await response.json();
            console.error("Enrollment failed:", error);
        }
    } catch (err) {
        console.error("Network Error:", err);
    }
};

/**
 * Joystick Functionality: Capture movement and send to Edge Node
 */
const joystickZone = document.getElementById('joystick-zone');
if (joystickZone) {
    const manager = nipplejs.create({
        zone: joystickZone,
        mode: 'static',
        position: { right: '50%', bottom: '50%' },
        color: '#3b82f6',
        size: 100
    });

    // Handle movement (Sending commands to the Pi)
    manager.on('move', (evt, data) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            // angle.degree provides 0-360 for direction
            // force provides distance from center (scaled for speed)
            ws.send(JSON.stringify({
                type: "CAMERA_CONTROL",
                direction: data.angle.degree,
                distance: data.force
            }));
        }
    });

    // Handle release (Stop the servos)
    manager.on('end', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: "CAMERA_CONTROL",
                direction: 0,
                distance: 0
            }));
        }
    });
}

// Start initial WebSocket connection
connect();
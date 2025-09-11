// CSRF helper (lấy cookie csrftoken)
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
    if (match) return match[2]
    return ''
}

// Theme (giữ của bạn)
function toggleTheme() {
    document.body.classList.toggle('dark')
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light')
}
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark')
}

document.getElementById("uploadForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch("/detect_image/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.image) {
            // Tạo thẻ <img> để hiển thị
            const imgElement = document.createElement("img");
            imgElement.src = "data:image/jpeg;base64," + data.image;
            imgElement.style.maxWidth = "100%";
            imgElement.style.border = "2px solid #333";
            imgElement.style.marginTop = "10px";

            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = ""; // clear trước đó
            resultDiv.appendChild(imgElement);
        } 
        // Nếu có dữ liệu ổ gà
        if (data.detections) {
            const detections = data.detections;
            const count = detections.length;
            // const avgConfidence = (detections.reduce((sum, d) => sum + d.confidence, 0) / count).toFixed(2);
            // const avgConfidence = round(float(detections[count-1]["confidence_TB"]), 2) 
            const avgConfidence = (data.confidence_TB * 100).toFixed(2);
            // cập nhật vào giao diện
            document.getElementById("pothole-count").textContent = count;
            document.getElementById("confidence").textContent = avgConfidence;
        } else if (data.error) {
            alert("Error: " + data.error);
        }

    } catch (err) {
        console.error("Upload error:", err);
        alert("Có lỗi khi upload ảnh.");
    }
});

// State
let isGPSActive = false
let isCameraActive = false
let gpsWatchId = null
let stream = null
let sendIntervalId = null
const video = document.getElementById('cameraFeed')
const canvas = document.getElementById('overlay')
const ctx = canvas.getContext('2d')

// GPS Toggle: lưu vị trí vào window.currentGPS để gửi lên server
window.currentGPS = null
function toggleGPS() {
    const gpsButton = document.getElementById('gpsToggle')
    const gpsStatus = document.getElementById('gps-status')

    if (!isGPSActive) {
        if (navigator.geolocation) {
            gpsWatchId = navigator.geolocation.watchPosition(
                (pos) => {
                    const { latitude, longitude } = pos.coords
                    window.currentGPS = { lat: latitude, lon: longitude }
                    gpsStatus.innerText = `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
                    gpsStatus.className = 'status-active'
                    gpsButton.innerText = '📍 Tắt GPS'
                    gpsButton.classList.add('btn-active')
                    isGPSActive = true
                },
                (err) => {
                    window.currentGPS = null
                    gpsStatus.innerText = 'Lỗi: ' + err.message
                    gpsStatus.className = 'status-inactive'
                },
                { enableHighAccuracy: true, maximumAge: 2000, timeout: 5000 }
            )
        } else {
            gpsStatus.innerText = 'GPS không hỗ trợ'
            gpsStatus.className = 'status-inactive'
        }
    } else {
        if (gpsWatchId) navigator.geolocation.clearWatch(gpsWatchId)
        window.currentGPS = null
        gpsStatus.innerText = 'Đã tắt'
        gpsStatus.className = 'status-inactive'
        gpsButton.innerText = '📍 Bật GPS'
        gpsButton.classList.remove('btn-active')
        isGPSActive = false
    }
}

video.addEventListener("loadedmetadata", () => {
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
})

// === WebSocket setup === 
let ws = null
// Kết nối WebSocket
function connectWS() {
    return new Promise((resolve, reject) => {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws"
        const wsUrl = `${wsScheme}://${window.location.host}/ws/detect/`
        console.log("Connecting WS to", wsUrl)
        ws = new WebSocket(wsUrl)   // browser sẽ cố kết nối đến server WebSocket backend
        ws.onopen = () => {
            console.log("WS connected")
            resolve()
        }
        ws.onclose = () => {
            console.log("WS closed")
            ws = null
        }
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)   // event.data là chuỗi JSON → parse thành object data.
                console.log("data received:", data)

                ctx.clearRect(0, 0, canvas.width, canvas.height)

                if (data && data.detections && data.detections.length > 0) {
                    document.getElementById('pothole-count').innerText = data.pothole_count
                    document.getElementById('confidence').innerText = (data.confidence_TB * 100).toFixed(2)

                    // Hiển thị ảnh đã vẽ box từ server
                    const imgElement = document.getElementById("pothole-frame") || document.createElement("img")
                    imgElement.id = "pothole-frame"
                    imgElement.src = "data:image/jpeg;base64," + data.image
                    imgElement.style.maxWidth = "100%"
                    
                    const resultDiv = document.getElementById("result")
                    resultDiv.innerHTML = ""
                    resultDiv.appendChild(imgElement)

                } else {
                    document.getElementById('pothole-count').innerText = '0'
                    document.getElementById('confidence').innerText = '-'
                }
            } catch (err) {
                console.error("WS parse error:", err)
            }
        }
        ws.onerror = (err) => {
            console.error("WS error:", err)
            reject(err)
        }
    })
}


// Camera Toggle: start/stop + start/stop capture loop
async function toggleCamera() {
    const cameraButton = document.getElementById('cameraToggle')
    const cameraStatus = document.getElementById('camera-status')

    if (!isCameraActive) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment', width: { ideal: 640 } }, audio: false })
            video.srcObject = stream
            isCameraActive = true
            cameraStatus.innerText = 'Đang bật'
            cameraStatus.className = 'status-active'
            cameraButton.innerText = '📷 Tắt Camera'
            cameraButton.classList.add('btn-active')
            // 🔑 chỉ mở WebSocket khi bật camera
            await connectWS()
            console.log('WebSocket state:', ws.readyState)
            if (sendIntervalId) {
                clearInterval(sendIntervalId)  // hủy interval cũ nếu có
                sendIntervalId = null
            }
            // start periodic sending => 5 FPS (200ms). Throttle to reduce CPU & bandwidth.
            sendIntervalId = setInterval(() => {
                captureAndSend()
                console.log("hello")
            }, 200)
        } catch (err) {
            console.error('Không mở được camera', err)
            cameraStatus.innerText = 'Không mở được camera'
            cameraStatus.className = 'status-inactive'
        }
    } else {
        // stop
        if (sendIntervalId) {
            clearInterval(sendIntervalId)
            sendIntervalId = null
        }
        if (stream) {
            stream.getTracks().forEach((t) => t.stop())
            stream = null
        }
        video.srcObject = null
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        isCameraActive = false
        cameraStatus.innerText = 'Chưa bật'
        cameraStatus.className = 'status-inactive'
        cameraButton.innerText = '📷 Bật Camera'
        cameraButton.classList.remove('btn-active')
        // reset info panel
        document.getElementById('pothole-count').innerText = '0'
        document.getElementById('confidence').innerText = '-'

        // 🔑 đóng WebSocket khi tắt camera
        if (ws) {
            ws.close()
            ws = null
        }
    }
}


// Capture + send loop (được bật khi camera on)
// Gửi frame qua WS
async function captureAndSend() {
    if (!isCameraActive || !ws || ws.readyState !== WebSocket.OPEN) return
    if (!video.videoWidth || !video.videoHeight) return

    const tempCanvas = document.createElement('canvas')
    tempCanvas.width = video.videoWidth
    tempCanvas.height = video.videoHeight
    const tempCtx = tempCanvas.getContext('2d')

    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height)

    const base64data = tempCanvas.toDataURL("image/jpeg", 0.7).split(",")[1]
    const payload = { frame: base64data, gps: window.currentGPS || null }

    try {
        ws.send(JSON.stringify(payload))
    } catch (err) {
        console.error("WS send error:", err)
    }
}


// Cleanup
window.addEventListener('beforeunload', () => {
    if (isGPSActive && gpsWatchId) navigator.geolocation.clearWatch(gpsWatchId)
    if (isCameraActive) {
        if (sendIntervalId) {
            clearInterval(sendIntervalId)
            sendIntervalId = null
        }
        if (stream) stream.getTracks().forEach((t) => t.stop())
    }
    if (ws) ws.close()
})



// ws.onopen → Khi kết nối thành công.
// ws.onmessage → Mỗi khi server gửi  dữ liệu JSON detection. (seft.sent())
// ws.onclose → Khi server đóng kết nối hoặc client ngắt.
// ws.onerror → Khi có lỗi mạng/kết nối WS thất bại.

// ws = new WebSocket(wsUrl) ⟶ gọi đến DetectionConsumer.connect() → await self.accept().
// ws.send({frame, gps}) (JS) ⟶ kích hoạt DetectionConsumer.receive(self, text_data).
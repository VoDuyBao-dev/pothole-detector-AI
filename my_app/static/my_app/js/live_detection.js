
// Theme (giữ của bạn)
function toggleTheme() {
    document.body.classList.toggle('dark')
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light')
}
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark')
}

// Image upload (giữ nguyên)
const form = document.getElementById('uploadForm')
form.onsubmit = async (e) => {
    e.preventDefault()
    let formData = new FormData(form)
    let res = await fetch(detect_image, {
        method: 'POST',
        body: formData
    })
    let data = await res.json()
    if (data.image) {
        let img = document.createElement('img')
        img.src = 'data:image/jpeg;base64,' + btoa(String.fromCharCode(...new Uint8Array(data.image.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)))))
        document.getElementById('result').innerHTML = ''
        document.getElementById('result').appendChild(img)
    }
}

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

// === WebSocket setup ===
let ws = null

// Kết nối WebSocket
function connectWS() {
    return new Promise((resolve, reject) => {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws"
        const wsUrl = `${wsScheme}://${window.location.host}/ws/detect/`
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            console.log("WS connected")
            resolve()
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                ctx.clearRect(0, 0, canvas.width, canvas.height)

                if (data && data.detections && data.detections.length > 0) {
                    const d0 = data.detections[0]
                    document.getElementById('pothole-count').innerText = data.detections.length
                    document.getElementById('confidence').innerText = (d0.confidence * 100).toFixed(2)
                    document.getElementById('area').innerText = d0.area.toFixed(0)
                    document.getElementById('size').innerText = d0.size
                    document.getElementById('level').innerText = d0.level
                } else {
                    document.getElementById('pothole-count').innerText = '0'
                    document.getElementById('confidence').innerText = '-'
                    document.getElementById('area').innerText = '-'
                    document.getElementById('size').innerText = '-'
                    document.getElementById('level').innerText = '-'
                }

                // Vẽ bounding boxes
                ; (data.detections || []).forEach(det => {
                    ctx.beginPath()
                    ctx.lineWidth = 2
                    ctx.strokeStyle = 'blue'
                    ctx.rect(det.x, det.y, det.width, det.height)
                    ctx.stroke()
                    ctx.fillStyle = 'green'
                    ctx.font = '14px Arial'
                    ctx.fillText(
                        `${det.label} (${(det.confidence * 100).toFixed(1)}%)`,
                        Math.max(det.x, 2),
                        Math.max(det.y - 6, 12)
                    )
                })
            } catch (err) {
                console.error("WS parse error:", err)
            }
        }

        ws.onerror = (err) => {
            console.error("WS error:", err)
            reject(err)
        }
        ws.onclose = () => {
            console.log("WS closed")
            ws = null
        }

    })
}


// === Capture loop ===
async function captureAndSendWS() {
    if (!isCameraActive || !ws || ws.readyState !== WebSocket.OPEN) return

    if (!video.videoWidth || !video.videoHeight) return

    // Resize canvas nếu cần
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
    }

    const tempCanvas = document.createElement("canvas")
    tempCanvas.width = video.videoWidth
    tempCanvas.height = video.videoHeight
    const tempCtx = tempCanvas.getContext("2d")
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height)

    tempCanvas.toBlob((blob) => {
        if (!blob) return
        const reader = new FileReader()
        reader.onload = () => {
            const base64data = reader.result.split(",")[1] // lấy phần sau "data:image/jpeg;base64,"

            const payload = {
                frame: base64data,
                gps: window.currentGPS || null,
            }

            try {
                ws.send(JSON.stringify(payload))
            } catch (e) {
                console.error("WS send error:", e)
            }
        }
    })
}


// === Camera Toggle ===
async function toggleCamera() {
    const cameraButton = document.getElementById('cameraToggle')
    const cameraStatus = document.getElementById('camera-status')

    if (!isCameraActive) {
        try {
            // mở camera
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 640 } },
                audio: false
            })
            video.srcObject = stream
            isCameraActive = true
            cameraStatus.innerText = 'Đang bật'
            cameraStatus.className = 'status-active'
            cameraButton.innerText = '📷 Tắt Camera'
            cameraButton.classList.add('btn-active')

            // 🔑 chỉ mở WebSocket khi bật camera
            await connectWS()

            // bắt đầu gửi frame định kỳ
            sendIntervalId = setInterval(captureAndSendWS, 200)

        } catch (err) {
            console.error("Không mở được camera", err)
            cameraStatus.innerText = 'Không mở được camera'
            cameraStatus.className = 'status-inactive'
        }
    } else {
        // dừng gửi frame
        if (sendIntervalId) clearInterval(sendIntervalId)

        // tắt camera
        if (stream) stream.getTracks().forEach((t) => t.stop())
        video.srcObject = null
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        isCameraActive = false
        cameraStatus.innerText = 'Chưa bật'
        cameraStatus.className = 'status-inactive'
        cameraButton.innerText = '📷 Bật Camera'
        cameraButton.classList.remove('btn-active')

        // reset info
        document.getElementById('pothole-count').innerText = '0'
        document.getElementById('confidence').innerText = '-'
        document.getElementById('area').innerText = '-'
        document.getElementById('size').innerText = '-'
        document.getElementById('level').innerText = '-'

        // 🔑 đóng WebSocket khi tắt camera
        if (ws) {
            ws.close()
            ws = null
        }
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
        if (ws) ws.close()
    }
})
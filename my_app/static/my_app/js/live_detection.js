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

// Helper: gửi frame blob + gps (FormData)
async function sendFrameBlob(blob) {
    const form = new FormData()
    form.append('frame', blob, 'frame.jpg')
    if (window.currentGPS) {
        form.append('lat', String(window.currentGPS.lat))
        form.append('lon', String(window.currentGPS.lon))
    }
    // Thêm CSRF header
    const csrftoken = getCookie('csrftoken')
    const res = await fetch(liveDetectionUrl, {
        method: 'POST',
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        body: form
    })
    console.log('Response status:', res.json)
    return res.json()
}

// Capture + send loop (được bật khi camera on)
async function captureAndSend() {
    if (!isCameraActive) return

    // ensure video resolution ready
    if (!video.videoWidth || !video.videoHeight) return

    // Resize canvas to video intrinsic size (pixel-perfect overlay)
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        // adjust computed CSS height to match aspect (optional)
    }

    // Draw current frame then get blob jpeg
    const tempCanvas = document.createElement('canvas')
    tempCanvas.width = video.videoWidth
    tempCanvas.height = video.videoHeight
    const tempCtx = tempCanvas.getContext('2d')
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height)

    tempCanvas.toBlob(
        async (blob) => {
            if (!blob) return
            try {
                const data = await sendFrameBlob(blob)
                // Clear overlay and redraw video image for overlay base
                ctx.clearRect(0, 0, canvas.width, canvas.height)
                // draw boxes if any
                if (data && data.detections && data.detections.length > 0) {
                    // update info panel with first detection
                    const d0 = data.detections[0]
                    document.getElementById('pothole-count').innerText = data.detections.length
                    document.getElementById('confidence').innerText = (d0.confidence * 100).toFixed(2)
                    document.getElementById('area').innerText = d0.area.toFixed(0)
                    document.getElementById('size').innerText = `${d0.width}x${d0.height}`
                    document.getElementById('level').innerText = (d0.width * d0.height).toFixed(0)
                } else {
                    document.getElementById('pothole-count').innerText = '0'
                    document.getElementById('confidence').innerText = '-'
                    document.getElementById('area').innerText = '-'
                    document.getElementById('size').innerText = '-'
                    document.getElementById('level').innerText = '-'
                }

                // draw bounding boxes returned by server
                ; (data.detections || []).forEach((det) => {
                    ctx.beginPath()
                    ctx.lineWidth = 2
                    ctx.strokeStyle = 'blue'
                    ctx.rect(det.x, det.y, det.width, det.height)
                    ctx.stroke()
                    ctx.fillStyle = 'green'
                    ctx.font = '14px Arial'
                    const labelText = `${det.label} (${(det.confidence * 100).toFixed(1)}%)`
                    ctx.fillText(labelText, Math.max(det.x, 2), Math.max(det.y - 6, 12))
                })
            } catch (err) {
                console.error('Error sending frame:', err)
            }
        },
        'image/jpeg',
        0.7
    ) // quality 0.7: trade quality vs bandwidth
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

            // start periodic sending => 5 FPS (200ms). Throttle to reduce CPU & bandwidth.
            sendIntervalId = setInterval(() => {
                captureAndSend()
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
        document.getElementById('size').innerText = '-'
        document.getElementById('level').innerText = '-'
    }
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (isGPSActive && gpsWatchId) navigator.geolocation.clearWatch(gpsWatchId)
    if (isCameraActive) {
        if (sendIntervalId) clearInterval(sendIntervalId)
        if (stream) stream.getTracks().forEach((t) => t.stop())
    }
})
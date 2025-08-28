const $ = (sel, ctx = document) => ctx.querySelector(sel)
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel))

// Tab switch
const tabLogin = $('#tab-login')
const tabSignup = $('#tab-signup')
const panelLogin = $('#panel-login')
const panelSignup = $('#panel-signup')
function setTab(which) {
    const isLogin = which === 'login'
    tabLogin.setAttribute('aria-selected', isLogin)
    tabSignup.setAttribute('aria-selected', !isLogin)
    panelLogin.hidden = !isLogin
    panelSignup.hidden = isLogin
}
tabLogin.addEventListener('click', () => setTab('login'))
tabSignup.addEventListener('click', () => setTab('signup'))
$('#to-login')?.addEventListener('click', (e) => {
    e.preventDefault()
    setTab('login')
})

// Toggle password visibility
$$('[data-toggle="password"]').forEach((btn) => {
    btn.addEventListener('click', () => {
        const target = document.querySelector(btn.dataset.target)
        if (!target) return
        const isPwd = target.getAttribute('type') === 'password'
        target.setAttribute('type', isPwd ? 'text' : 'password')
        btn.textContent = isPwd ? '🙈' : '👁️'
    })
})

// Toast helper
let toastTimer
function toast(msg) {
    const el = $('#toast')
    el.textContent = msg
    el.classList.add('show')
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => el.classList.remove('show'), 2000)
}
window.toast = toast

// Password strength (đơn giản):
const pw = $('#su-password')
const pwBar = $('#pw-bar')
pw?.addEventListener('input', () => {
    const v = pw.value || ''
    let score = 0
    if (v.length >= 6) score++
    if (/[A-Z]/.test(v)) score++
    if (/[a-z]/.test(v)) score++
    if (/\d/.test(v)) score++
    if (/[\W_]/.test(v)) score++
    const percent = Math.min(100, score * 20)
    pwBar.style.width = percent + '%'
    pwBar.parentElement.setAttribute('aria-label', 'Độ mạnh mật khẩu: ' + percent + '%')
})

// Validation helpers
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}
function showError(input, msg) {
    input.setCustomValidity(msg || '')
    input.reportValidity()
    if (msg) toast(msg)
}

// Handle login submit
$('#form-login')?.addEventListener('submit', (e) => {
    e.preventDefault()
    const email = $('#login-email')
    const pass = $('#login-password')
    if (!validateEmail(email.value)) return showError(email, 'Email không hợp lệ')
    if ((pass.value || '').length < 6) return showError(pass, 'Mật khẩu tối thiểu 6 ký tự')
    showError(email, '')
    showError(pass, '')
    toast('Đăng nhập thành công (demo)')
})

// Handle signup submit
$('#form-signup')?.addEventListener('submit', (e) => {
    e.preventDefault()
    const name = $('#su-name')
    const uname = $('#su-username')
    const email = $('#su-email')
    const pass = $('#su-password')
    const confirm = $('#su-confirm')
    const terms = $('#su-terms')

    if (name.value.trim().length < 2) return showError(name, 'Vui lòng nhập họ tên')
    if (uname.value.trim().length < 4) return showError(uname, 'Tên đăng nhập tối thiểu 4 ký tự')
    if (!validateEmail(email.value)) return showError(email, 'Email không hợp lệ')
    if ((pass.value || '').length < 6) return showError(pass, 'Mật khẩu tối thiểu 6 ký tự')
    if (pass.value !== confirm.value) return showError(confirm, 'Mật khẩu xác nhận không khớp')
    if (!terms.checked) {
        toast('Bạn cần đồng ý điều khoản')
        return
    }

    ;[name, uname, email, pass, confirm].forEach((i) => showError(i, ''))
    toast('Tạo tài khoản thành công (demo)')
    setTab('login')
})

// Prefill demo for dễ test
setTimeout(() => {
    $('#login-email').value = 'demo@site.com'
    $('#login-password').value = 'Demo@123'
}, 300)


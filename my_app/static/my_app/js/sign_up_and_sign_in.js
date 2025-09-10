const $ = (sel, ctx = document) => ctx.querySelector(sel)
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel))


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
// $('#form-login')?.addEventListener('submit', (e) => {
//     e.preventDefault()
//     const email = $('#login-email')
//     const pass = $('#login-password')
//     if (!validateEmail(email.value)) return showError(email, 'Email không hợp lệ')
//     if ((pass.value || '').length < 6) return showError(pass, 'Mật khẩu tối thiểu 6 ký tự')
//     showError(email, '')
//     showError(pass, '')
//     toast('Đăng nhập thành công (demo)')
// })

// Prefill demo for dễ test
setTimeout(() => {
    $('#login-email').value = 'user1@example.com'
    $('#login-password').value = '123456'
}, 300)







const toggle = document.getElementById('themeToggle');
const body = document.body;

// Check for saved theme in localStorage and apply it
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark');
    toggle.checked = true;
}

toggle.addEventListener('change', () => {
    body.classList.toggle('dark');
    if (body.classList.contains('dark')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
}); 
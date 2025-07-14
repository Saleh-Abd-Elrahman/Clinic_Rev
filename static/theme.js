document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Check if toggle exists on this page
    if (!toggle) {
        console.log('Theme toggle not found on this page');
        return;
    }
    
    // Check for saved theme in localStorage and apply it
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark');
        toggle.checked = true;
    }
    
    // Add toggle event listener
    toggle.addEventListener('change', function() {
        body.classList.toggle('dark');
        if (body.classList.contains('dark')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });
}); 
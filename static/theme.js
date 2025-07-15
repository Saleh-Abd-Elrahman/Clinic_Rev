document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    
    // Always check for saved theme and apply it on page load
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        htmlElement.classList.add('dark');
        // Set toggle to checked if it exists
        if (toggle) {
            toggle.checked = true;
        }
    } else {
        // Ensure light theme is applied if no dark theme
        htmlElement.classList.remove('dark');
        if (toggle) {
            toggle.checked = false;
        }
    }
    
    // Only add toggle event listener if toggle exists on this page
    if (toggle) {
        toggle.addEventListener('change', function() {
            htmlElement.classList.toggle('dark');
            if (htmlElement.classList.contains('dark')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }
}); 
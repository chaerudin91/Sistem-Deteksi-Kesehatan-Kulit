document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            // Deactivate all tabs
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Activate the clicked tab and corresponding content
            tab.classList.add('active');
            const targetContent = document.getElementById(tab.getAttribute('data-tab'));
            targetContent.classList.add('active');
        });
    });
});

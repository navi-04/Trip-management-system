document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    if (document.querySelector('.tab-links')) {
        const firstTab = document.querySelector('.tab-link');
        if (firstTab) {
            firstTab.click();
        }
    }
});

function openTab(evt, tabName) {
    // Hide all tab content
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }

    // Remove active class from all tab links
    const tabLinks = document.getElementsByClassName('tab-link');
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }

    // Show the current tab and add active class to the button
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
}

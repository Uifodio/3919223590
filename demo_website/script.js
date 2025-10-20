// Demo JavaScript File
console.log('Modern Server Administrator - Demo Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully');
    
    // Add some interactive features
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Button clicked! Server is working perfectly.');
        });
    });
});
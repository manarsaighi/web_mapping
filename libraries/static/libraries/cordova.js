
// pwa 
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register("{% static 'service-worker.js' %}")
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);
        })
        .catch(function(err) {
            console.log('Service Worker registration failed:', err);
        });
    });
}

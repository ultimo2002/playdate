document.addEventListener('DOMContentLoaded', () => {
    window.scrollTo(0, document.body.scrollHeight);

    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'c' && prompt('Stop the server? Type "yes" to confirm') === 'yes') {
            fetch(`/stop?key=${new URLSearchParams(location.search).get('key')}`, { method: 'DELETE' })
                .then(r => r.ok && r.headers.get('Content-Length') > 0 ? r.text().then(alert) : null);
        }
    });

    if (window.matchMedia('(max-width: 600px)').matches) {
        const btn = Object.assign(document.createElement('button'), { textContent: 'Remove timestamps', style: 'margin: 0.5rem 0 1.5rem 0; font-size: 0.7rem;' });
        document.body.prepend(btn);
        btn.addEventListener('click', () => {
            document.querySelectorAll('pre').forEach(p => p.innerHTML = p.innerHTML.replace(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/g, ''));
            document.querySelectorAll('pre span[style="color:grey"]').forEach(s => s.remove());
            btn.remove();
        });
    }
});
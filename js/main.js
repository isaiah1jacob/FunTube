// FunTube main scripts
document.addEventListener('DOMContentLoaded', function () {
    const likeBtn = document.getElementById('likeBtn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function () {
            const pk = this.dataset.videoId;
            fetch('/video/' + pk + '/like/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.dataset.csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('likeCount').textContent = data.count;
                likeBtn.classList.toggle('active', data.liked);
                const icon = likeBtn.querySelector('i');
                icon.className = data.liked ? 'bi bi-hand-thumbs-up-fill' : 'bi bi-hand-thumbs-up';
            });
        });
    }
});
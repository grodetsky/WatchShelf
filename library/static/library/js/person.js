document.addEventListener("DOMContentLoaded", function () {
  const bio = document.getElementById('biography');
  const btn = document.getElementById('toggleBiographyBtn');

  if (bio && btn) {
    if (bio.scrollHeight <= 170) {
      bio.classList.remove('collapsed');
      bio.style.maxHeight = 'none';
      bio.querySelector('.fade-out')?.remove();
      btn.remove();
    } else {
      btn.classList.remove('d-none');
    }

    btn.addEventListener("click", function () {
      if (bio.classList.contains('collapsed')) {
        bio.classList.remove('collapsed');
        bio.style.maxHeight = 'none';
        bio.querySelector('.fade-out')?.remove();
        btn.innerText = 'Read less';
      } else {
        bio.classList.add('collapsed');
        bio.style.maxHeight = '170px';

        const fade = document.createElement('div');
        fade.className = 'fade-out';
        fade.style.position = 'absolute';
        fade.style.bottom = 0;
        fade.style.left = 0;
        fade.style.width = '100%';
        fade.style.height = '2em';
        fade.style.background = 'linear-gradient(to bottom, transparent, white)';
        bio.appendChild(fade);

        btn.innerText = 'Read more';
      }
    });
  }
});

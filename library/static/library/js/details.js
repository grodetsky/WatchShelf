class DetailsPage {
  constructor() {
    this.init();
  }

  init() {
    this.initViewAllLinks();
    this.initCollectionSelect();
    this.initModals();
    this.initCarousels();
    this.activateTabFromUrl();
  }

  initViewAllLinks() {
    const updateViewAllLink = () => {
      const activeTab = document.querySelector('#mediaTabs .nav-link.active');
      const viewAllContainer = document.getElementById('viewAllLink');

      if (!activeTab || !viewAllContainer) return;

      let label = '';
      let tab = '';
      if (activeTab.id.startsWith('videos-tab')) {
        label = 'Videos';
        tab = 'videos';
      } else if (activeTab.id.startsWith('backdrops-tab')) {
        label = 'Backdrops';
        tab = 'backdrops';
      } else if (activeTab.id.startsWith('posters-tab')) {
        label = 'Posters';
        tab = 'posters';
      }

      const baseUrl = viewAllContainer.dataset.mediaUrl || '#';
      viewAllContainer.innerHTML = `
        <a href="${baseUrl}?tab=${tab}" class="text-decoration-none fw-semibold text-primary text-nowrap">
          View All ${label}
        </a>
      `;
    };

    updateViewAllLink();

    const tabButtons = document.querySelectorAll('#mediaTabs .nav-link');
    tabButtons.forEach(button => {
      button.addEventListener('shown.bs.tab', updateViewAllLink);
    });
  }

  initCollectionSelect() {
    const select = document.getElementById('collectionSelect');
    if (select) {
      select.addEventListener('change', function() {
        if (this.value === 'create') {
          this.value = '';
          new bootstrap.Modal(document.getElementById('createCollectionModal')).show();
        } else if (this.value) {
          document.getElementById('collectionForm').submit();
        }
      });
    }
  }

  initModals() {
    const videoModal = document.getElementById('videoModal');
    if (videoModal) {
      const iframe = document.getElementById('videoIframe');
      videoModal.addEventListener('hidden.bs.modal', function () {
        iframe.setAttribute('src', '');
      });
    }
  }

  initCarousels() {
    this.initCastCarousels();
    this.initMediaCarousels();
  }

  initCastCarousels() {
    const carousels = document.querySelectorAll('.cast-carousel');

    carousels.forEach(carousel => {
      const container = carousel.closest('.cast-carousel-container');
      const prevBtn = container.querySelector('.cast-nav-prev');
      const nextBtn = container.querySelector('.cast-nav-next');
      const scrollAmount = 160;

      this.setupCarouselNavigation(carousel, prevBtn, nextBtn, scrollAmount);
    });
  }

  initMediaCarousels() {
    const mediaCarousels = document.querySelectorAll('.media-carousel');

    mediaCarousels.forEach(carousel => {
      const container = carousel.closest('.media-carousel-container');
      const prevBtn = container.querySelector('.media-nav-prev');
      const nextBtn = container.querySelector('.media-nav-next');
      const scrollAmount = 320;

      this.setupCarouselNavigation(carousel, prevBtn, nextBtn, scrollAmount);
    });

    const mediaTabTriggers = document.querySelectorAll('#mediaTabs button[data-bs-toggle="tab"]');
    mediaTabTriggers.forEach(trigger => {
      trigger.addEventListener('shown.bs.tab', () => {
        mediaCarousels.forEach(carousel => {
          this.updateCarouselButtons(carousel);
        });
      });
    });
  }

  setupCarouselNavigation(carousel, prevBtn, nextBtn, scrollAmount) {
    if (!prevBtn || !nextBtn) return;

    prevBtn.addEventListener('click', () => {
      carousel.scrollBy({
        left: -scrollAmount,
        behavior: 'smooth'
      });
    });

    nextBtn.addEventListener('click', () => {
      carousel.scrollBy({
        left: scrollAmount,
        behavior: 'smooth'
      });
    });

    const updateButtons = () => this.updateCarouselButtons(carousel);

    carousel.addEventListener('scroll', updateButtons);
    updateButtons();
    window.addEventListener('resize', updateButtons);
  }

  updateCarouselButtons(carousel) {
    const container = carousel.closest('.cast-carousel-container, .media-carousel-container');
    if (!container) return;

    const prevBtn = container.querySelector('.cast-nav-prev, .media-nav-prev');
    const nextBtn = container.querySelector('.cast-nav-next, .media-nav-next');

    if (!prevBtn || !nextBtn) return;

    const isAtStart = carousel.scrollLeft <= 0;
    const isAtEnd = carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth - 5;

    prevBtn.style.display = isAtStart ? 'none' : 'flex';
    nextBtn.style.display = isAtEnd ? 'none' : 'flex';
  }

  activateTabFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const tabId = urlParams.get('tab');

    if (tabId) {
      const tabButton = document.getElementById(`${tabId}-tab`);
      if (tabButton) {
        const tab = new bootstrap.Tab(tabButton);
        tab.show();

        const url = new URL(window.location);
        url.searchParams.delete('tab');
        window.history.replaceState({}, '', url);
      }
    }
  }
}

function openVideoModal(videoKey, videoTitle) {
  const modal = document.getElementById('videoModal');
  const iframe = document.getElementById('videoIframe');
  const title = document.getElementById('videoModalLabel');

  iframe.src = `https://www.youtube.com/embed/${videoKey}?rel=0&modestbranding=1&autoplay=1`;
  title.textContent = videoTitle;

  new bootstrap.Modal(modal).show();
}

function openImageModal(imageSrc) {
  const modal = document.getElementById('imageModal');
  const img = document.getElementById('modalImage');
  const dialog = document.getElementById('imageModalDialog');

  dialog.style.maxWidth = '80vw';

  img.src = imageSrc;

  new bootstrap.Modal(modal).show();

  img.onload = () => {
    const isPoster = img.naturalHeight / img.naturalWidth > 1.3;
    dialog.style.maxWidth = isPoster ? '480px' : '80vw';
  };
}

document.addEventListener('DOMContentLoaded', function() {
  new DetailsPage();
});

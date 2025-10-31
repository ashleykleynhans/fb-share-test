// Insert image on page load
window.addEventListener('DOMContentLoaded', function() {
    const imageContainer = document.getElementById('image-container');
    if (!imageContainer) return;

    // Get image data from data attributes
    const imageSrc = imageContainer.dataset.imageSrc;
    const imageAlt = imageContainer.dataset.imageAlt;

    if (imageSrc) {
        const img = document.createElement('img');
        img.src = imageSrc;
        img.alt = imageAlt || '';
        imageContainer.appendChild(img);
    }
});

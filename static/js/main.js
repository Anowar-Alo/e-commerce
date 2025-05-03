// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Cart functionality
    setupCart();

    // Product image gallery
    setupProductGallery();

    // Search functionality
    setupSearch();

    // Newsletter subscription
    setupNewsletter();

    // Notification system
    setupNotifications();
});

// Cart functionality
function setupCart() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = document.querySelector(`#quantity-${productId}`)?.value || 1;

            try {
                const response = await fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: quantity
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    updateCartBadge(data.cart_count);
                    showNotification('Success', 'Product added to cart!', 'success');
                    animateCartButton(this);
                } else {
                    showNotification('Error', data.error, 'danger');
                }
            } catch (error) {
                showNotification('Error', 'Could not add product to cart', 'danger');
            }
        });
    });
}

// Product image gallery
function setupProductGallery() {
    const mainImage = document.querySelector('.product-main-image');
    const galleryImages = document.querySelectorAll('.product-image-gallery img');

    if (mainImage && galleryImages.length) {
        galleryImages.forEach(img => {
            img.addEventListener('click', function() {
                // Remove active class from all images
                galleryImages.forEach(i => i.classList.remove('active'));
                // Add active class to clicked image
                this.classList.add('active');
                // Update main image
                mainImage.src = this.src;
                mainImage.alt = this.alt;
            });
        });
    }
}

// Search functionality
function setupSearch() {
    const searchForm = document.querySelector('#search-form');
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');

    if (searchForm && searchInput) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const query = this.value.trim();
                
                if (query.length < 2) {
                    searchResults.innerHTML = '';
                    return;
                }

                try {
                    const response = await fetch(`/search/?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (response.ok) {
                        displaySearchResults(data.results);
                    }
                } catch (error) {
                    console.error('Search error:', error);
                }
            }, 300);
        });
    }
}

// Newsletter subscription
function setupNewsletter() {
    const newsletterForm = document.querySelector('#newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;

            try {
                const response = await fetch('/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ email })
                });

                const data = await response.json();
                
                if (response.ok) {
                    showNotification('Success', 'Successfully subscribed to newsletter!', 'success');
                    this.reset();
                } else {
                    showNotification('Error', data.error, 'danger');
                }
            } catch (error) {
                showNotification('Error', 'Could not subscribe to newsletter', 'danger');
            }
        });
    }
}

// Notification system
function setupNotifications() {
    // WebSocket connection for real-time notifications
    if (window.user_id) {
        const ws_scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const notificationSocket = new WebSocket(
            `${ws_scheme}://${window.location.host}/ws/notifications/${window.user_id}/`
        );

        notificationSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            showNotification(data.title, data.message, data.level);
        };

        notificationSocket.onclose = function() {
            console.log('Notification WebSocket closed unexpectedly');
        };
    }
}

// Utility functions
function showNotification(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    document.querySelector('.toast-container').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.classList.remove('d-none');
    }
}

function animateCartButton(button) {
    button.classList.add('animate-bounce');
    setTimeout(() => {
        button.classList.remove('animate-bounce');
    }, 1000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('#search-results');
    
    if (!searchResults) return;

    if (!results.length) {
        searchResults.innerHTML = '<div class="p-3">No results found</div>';
        return;
    }

    const html = results.map(result => `
        <a href="${result.url}" class="list-group-item list-group-item-action">
            <div class="d-flex align-items-center">
                <img src="${result.image}" alt="${result.name}" class="me-3" style="width: 50px; height: 50px; object-fit: cover;">
                <div>
                    <h6 class="mb-1">${result.name}</h6>
                    <p class="mb-1 small text-muted">${result.price}</p>
                </div>
            </div>
        </a>
    `).join('');

    searchResults.innerHTML = `<div class="list-group">${html}</div>`;
}

// Price range slider
function initPriceRangeSlider() {
    const slider = document.querySelector('#price-range');
    if (slider) {
        noUiSlider.create(slider, {
            start: [0, 1000],
            connect: true,
            range: {
                'min': 0,
                'max': 1000
            },
            format: {
                to: value => Math.round(value),
                from: value => Number(value)
            }
        });

        const minPrice = document.querySelector('#min-price');
        const maxPrice = document.querySelector('#max-price');

        slider.noUiSlider.on('update', (values, handle) => {
            const value = values[handle];
            if (handle === 0) {
                minPrice.value = value;
            } else {
                maxPrice.value = value;
            }
        });
    }
} 
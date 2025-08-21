// WebSocket para notificaciones
const initWebSocket = () => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = ws_scheme + '://' + window.location.host + "/ws/notificaciones/";
    const socket = new WebSocket(ws_path);

    socket.onopen = function(e) {
        // console.log("WebSocket conectado");
    };
    socket.onmessage = function(e) {
        // console.log("Mensaje recibido:", e.data);
    };
    socket.onerror = function(e) {
        // console.error("WebSocket error:", e);
    };
    socket.onclose = function(e) {
        // console.log("WebSocket cerrado");
    };
};

// Variables para la paginación de productos
let currentOffset = 3; // Ya tenemos 3 productos cargados inicialmente
let isLoading = false;
let productosOriginales = 3; // Número de productos iniciales

// Función para cargar más productos
const cargarMasProductos = () => {
    if (isLoading) return;
    
    isLoading = true;
    const loadingEl = document.getElementById('loading-productos');
    const btnMostrarMas = document.getElementById('mostrar-mas-productos');
    const btnMostrarMenos = document.getElementById('mostrar-menos-productos');
    
    if (loadingEl) loadingEl.style.display = 'block';
    if (btnMostrarMas) btnMostrarMas.style.display = 'none';
    
    fetch(`/productos/ajax/?offset=${currentOffset}&limit=6`)
        .then(response => response.json())
        .then(data => {
            const productosGrid = document.getElementById('productos-grid');
            
            data.productos.forEach(producto => {
                const productCard = document.createElement('div');
                productCard.className = 'product-card producto-adicional';
                
                const imagenSrc = producto.imagen_url || 'https://via.placeholder.com/400x300?text=Sin+Imagen';
                
                productCard.innerHTML = `
                    <div class="product-carousel">
                        <img src="${imagenSrc}" class="product-img" alt="${producto.nombre}" />
                    </div>
                    <div class="product-info">
                        <h3 class="product-name">${producto.nombre}</h3>
                        <p class="product-price">$${producto.precio}</p>
                        <p class="product-description">${producto.descripcion ? producto.descripcion.substring(0, 60) + '...' : ''}</p>
                        <button class="btn-green" data-producto-id="${producto.id}">Ver producto</button>
                    </div>
                `;
                
                productosGrid.appendChild(productCard);
            });
            
            currentOffset += data.productos.length;
            
            if (data.has_more) {
                if (btnMostrarMas) btnMostrarMas.style.display = 'inline-block';
            } else {
                if (btnMostrarMas) btnMostrarMas.style.display = 'none';
            }
            
            // Mostrar botón "Mostrar menos productos"
            if (btnMostrarMenos) btnMostrarMenos.style.display = 'inline-block';
            
            if (loadingEl) loadingEl.style.display = 'none';
            isLoading = false;
        })
        .catch(error => {
            console.error('Error cargando productos:', error);
            if (loadingEl) loadingEl.style.display = 'none';
            if (btnMostrarMas) btnMostrarMas.style.display = 'inline-block';
            isLoading = false;
        });
};

// Función para mostrar menos productos (volver a los 3 iniciales)
const mostrarMenosProductos = () => {
    const productosGrid = document.getElementById('productos-grid');
    const btnMostrarMas = document.getElementById('mostrar-mas-productos');
    const btnMostrarMenos = document.getElementById('mostrar-menos-productos');
    
    // Eliminar todos los productos adicionales
    const productosAdicionales = productosGrid.querySelectorAll('.producto-adicional');
    productosAdicionales.forEach(producto => {
        producto.remove();
    });
    
    // Resetear variables
    currentOffset = productosOriginales;
    
    // Mostrar botón "Mostrar más" y ocultar "Mostrar menos"
    if (btnMostrarMas) btnMostrarMas.style.display = 'inline-block';
    if (btnMostrarMenos) btnMostrarMenos.style.display = 'none';
};

// Navegación suave
const initSmoothScrolling = () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
};

// Efecto del navbar al hacer scroll
const initNavbarScrollEffect = () => {
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (window.scrollY > 100) {
            header.style.background = 'rgba(0,0,0,0.9)';
        } else {
            header.style.background = 'transparent';
        }
    });
};

// Botones del hero
const initHeroButtons = () => {
    document.querySelectorAll('.hero-buttons .hero-button').forEach(btn => {
        if (btn.dataset.action === 'carta') {
            btn.onclick = () => {
                const target = document.getElementById('carta-section');
                if (target) target.scrollIntoView({behavior: 'smooth'});
            };
        }
        if (btn.dataset.action === 'historia') {
            btn.onclick = () => {
                const target = document.getElementById('cocktails-section');
                if (target) target.scrollIntoView({behavior: 'smooth'});
            };
        }
    });
};

// Delegación de eventos para botones "Ver producto"
const initProductButtons = () => {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-green') && e.target.dataset.productoId) {
            const productoId = e.target.dataset.productoId;
            alert(`Ver detalles del producto ID: ${productoId}`);
            // Aquí puedes agregar la lógica para mostrar detalles del producto
        }
    });
};

// Efectos de click en botones
const initButtonEffects = () => {
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
};

// Event listeners para botones de productos
const initProductsPagination = () => {
    const btnMostrarMas = document.getElementById('mostrar-mas-productos');
    const btnMostrarMenos = document.getElementById('mostrar-menos-productos');
    
    if (btnMostrarMas) {
        btnMostrarMas.addEventListener('click', cargarMasProductos);
    }
    
    if (btnMostrarMenos) {
        btnMostrarMenos.addEventListener('click', mostrarMenosProductos);
    }
};

// Funcionalidad del newsletter
const initNewsletter = () => {
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('.newsletter-input');
            const email = emailInput.value.trim();
            
            if (email) {
                // Aquí puedes agregar la lógica para enviar el email al backend
                alert(`¡Gracias por suscribirte! Enviaremos novedades a: ${email}`);
                emailInput.value = '';
                
                // Opcional: enviar datos al servidor
                // fetch('/newsletter/subscribe/', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //         'X-CSRFToken': getCookie('csrftoken')
                //     },
                //     body: JSON.stringify({ email: email })
                // });
            }
        });
    }
};

// Smooth scroll para enlaces del footer
const initFooterNavigation = () => {
    document.querySelectorAll('.footer-section a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
};

// Animaciones para iconos sociales
const initSocialIcons = () => {
    document.querySelectorAll('.social-icon').forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.1)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
};

// Validación mejorada del newsletter
const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// Función para obtener cookie CSRF (si es necesario para Django)
const getCookie = (name) => {
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
};

// Hero Carousel functionality
let currentSlide = 0;
let slideInterval;
let slides = [];
let dots = [];

const showSlide = (index) => {
    // Remove active class from all slides and dots
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    // Add active class to current slide and dot
    if (slides[index]) {
        slides[index].classList.add('active');
    }
    if (dots[index]) {
        dots[index].classList.add('active');
    }
    
    currentSlide = index;
};

const nextSlide = () => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
};

const startCarousel = () => {
    if (slideInterval) {
        clearInterval(slideInterval);
    }
    slideInterval = setInterval(nextSlide, 4000); // Change slide every 4 seconds
};

const stopCarousel = () => {
    if (slideInterval) {
        clearInterval(slideInterval);
    }
};

const initHeroCarousel = () => {
    // Define slides and dots after DOM is loaded
    slides = document.querySelectorAll('.hero-slide');
    dots = document.querySelectorAll('.hero-dot');
    
    if (slides.length === 0) {
        return;
    }
    
    // Initialize first slide
    showSlide(0);
    
    // Add click event to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            stopCarousel();
            showSlide(index);
            startCarousel();
        });
    });
    
    // Pause carousel on hover
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.addEventListener('mouseenter', stopCarousel);
        heroSection.addEventListener('mouseleave', startCarousel);
    }
    
    // Start the carousel immediately
    startCarousel();
};

// Preload images for better performance
const preloadHeroImages = () => {
    const imageUrls = [
        'https://images.unsplash.com/photo-1516997121675-4c2d1684aa3e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
        'https://images.unsplash.com/photo-1551024601-bec78aea704b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2080&q=80',
        'https://images.unsplash.com/photo-1470337458703-46ad1756a187?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
        'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
        'https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
        'https://images.unsplash.com/photo-1519864600265-abb23847ef2c?auto=format&fit=crop&w=2070&q=80'
    ];
    
    imageUrls.forEach(url => {
        const img = new Image();
        img.src = url;
    });
};

// Actualizar la función init para incluir el carrusel
const init = () => {
    preloadHeroImages();
    initHeroCarousel();
    initWebSocket();
    initSmoothScrolling();
    initNavbarScrollEffect();
    initHeroButtons();
    initProductButtons();
    initButtonEffects();
    initProductsPagination();
    initNewsletter();
    initFooterNavigation();
    initSocialIcons();
};

// Ejecutar cuando el DOM esté cargado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

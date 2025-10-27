/**
 * QuickFill - UI Enhancements
 * Modern interactions, animations, and effects
 */

(function() {
    'use strict';

    // ========================================
    // SMOOTH SCROLL & PARALLAX
    // ========================================
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Parallax effect on scroll
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                handleScrollEffects();
                ticking = false;
            });
            ticking = true;
        }
    });

    function handleScrollEffects() {
        const scrolled = window.pageYOffset;
        
        // Parallax backgrounds
        document.querySelectorAll('.parallax-bg').forEach(el => {
            const speed = el.dataset.speed || 0.5;
            el.style.transform = `translateY(${scrolled * speed}px)`;
        });

        // Reveal animations
        document.querySelectorAll('.scroll-reveal').forEach(el => {
            const rect = el.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            
            if (rect.top < windowHeight * 0.85) {
                el.classList.add('active');
            }
        });
    }

    // ========================================
    // INTERACTIVE CARDS & BUTTONS
    // ========================================
    
    // Tilt effect on cards
    document.querySelectorAll('.tilt-card, .feature-item, .station-card').forEach(card => {
        card.addEventListener('mousemove', handleTilt);
        card.addEventListener('mouseleave', resetTilt);
    });

    function handleTilt(e) {
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    }

    function resetTilt(e) {
        const card = e.currentTarget;
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
    }

    // Ripple effect on buttons
    document.querySelectorAll('button, .btn, .hero-btn').forEach(button => {
        button.addEventListener('click', createRipple);
    });

    function createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple-effect');
        
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    // ========================================
    // LOADING STATES & SKELETONS
    // ========================================
    
    window.showLoading = function(container) {
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
        container.appendChild(loader);
    };

    window.hideLoading = function(container) {
        const loader = container.querySelector('.loading-overlay');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 300);
        }
    };

    // ========================================
    // TOAST NOTIFICATIONS
    // ========================================
    
    window.showToast = function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slideInTop`;
        
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        
        toast.innerHTML = `
            ${icons[type] || icons.info}
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutTop 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    };

    // ========================================
    // CUSTOM CURSOR (OPTIONAL)
    // ========================================
    
    if (window.innerWidth > 768) {
        const cursor = document.createElement('div');
        cursor.className = 'custom-cursor';
        document.body.appendChild(cursor);
        
        const cursorDot = document.createElement('div');
        cursorDot.className = 'custom-cursor-dot';
        document.body.appendChild(cursorDot);
        
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
            
            cursorDot.style.left = e.clientX + 'px';
            cursorDot.style.top = e.clientY + 'px';
        });
        
        // Expand cursor on hover over interactive elements
        document.querySelectorAll('a, button, .station-card, .feature-item').forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.classList.add('expand');
            });
            el.addEventListener('mouseleave', () => {
                cursor.classList.remove('expand');
            });
        });
    }

    // ========================================
    // NUMBER ANIMATION (COUNT UP)
    // ========================================
    
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = current;
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }

    // Animate numbers when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = entry.target;
                const endValue = parseInt(target.dataset.count || target.textContent);
                target.dataset.animated = 'true';
                animateValue(target, 0, endValue, 2000);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-number, .count-up').forEach(el => {
        observer.observe(el);
    });

    // ========================================
    // PAGE TRANSITION
    // ========================================
    
    document.querySelectorAll('a:not([target="_blank"])').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only apply to internal links
            if (href && !href.startsWith('#') && !href.startsWith('http')) {
                e.preventDefault();
                
                document.body.classList.add('page-transition-out');
                
                setTimeout(() => {
                    window.location.href = href;
                }, 400);
            }
        });
    });

    // Remove transition class on page load
    window.addEventListener('load', () => {
        document.body.classList.remove('page-transition-out');
    });

    // ========================================
    // ENHANCED FORM INTERACTIONS
    // ========================================
    
    // Floating labels
    document.querySelectorAll('.input-wrapper input, .input-wrapper textarea').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Check on load
        if (input.value) {
            input.parentElement.classList.add('focused');
        }
    });

    // ========================================
    // IMAGE LAZY LOADING WITH BLUR-UP
    // ========================================
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });

    // ========================================
    // THEME TOGGLE (Optional)
    // ========================================
    
    window.toggleTheme = function() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    };

    // Load saved theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }

    // ========================================
    // INITIALIZE ON DOM READY
    // ========================================
    
    console.log('🚀 QuickFill UI Enhancements Loaded');
    
    // Trigger scroll reveal on load
    handleScrollEffects();
    
})();

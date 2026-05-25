/**
 * Responsive Utilities - FASE 2 Enhancement
 * Professional Soccer Predictions System
 *
 * Provides JavaScript helpers for responsive behavior enhancements
 */

(function() {
    'use strict';

    // Viewport detection
    const viewportDetector = {
        isMobile: () => window.matchMedia('(max-width: 640px)').matches,
        isTablet: () => window.matchMedia('(min-width: 641px) and (max-width: 768px)').matches,
        isDesktop: () => window.matchMedia('(min-width: 769px)').matches,
        isTouchDevice: () => 'ontouchstart' in window || navigator.maxTouchPoints > 0,

        get current() {
            if (this.isMobile()) return 'mobile';
            if (this.isTablet()) return 'tablet';
            return 'desktop';
        }
    };

    // Auto-collapse on mobile
    function initMobileCollapse() {
        if (!viewportDetector.isMobile()) return;

        // Auto-collapse sidebars on mobile
        const sidebars = document.querySelectorAll('.sidebar-collapse');
        sidebars.forEach(sidebar => {
            sidebar.classList.add('collapsed');

            // Add toggle button if not exists
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-sm btn-outline-primary mb-3 w-100';
            toggleBtn.innerHTML = '<i class="bi bi-list"></i> Menu';
            toggleBtn.onclick = () => sidebar.classList.toggle('collapsed');

            sidebar.parentElement.insertBefore(toggleBtn, sidebar);
        });
    }

    // Chart responsive adjustments
    function adjustChartSizes() {
        const charts = document.querySelectorAll('canvas');

        charts.forEach(canvas => {
            const container = canvas.closest('.chart-container, .chart-container-professional');
            if (!container) return;

            // Force chart redraw on resize with debounce
            const resizeObserver = new ResizeObserver(debounce(() => {
                const chart = Chart.getChart(canvas);
                if (chart) {
                    chart.resize();
                }
            }, 150));

            resizeObserver.observe(container);
        });
    }

    // Touch-friendly table scrolling
    function enhanceTableScroll() {
        const tables = document.querySelectorAll('table:not(.table-responsive table)');

        tables.forEach(table => {
            if (viewportDetector.isMobile()) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                wrapper.style.overflowX = 'auto';
                wrapper.style.webkitOverflowScrolling = 'touch';

                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }

    // Sticky navigation on mobile
    function initStickyNav() {
        const navbar = document.querySelector('.navbar, nav');
        if (!navbar || !viewportDetector.isMobile()) return;

        let lastScrollTop = 0;
        const delta = 5;

        window.addEventListener('scroll', debounce(() => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (Math.abs(lastScrollTop - scrollTop) <= delta) return;

            if (scrollTop > lastScrollTop && scrollTop > navbar.offsetHeight) {
                // Scrolling down - hide navbar
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up - show navbar
                navbar.style.transform = 'translateY(0)';
            }

            lastScrollTop = scrollTop;
        }, 50));

        // Add transition
        navbar.style.transition = 'transform 0.3s ease';
    }

    // Prevent iOS zoom on form focus
    function preventIOSZoom() {
        if (!/(iPhone|iPad|iPod)/i.test(navigator.userAgent)) return;

        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const fontSize = window.getComputedStyle(input).fontSize;
            const size = parseFloat(fontSize);

            // iOS zooms if font-size < 16px
            if (size < 16) {
                input.style.fontSize = '16px';
            }
        });
    }

    // Debounce utility
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Responsive image lazy loading
    function initLazyLoading() {
        if ('loading' in HTMLImageElement.prototype) {
            // Native lazy loading
            const images = document.querySelectorAll('img[data-src]');
            images.forEach(img => {
                img.src = img.dataset.src;
                img.loading = 'lazy';
            });
        } else {
            // Fallback with IntersectionObserver
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // Viewport info badge (dev mode)
    function showViewportInfo() {
        if (!window.location.search.includes('debug=responsive')) return;

        const badge = document.createElement('div');
        badge.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-family: monospace;
            z-index: 9999;
            pointer-events: none;
        `;

        function update() {
            badge.textContent = `${viewportDetector.current} | ${window.innerWidth}x${window.innerHeight} | ${viewportDetector.isTouchDevice() ? 'Touch' : 'Mouse'}`;
        }

        update();
        window.addEventListener('resize', debounce(update, 100));

        document.body.appendChild(badge);
    }

    // Initialize all enhancements
    function init() {
        // Wait for DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        try {
            initMobileCollapse();
            enhanceTableScroll();
            preventIOSZoom();
            initLazyLoading();
            showViewportInfo();

            // Adjust charts after Chart.js loads
            if (typeof Chart !== 'undefined') {
                adjustChartSizes();
            } else {
                window.addEventListener('load', adjustChartSizes);
            }

            // Optional: sticky nav (commented out by default)
            // initStickyNav();

            console.log('✅ Responsive utilities initialized:', viewportDetector.current);
        } catch (error) {
            console.error('❌ Error initializing responsive utilities:', error);
        }
    }

    // Export utilities globally
    window.ResponsiveUtils = {
        viewport: viewportDetector,
        debounce
    };

    // Auto-init
    init();
})();

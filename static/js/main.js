// Main JavaScript file

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeModals();
    initializeAlerts();
    initializeForms();
    initializeDropdowns();
}

// Modal functionality
function initializeModals() {
    document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.dataset.modalTrigger;
            openModal(modalId);
        });
    });
    
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay.id);
            }
        });
    });
    
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-overlay');
            closeModal(modal.id);
        });
    });
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Alert auto-dismiss
function initializeAlerts() {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

// Form validation
function initializeForms() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showFieldError(field, 'This field is required');
        } else {
            clearFieldError(field);
        }
    });
    
    form.querySelectorAll('input[type="email"]').forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            isValid = false;
            showFieldError(field, 'Please enter a valid email address');
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    let error = field.parentNode.querySelector('.form-error');
    if (!error) {
        error = document.createElement('div');
        error.className = 'form-error';
        field.parentNode.appendChild(error);
    }
    error.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('error');
    const error = field.parentNode.querySelector('.form-error');
    if (error) error.remove();
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Dropdown functionality
function initializeDropdowns() {
    document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const dropdown = trigger.nextElementSibling;
            dropdown.classList.toggle('active');
        });
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
                menu.classList.remove('active');
            });
        }
    });
}

// Fetch API wrapper
async function api(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    try {
        const response = await fetch(url, { ...defaults, ...options });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, message: 'Network error occurred' };
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fade-in`;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
        animation: slideIn 0.3s ease;
    `;
    
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Loading state
function setLoading(element, isLoading) {
    if (isLoading) {
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<span class="loader" style="width: 20px; height: 20px;"></span>';
        element.disabled = true;
    } else {
        element.innerHTML = element.dataset.originalText;
        element.disabled = false;
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format number
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Debounce function
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

// ATS Score Circle Animation
function animateATSScore(element, score) {
    const circle = element.querySelector('.progress');
    const radius = circle.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    
    circle.style.strokeDasharray = circumference;
    circle.style.strokeDashoffset = circumference;
    
    const offset = circumference - (score / 100) * circumference;
    
    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
    }, 100);
    
    // Animate number
    const numberElement = element.querySelector('.score-number');
    let current = 0;
    const increment = score / 50;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= score) {
            current = score;
            clearInterval(timer);
        }
        numberElement.textContent = Math.round(current);
    }, 20);
}

// Skill tag input
function initializeSkillInput(inputId, containerId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    const skills = [];
    
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const skill = input.value.trim();
            if (skill && !skills.includes(skill)) {
                skills.push(skill);
                renderSkills();
            }
            input.value = '';
        }
    });
    
    function renderSkills() {
        container.innerHTML = skills.map((skill, i) => `
            <span class="tag">
                ${skill}
                <button type="button" onclick="removeSkill(${i})" style="background: none; border: none; cursor: pointer; margin-left: 4px;">
                    <i class="fas fa-times"></i>
                </button>
            </span>
        `).join('');
    }
    
    window.removeSkill = (index) => {
        skills.splice(index, 1);
        renderSkills();
    };
    
    return () => skills;
}

// Infinite scroll
function initializeInfiniteScroll(container, loadMore) {
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            loadMore();
        }
    }, { threshold: 0.5 });
    
    const sentinel = document.createElement('div');
    sentinel.className = 'scroll-sentinel';
    container.appendChild(sentinel);
    observer.observe(sentinel);
}

// Export functions for global use
window.openModal = openModal;
window.closeModal = closeModal;
window.showToast = showToast;
window.api = api;
window.setLoading = setLoading;
window.formatDate = formatDate;
window.formatNumber = formatNumber;
window.animateATSScore = animateATSScore;

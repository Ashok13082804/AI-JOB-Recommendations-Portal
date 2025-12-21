// Authentication JavaScript

let currentStep = 1;
const totalSteps = 3;

// Multi-step form navigation
function nextStep() {
    if (!validateCurrentStep()) return;

    if (currentStep < totalSteps) {
        document.querySelector(`.form-step[data-step="${currentStep}"]`).style.display = 'none';
        currentStep++;
        document.querySelector(`.form-step[data-step="${currentStep}"]`).style.display = 'block';
        updateProgressSteps();

        // Start webcam on face step
        if (currentStep === 3) {
            startWebcam('webcam');
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        // Stop webcam if leaving face step
        if (currentStep === 3) {
            stopWebcam();
        }

        document.querySelector(`.form-step[data-step="${currentStep}"]`).style.display = 'none';
        currentStep--;
        document.querySelector(`.form-step[data-step="${currentStep}"]`).style.display = 'block';
        updateProgressSteps();
    }
}

function updateProgressSteps() {
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');

        if (stepNum < currentStep) {
            step.classList.add('completed');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
        }
    });
}

function validateCurrentStep() {
    const step = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    const requiredFields = step.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = 'var(--error)';
            field.addEventListener('input', () => {
                field.style.borderColor = '';
            }, { once: true });
        }
    });

    // Email validation
    const emailField = step.querySelector('input[type="email"]');
    if (emailField && emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
        isValid = false;
        emailField.style.borderColor = 'var(--error)';
    }

    // Password validation
    const passwordField = step.querySelector('input[type="password"]');
    if (passwordField && passwordField.value && passwordField.value.length < 6) {
        isValid = false;
        passwordField.style.borderColor = 'var(--error)';
    }

    if (!isValid) {
        showFormError('Please fill in all required fields correctly.');
    }

    return isValid;
}

function showFormError(message) {
    const errorDiv = document.getElementById('form-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 5000);
    }
}

function skipFace() {
    submitRegistration(null);
}

// Registration form submission
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Get face data from window object (set by face-recognition.js)
            const faceData = window.capturedFaceData || null;
            console.log('Submitting registration with face data:', faceData ? 'yes' : 'no');
            submitRegistration(faceData);
        });
    }
});

async function submitRegistration(faceData) {
    const form = document.getElementById('register-form');
    const formData = new FormData(form);

    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        password: formData.get('password'),
        role: formData.get('role'),
        company_name: formData.get('company_name'),
        headline: formData.get('headline'),
        bio: formData.get('bio'),
        skills: formData.get('skills'),
        face_encoding: faceData
    };

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Registration successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = result.redirect;
            }, 1500);
        } else {
            showFormError(result.message || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showFormError('An error occurred. Please try again.');
    }
}

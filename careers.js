const API_URL = 'http://localhost:5000';

let currentPosition = '';

// Redirect to individual application pages
function redirectToApplication(jobId) {
    window.location.href = `pages/apply.html?job=${jobId}`;
}

// Open application modal
function openApplicationModal(position) {
    currentPosition = position;
    document.getElementById('modalJobTitle').textContent = `Apply for ${position}`;
    document.getElementById('position').value = position;
    document.getElementById('applicationModal').classList.add('active');
    document.getElementById('applicationForm').reset();
}

// Close application modal
function closeApplicationModal() {
    document.getElementById('applicationModal').classList.remove('active');
    document.getElementById('applicationForm').reset();
}

// Close modal when clicking outside
document.getElementById('applicationModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'applicationModal') {
        closeApplicationModal();
    }
});

// Handle form submission
document.getElementById('applicationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.querySelector('.submit-application-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const formData = new FormData(e.target);
        
        // Validate file size
        const resumeFile = document.getElementById('resume').files[0];
        if (resumeFile && resumeFile.size > 5 * 1024 * 1024) {
            showToast('Resume file size must be less than 5MB', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Application';
            return;
        }
        
        // Convert FormData to JSON (excluding file for now)
        const applicationData = {
            position: formData.get('position'),
            fullName: formData.get('fullName'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            address: formData.get('address'),
            college: formData.get('college'),
            degree: formData.get('degree'),
            semester: formData.get('semester'),
            year: formData.get('year'),
            about: formData.get('about'),
            linkedin: formData.get('linkedin') || '',
            github: formData.get('github') || '',
            resumeName: resumeFile.name,
            appliedAt: new Date().toISOString()
        };
        
        // Send to backend
        const response = await fetch(`${API_URL}/api/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(applicationData)
        });
        
        if (response.ok) {
            showSuccessMessage();
            setTimeout(() => {
                closeApplicationModal();
            }, 2000);
        } else {
            const error = await response.json();
            showToast(error.message || 'Failed to submit application', 'error');
        }
    } catch (error) {
        console.error('Application error:', error);
        showToast('Failed to submit application. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Application';
    }
});

// Show success message
function showSuccessMessage() {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message show';
    successDiv.innerHTML = `
        <h3>🎉 Application Submitted Successfully!</h3>
        <p>Thank you for applying to XGENAI. We'll review your application and get back to you soon.</p>
    `;
    
    const form = document.getElementById('applicationForm');
    form.insertBefore(successDiv, form.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: ${type === 'success' ? '#22c55e' : '#ef4444'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// File input styling
document.getElementById('resume')?.addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name;
    if (fileName) {
        const label = this.parentElement.querySelector('small');
        if (label) {
            label.textContent = `Selected: ${fileName}`;
            label.style.color = 'var(--primary-color)';
        }
    }
});

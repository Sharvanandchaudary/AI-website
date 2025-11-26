// Job Application Form Handler
const API_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'https://your-backend-url.com';

// Get job title from URL parameter or page title
function getJobTitle() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('position') || document.querySelector('h1').textContent.replace('Apply for ', '');
}

// Handle form submission
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const formData = new FormData(form);
            
            // Prepare application data
            const applicationData = {
                position: formData.get('position') || getJobTitle(),
                fullName: formData.get('fullName') || formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                address: formData.get('address') || 'Not provided',
                college: formData.get('college') || 'Not provided',
                degree: formData.get('degree') || 'Not provided',
                semester: formData.get('semester') || 'Not provided',
                year: formData.get('year') || 'Not provided',
                about: formData.get('about') || `Applied for ${formData.get('position') || getJobTitle()}`,
                resumeName: formData.get('resume') && formData.get('resume').name ? formData.get('resume').name : 'resume.pdf',
                linkedin: formData.get('linkedin') || '',
                github: formData.get('github') || ''
            };

            // Submit application
            const response = await fetch(`${API_URL}/api/applications`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(applicationData)
            });

            const result = await response.json();

            if (response.ok) {
                // Show success message
                alert('Application submitted successfully! We will contact you soon.');
                form.reset();
                // Redirect to careers page after 2 seconds
                setTimeout(() => {
                    window.location.href = '../careers.html';
                }, 2000);
            } else {
                alert('Error: ' + (result.error || 'Failed to submit application'));
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        } catch (error) {
            console.error('Error submitting application:', error);
            alert('Failed to submit application. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
});

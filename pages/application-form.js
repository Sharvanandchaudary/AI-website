// Job Application Form Handler
const API_URL = window.location.origin;

// Get job title from URL parameter or page title
function getJobTitle() {
    const urlParams = new URLSearchParams(window.location.search);
    const jobParam = urlParams.get('job') || urlParams.get('position');
    
    // Map job IDs to position names
    const jobMap = {
        'job1': 'AI Intern',
        'job2': 'Machine Learning Intern',
        'job3': 'MedTech Intern',
        'job4': 'Full Stack Developer Intern',
        'job5': 'Data Science Intern',
        'job6': 'Software Engineering Intern'
    };
    
    return jobMap[jobParam] || jobParam || document.querySelector('h1')?.textContent.replace('Apply for ', '') || 'General Application';
}

// Handle form submission
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (!form) {
        console.error('Application form not found');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const formData = new FormData(form);
            
            // Get position from URL or form
            const position = getJobTitle();
            
            // Prepare application data with proper field mapping
            const applicationData = {
                position: position,
                fullName: formData.get('fullName') || formData.get('name') || '',
                email: formData.get('email') || '',
                phone: formData.get('phone') || '',
                address: formData.get('address') || '',
                college: formData.get('college') || '',
                degree: formData.get('degree') || '',
                semester: formData.get('semester') || '',
                year: formData.get('year') || '',
                about: formData.get('about') || formData.get('message') || `Applying for ${position}`,
                resumeName: formData.get('resume')?.name || 'resume.pdf',
                linkedin: formData.get('linkedin') || '',
                github: formData.get('github') || ''
            };

            console.log('Submitting application to:', `${API_URL}/api/applications`);
            console.log('Application data:', applicationData);

            // Validate required fields
            const requiredFields = ['fullName', 'email', 'phone', 'address', 'college', 'degree', 'semester', 'year'];
            const missingFields = requiredFields.filter(field => !applicationData[field]);
            
            if (missingFields.length > 0) {
                throw new Error(`Please fill in all required fields: ${missingFields.join(', ')}`);
            }

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
                alert('✅ Application submitted successfully! We will contact you soon.');
                form.reset();
                // Redirect to careers page after 1.5 seconds
                setTimeout(() => {
                    window.location.href = '/careers';
                }, 1500);
            } else {
                console.error('Application submission error:', result);
                throw new Error(result.error || 'Failed to submit application');
            }
        } catch (error) {
            console.error('Error submitting application:', error);
            alert('❌ Failed to submit application: ' + error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
});

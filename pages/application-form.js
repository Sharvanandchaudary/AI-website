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

            if (response.ok && result.success) {
                // Show success message
                alert(result.message || '✅ Application submitted successfully! We will contact you soon.');
                form.reset();
                
                // Show a more visible success message
                const successDiv = document.createElement('div');
                successDiv.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #10b981; color: white; padding: 20px 40px; border-radius: 12px; font-size: 18px; font-weight: 600; box-shadow: 0 10px 40px rgba(16, 185, 129, 0.4); z-index: 9999;';
                successDiv.textContent = '✅ Application Submitted Successfully!';
                document.body.appendChild(successDiv);
                
                // Redirect to careers page after 2 seconds
                setTimeout(() => {
                    window.location.href = '/careers';
                }, 2000);
            } else {
                console.error('Application submission error:', result);
                throw new Error(result.error || 'Failed to submit application');
            }
        } catch (error) {
            console.error('Error submitting application:', error);
            
            // Show error message with more details
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #ef4444; color: white; padding: 20px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; box-shadow: 0 10px 40px rgba(239, 68, 68, 0.4); z-index: 9999; max-width: 500px; text-align: center;';
            errorDiv.innerHTML = `❌ Failed to submit application<br><small style="font-size: 14px; font-weight: 400; margin-top: 8px; display: block;">${error.message}</small>`;
            document.body.appendChild(errorDiv);
            
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
            
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
});

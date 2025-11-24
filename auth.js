// Form Elements
const loginCard = document.getElementById('loginCard');
const signupCard = document.getElementById('signupCard');
const successCard = document.getElementById('successCard');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const showSignupBtn = document.getElementById('showSignup');
const showLoginBtn = document.getElementById('showLogin');
const goToLoginBtn = document.getElementById('goToLogin');
const toast = document.getElementById('toast');

// Switch to Signup
showSignupBtn.addEventListener('click', (e) => {
    e.preventDefault();
    loginCard.style.display = 'none';
    signupCard.style.display = 'block';
    successCard.style.display = 'none';
});

// Switch to Login
showLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    signupCard.style.display = 'none';
    loginCard.style.display = 'block';
    successCard.style.display = 'none';
});

// Go to Login from Success
goToLoginBtn.addEventListener('click', () => {
    successCard.style.display = 'none';
    loginCard.style.display = 'block';
});

// Show Toast Notification
function showToast(message, type = 'success') {
    const toastMessage = document.getElementById('toastMessage');
    toastMessage.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Validate Email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate Phone
function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// Password Strength Checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/\d/)) strength++;
    if (password.match(/[^a-zA-Z\d]/)) strength++;
    return strength;
}

// Handle Login Form
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const submitBtn = loginForm.querySelector('.auth-btn');
    
    // Validate
    if (!isValidEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    // Show loading
    submitBtn.classList.add('loading');
    
    // Simulate API call
    setTimeout(() => {
        // Check if user exists in localStorage
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        const user = users.find(u => u.email === email && u.password === password);
        
        submitBtn.classList.remove('loading');
        
        if (user) {
            showToast('Login successful! Redirecting...', 'success');
            localStorage.setItem('currentUser', JSON.stringify(user));
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            showToast('Invalid email or password', 'error');
        }
    }, 1500);
});

// Handle Signup Form
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const phone = document.getElementById('signupPhone').value.trim();
    const address = document.getElementById('signupAddress').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const submitBtn = signupForm.querySelector('.auth-btn');
    
    // Validate Name
    if (name.length < 2) {
        showToast('Please enter a valid name', 'error');
        return;
    }
    
    // Validate Email
    if (!isValidEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    // Validate Phone
    if (!isValidPhone(phone)) {
        showToast('Please enter a valid phone number', 'error');
        return;
    }
    
    // Validate Address
    if (address.length < 10) {
        showToast('Please enter a complete address', 'error');
        return;
    }
    
    // Validate Password
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    // Check Password Match
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    // Show loading
    submitBtn.classList.add('loading');
    
    // Simulate API call and email sending
    setTimeout(() => {
        // Check if user already exists
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        const existingUser = users.find(u => u.email === email);
        
        if (existingUser) {
            submitBtn.classList.remove('loading');
            showToast('An account with this email already exists', 'error');
            return;
        }
        
        // Create new user
        const newUser = {
            id: Date.now(),
            name,
            email,
            phone,
            address,
            password,
            createdAt: new Date().toISOString()
        };
        
        // Save to localStorage
        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));
        
        // Send confirmation email (simulated)
        sendConfirmationEmail(newUser);
        
        submitBtn.classList.remove('loading');
        
        // Show success card
        document.getElementById('userEmail').textContent = email;
        signupCard.style.display = 'none';
        successCard.style.display = 'block';
        
        // Reset form
        signupForm.reset();
    }, 2000);
});

// Simulate Email Sending
function sendConfirmationEmail(user) {
    // In a real application, this would send an actual email
    // For now, we'll just log it and show in console
    const emailContent = {
        to: user.email,
        subject: 'Welcome to AI Solutions - Account Created Successfully!',
        body: `
            Hi ${user.name},
            
            Welcome to AI Solutions!
            
            Your account has been created successfully. Here are your details:
            
            Name: ${user.name}
            Email: ${user.email}
            Phone: ${user.phone}
            Address: ${user.address}
            Account Created: ${new Date(user.createdAt).toLocaleString()}
            
            Thank you for joining us!
            
            Best regards,
            AI Solutions Team
        `
    };
    
    console.log('📧 Confirmation Email Sent:', emailContent);
    
    // Store email in localStorage for demo purposes
    const emails = JSON.parse(localStorage.getItem('emails') || '[]');
    emails.push({
        ...emailContent,
        sentAt: new Date().toISOString()
    });
    localStorage.setItem('emails', JSON.stringify(emails));
    
    // Show in toast
    showToast('Confirmation email sent successfully!', 'success');
}

// Password Strength Indicator
const signupPassword = document.getElementById('signupPassword');
if (signupPassword) {
    // Add strength indicator
    const strengthDiv = document.createElement('div');
    strengthDiv.className = 'password-strength';
    strengthDiv.innerHTML = '<div class="password-strength-bar"></div>';
    signupPassword.parentElement.appendChild(strengthDiv);
    
    signupPassword.addEventListener('input', (e) => {
        const password = e.target.value;
        const strengthBar = strengthDiv.querySelector('.password-strength-bar');
        const strength = checkPasswordStrength(password);
        
        strengthBar.className = 'password-strength-bar';
        
        if (password.length === 0) {
            strengthBar.style.width = '0';
        } else if (strength <= 1) {
            strengthBar.classList.add('weak');
        } else if (strength <= 2) {
            strengthBar.classList.add('medium');
        } else {
            strengthBar.classList.add('strong');
        }
    });
}

// Auto-format phone number
const phoneInput = document.getElementById('signupPhone');
if (phoneInput) {
    phoneInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 0) {
            if (value.length <= 3) {
                value = `(${value}`;
            } else if (value.length <= 6) {
                value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
            } else {
                value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
            }
        }
        e.target.value = value;
    });
}

// Check if user is already logged in
window.addEventListener('load', () => {
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser && window.location.pathname.includes('auth.html')) {
        showToast('You are already logged in', 'success');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    }
});

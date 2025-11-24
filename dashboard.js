const API_URL = 'http://localhost:5000';

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return false;
    }
    return token;
}

// Load user data and projects
async function loadDashboard() {
    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch(`${API_URL}/api/user/dashboard`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Failed to load dashboard');
        }

        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

// Update dashboard with data
function updateDashboard(data) {
    // Update user info
    document.getElementById('userName').textContent = data.user.name;
    document.getElementById('joinDate').textContent = formatDate(data.user.created_at);
    
    // Update stats
    document.getElementById('totalProjects').textContent = data.projects.length;
    document.getElementById('activeProjects').textContent = 
        data.projects.filter(p => p.status === 'active').length;
    document.getElementById('completedProjects').textContent = 
        data.projects.filter(p => p.status === 'completed').length;
    document.getElementById('daysActive').textContent = calculateDaysActive(data.user.created_at);
    
    // Update profile
    document.getElementById('profileName').textContent = data.user.name;
    document.getElementById('profileEmail').textContent = data.user.email;
    document.getElementById('profilePhone').textContent = data.user.phone || 'Not provided';
    document.getElementById('profileAddress').textContent = data.user.address || 'Not provided';
    document.getElementById('profileJoinDate').textContent = formatDate(data.user.created_at);
    document.getElementById('profileLastLogin').textContent = formatDate(data.user.last_login);
    
    // Update projects
    displayProjects(data.projects);
}

// Display projects
function displayProjects(projects) {
    const projectsGrid = document.getElementById('projectsGrid');
    
    if (projects.length === 0) {
        projectsGrid.innerHTML = `
            <div class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <p>No projects yet. Click "Add Project" to get started!</p>
            </div>
        `;
        return;
    }
    
    projectsGrid.innerHTML = projects.map(project => `
        <div class="project-card">
            <div class="project-header">
                <h3 class="project-title">${escapeHtml(project.name)}</h3>
                <span class="project-status status-${project.status}">${project.status}</span>
            </div>
            <p class="project-description">${escapeHtml(project.description)}</p>
            <div class="project-meta">
                <span>Created: ${formatDate(project.created_at)}</span>
                <span>Updated: ${formatDate(project.updated_at)}</span>
            </div>
        </div>
    `).join('');
}

// Add new project
document.getElementById('addProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const token = checkAuth();
    if (!token) return;
    
    const projectData = {
        name: document.getElementById('projectName').value,
        description: document.getElementById('projectDescription').value,
        status: document.getElementById('projectStatus').value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/user/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(projectData)
        });
        
        if (!response.ok) throw new Error('Failed to add project');
        
        showToast('Project added successfully!', 'success');
        closeAddProjectModal();
        document.getElementById('addProjectForm').reset();
        loadDashboard();
    } catch (error) {
        console.error('Error adding project:', error);
        showToast('Failed to add project', 'error');
    }
});

// Modal functions
function openAddProjectModal() {
    document.getElementById('addProjectModal').classList.add('active');
}

function closeAddProjectModal() {
    document.getElementById('addProjectModal').classList.remove('active');
}

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'auth.html';
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function calculateDaysActive(joinDate) {
    const start = new Date(joinDate);
    const now = new Date();
    const diff = Math.floor((now - start) / (1000 * 60 * 60 * 24));
    return diff;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Load dashboard on page load
loadDashboard();

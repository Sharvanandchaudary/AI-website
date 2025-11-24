const API_URL = 'http://localhost:5000';

// Check if admin is logged in (for now, any logged-in user can access)
function checkAuth() {
    const token = localStorage.getItem('token');
    // For development: allow access without login
    // Remove this if statement for production
    if (!token) {
        // Generate a temporary token for admin access
        const tempToken = 'admin-temp-token';
        localStorage.setItem('token', tempToken);
        return tempToken;
    }
    return token;
}

// Load all admin data
async function loadAdminData() {
    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch(`${API_URL}/api/admin/all-data`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                logout();
                return;
            }
            throw new Error('Failed to load admin data');
        }

        const data = await response.json();
        updateAdminDashboard(data);
    } catch (error) {
        console.error('Error loading admin data:', error);
        showToast('Failed to load admin data', 'error');
    }
}

// Update admin dashboard
function updateAdminDashboard(data) {
    // Update stats
    document.getElementById('totalUsers').textContent = data.users.length;
    
    let totalProjects = 0;
    let activeProjects = 0;
    data.users.forEach(user => {
        totalProjects += user.projects.length;
        activeProjects += user.projects.filter(p => p.status === 'active').length;
    });
    
    document.getElementById('totalProjects').textContent = totalProjects;
    document.getElementById('activeProjects').textContent = activeProjects;
    
    // Calculate new users in last 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const newUsers = data.users.filter(u => new Date(u.created_at) > sevenDaysAgo).length;
    document.getElementById('newUsers').textContent = newUsers;
    
    // Update users table
    displayUsersTable(data.users);
}

// Display users table
function displayUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${escapeHtml(user.name)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td>${escapeHtml(user.phone || 'N/A')}</td>
            <td>${user.projects.length}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>${formatDate(user.last_login)}</td>
            <td>
                <button class="view-dashboard-btn" onclick='viewUserDashboard(${JSON.stringify(user)})'>
                    View Dashboard
                </button>
            </td>
        </tr>
    `).join('');
}

// View user dashboard
function viewUserDashboard(user) {
    document.getElementById('modalUserName').textContent = `${user.name}'s Dashboard`;
    document.getElementById('detailName').textContent = user.name;
    document.getElementById('detailEmail').textContent = user.email;
    document.getElementById('detailPhone').textContent = user.phone || 'Not provided';
    document.getElementById('detailAddress').textContent = user.address || 'Not provided';
    document.getElementById('detailJoinDate').textContent = formatDate(user.created_at);
    document.getElementById('detailLastLogin').textContent = formatDate(user.last_login);
    
    // Display projects
    const projectsContainer = document.getElementById('userProjects');
    if (user.projects.length === 0) {
        projectsContainer.innerHTML = '<p style="color: var(--text-secondary);">No projects yet</p>';
    } else {
        projectsContainer.innerHTML = user.projects.map(project => `
            <div class="mini-project-card">
                <div class="mini-project-title">${escapeHtml(project.name)}</div>
                <span class="mini-project-status status-${project.status}">${project.status}</span>
                <p style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">
                    ${escapeHtml(project.description)}
                </p>
                <p style="color: var(--text-secondary); font-size: 0.7rem; margin-top: 0.5rem;">
                    Created: ${formatDate(project.created_at)}
                </p>
            </div>
        `).join('');
    }
    
    document.getElementById('userModal').classList.add('active');
}

function closeUserModal() {
    document.getElementById('userModal').classList.remove('active');
}

// Search functionality
document.getElementById('searchBox').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const rows = document.querySelectorAll('#usersTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
});

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
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
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

// Load data on page load
loadAdminData();

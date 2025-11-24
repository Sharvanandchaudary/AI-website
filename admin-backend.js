// API Configuration
const API_URL = 'http://localhost:5000/api';

async function loadDashboard() {
    try {
        // Fetch statistics
        const statsResponse = await fetch(`${API_URL}/stats`);
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            document.getElementById('totalUsers').textContent = stats.total_users || 0;
            document.getElementById('totalEmails').textContent = stats.total_emails || 0;
            document.getElementById('todayUsers').textContent = stats.today_users || 0;
        }

        // Fetch users
        const usersResponse = await fetch(`${API_URL}/users`);
        if (usersResponse.ok) {
            const usersData = await usersResponse.json();
            const users = usersData.users || [];
            
            const usersTableBody = document.getElementById('usersTableBody');
            if (users.length === 0) {
                usersTableBody.innerHTML = '<tr><td colspan="7" class="no-data">No users registered yet</td></tr>';
            } else {
                usersTableBody.innerHTML = users.map((user, index) => `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${user.name}</td>
                        <td>${user.email}</td>
                        <td>${user.phone}</td>
                        <td>${user.address}</td>
                        <td>${new Date(user.created_at).toLocaleString()}</td>
                        <td>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                    </tr>
                `).join('');
            }
        }

        // Fetch emails
        const emailsResponse = await fetch(`${API_URL}/emails`);
        if (emailsResponse.ok) {
            const emailsData = await emailsResponse.json();
            const emails = emailsData.emails || [];
            
            const emailsTableBody = document.getElementById('emailsTableBody');
            if (emails.length === 0) {
                emailsTableBody.innerHTML = '<tr><td colspan="6" class="no-data">No emails sent yet</td></tr>';
            } else {
                emailsTableBody.innerHTML = emails.map((email, index) => `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${email.to}</td>
                        <td>${email.subject}</td>
                        <td>${new Date(email.sent_at).toLocaleString()}</td>
                        <td>${email.user_name || 'N/A'}</td>
                        <td><div class="email-content">${email.body.substring(0, 100)}...</div></td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
        try {
            const response = await fetch(`${API_URL}/clear-data`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('All data cleared successfully!');
                loadDashboard();
            } else {
                const data = await response.json();
                alert('Error: ' + (data.error || 'Failed to clear data'));
            }
        } catch (error) {
            console.error('Error clearing data:', error);
            alert('Connection error. Please try again.');
        }
    }
}

// Load dashboard on page load
loadDashboard();

// Refresh every 5 seconds
setInterval(loadDashboard, 5000);

const API_URL = window.location.origin;
let currentIntern = null;
let currentTasks = [];
let selectedFile = null;

// Check authentication on page load
window.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('intern_token');
    
    if (!token) {
        window.location.href = '/intern/login';
        return;
    }
    
    // Load intern data
    const storedIntern = localStorage.getItem('intern_data');
    if (storedIntern) {
        currentIntern = JSON.parse(storedIntern);
        updateInternInfo();
    }
    
    // Load dashboard data
    await loadDashboard();
});

function updateInternInfo() {
    if (currentIntern) {
        document.getElementById('internName').textContent = currentIntern.name;
        document.getElementById('internPosition').textContent = currentIntern.position;
    }
}

async function loadDashboard() {
    const token = localStorage.getItem('intern_token');
    
    try {
        const response = await fetch(`${API_URL}/api/intern/dashboard`, {
            headers: {
                'Authorization': token
            }
        });
        
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.clear();
            window.location.href = '/intern/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load dashboard');
        }
        
        const data = await response.json();
        
        // Update current week
        document.getElementById('currentWeek').textContent = data.current_week;
        
        // Update progress
        const progress = data.progress;
        const percentage = progress.total > 0 
            ? Math.round((progress.completed / progress.total) * 100) 
            : 0;
        
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = percentage + '%';
        progressFill.textContent = percentage + '%';
        
        // Load tasks
        currentTasks = data.tasks;
        renderTasks(data.tasks);
        
        // Load submissions
        renderSubmissions(data.submissions);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

function renderTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        document.getElementById('tasksContainer').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <p>No tasks assigned for this week</p>
            </div>
        `;
        return;
    }
    
    // Regular tasks
    const regularTasks = tasks.filter(t => !t.mini_project_guidelines && !t.ds_algo_topic && !t.ai_news);
    const miniProjects = tasks.filter(t => t.mini_project_guidelines);
    const dsAlgo = tasks.filter(t => t.ds_algo_topic);
    const aiNews = tasks.filter(t => t.ai_news);
    
    // Render regular tasks
    if (regularTasks.length > 0) {
        document.getElementById('tasksContainer').innerHTML = regularTasks.map(task => `
            <div class="task-item">
                <h4>${task.title}</h4>
                <p>${task.description}</p>
                <div class="task-meta">
                    <span><i class="fas fa-calendar"></i> Week ${task.week_number}</span>
                    ${task.due_date ? `<span><i class="fas fa-clock"></i> Due: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    // Render mini projects
    if (miniProjects.length > 0) {
        document.getElementById('miniProjectContainer').innerHTML = miniProjects.map(task => `
            <div class="task-item mini-project">
                <h4><i class="fas fa-code"></i> ${task.title}</h4>
                <p>${task.description}</p>
                <div class="learning-notes">
                    <h4>Guidelines:</h4>
                    <p style="color: #ccc;">${task.mini_project_guidelines}</p>
                </div>
                <div class="task-meta">
                    ${task.due_date ? `<span><i class="fas fa-clock"></i> Due: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    // Render DS & Algo
    if (dsAlgo.length > 0) {
        document.getElementById('dsAlgoContainer').innerHTML = dsAlgo.map(task => `
            <div class="task-item ds-algo">
                <h4><i class="fas fa-brain"></i> ${task.ds_algo_topic}</h4>
                <p>${task.description}</p>
                <div class="task-meta">
                    <span><i class="fas fa-book"></i> Study Topic</span>
                    ${task.due_date ? `<span><i class="fas fa-clock"></i> Complete by: ${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    // Render AI News
    if (aiNews.length > 0) {
        document.getElementById('aiNewsContainer').innerHTML = aiNews.map(task => `
            <div class="task-item ai-news">
                <h4><i class="fas fa-newspaper"></i> ${task.title}</h4>
                <div class="learning-notes">
                    <p style="color: #ccc;">${task.ai_news}</p>
                </div>
            </div>
        `).join('');
    }
    
    // Populate task select dropdown
    const taskSelect = document.getElementById('taskSelect');
    taskSelect.innerHTML = '<option value="">Choose a task...</option>' + 
        tasks.map(task => `
            <option value="${task.id}">${task.title} (Week ${task.week_number})</option>
        `).join('');
}

function renderSubmissions(submissions) {
    if (!submissions || submissions.length === 0) {
        document.getElementById('historyContainer').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clock"></i>
                <p>No submissions yet. Complete your first task!</p>
            </div>
        `;
        return;
    }
    
    document.getElementById('historyContainer').innerHTML = submissions.map(sub => `
        <div class="history-item">
            <div class="history-info">
                <h4>${sub.task_title}</h4>
                <p>Week ${sub.week_number} • Submitted on ${formatDateTime(sub.submitted_at)}</p>
                ${sub.what_learned ? `<p style="color: #00ff88; font-style: italic; margin-top: 8px;">"${truncate(sub.what_learned, 100)}"</p>` : ''}
            </div>
            <span class="status-badge status-${sub.status}">${capitalize(sub.status)}</span>
        </div>
    `).join('');
}

// File upload handling
document.getElementById('fileUpload').addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

document.getElementById('fileInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showError('File size must be less than 5MB');
            return;
        }
        
        // Check file type
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
        if (!allowedTypes.includes(file.type)) {
            showError('Only PDF, PNG, and JPG files are allowed');
            return;
        }
        
        selectedFile = file;
        document.getElementById('fileName').innerHTML = `
            <i class="fas fa-check-circle"></i> ${file.name} (${(file.size / 1024).toFixed(2)} KB)
        `;
        
        // Convert to base64
        const reader = new FileReader();
        reader.onload = (e) => {
            selectedFile.base64 = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// Form submission
document.getElementById('submissionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const taskId = document.getElementById('taskSelect').value;
    const whatLearned = document.getElementById('whatLearned').value;
    
    if (!taskId) {
        showError('Please select a task');
        return;
    }
    
    if (!selectedFile) {
        showError('Please upload a file');
        return;
    }
    
    const token = localStorage.getItem('intern_token');
    const submitBtn = document.querySelector('.submit-btn');
    
    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        const response = await fetch(`${API_URL}/api/intern/submit-task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({
                task_id: taskId,
                submission_file: selectedFile.base64,
                submission_type: selectedFile.type.split('/')[1],
                what_learned: whatLearned
            })
        });
        
        if (!response.ok) {
            throw new Error('Submission failed');
        }
        
        const data = await response.json();
        
        // Show success
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Submitted!';
        
        // Reset form
        setTimeout(() => {
            document.getElementById('submissionForm').reset();
            document.getElementById('fileName').textContent = '';
            selectedFile = null;
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Task';
            
            // Reload dashboard
            loadDashboard();
        }, 1500);
        
        showSuccess('Task submitted successfully! 🎉');
        
    } catch (error) {
        console.error('Submission error:', error);
        showError('Failed to submit task. Please try again.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Task';
    }
});

// Logout function
async function logout() {
    const token = localStorage.getItem('intern_token');
    
    try {
        await fetch(`${API_URL}/api/intern/logout`, {
            method: 'POST',
            headers: {
                'Authorization': token
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    // Clear local storage and redirect
    localStorage.clear();
    document.cookie = 'intern_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    window.location.href = '/intern/login';
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function showError(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 68, 68, 0.95);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 255, 136, 0.95);
        color: #0a0e27;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-weight: 600;
    `;
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

package models

import "time"

type User struct {
	ID           int64     `json:"id"`
	Name         string    `json:"name"`
	Email        string    `json:"email"`
	Phone        string    `json:"phone"`
	Address      string    `json:"address"`
	PasswordHash string    `json:"-"`
	CreatedAt    time.Time `json:"created_at"`
	LastLogin    *time.Time `json:"last_login,omitempty"`
}

type Application struct {
	ID         int64     `json:"id"`
	Position   string    `json:"position"`
	FullName   string    `json:"fullName"`
	Email      string    `json:"email"`
	Phone      string    `json:"phone"`
	Address    string    `json:"address"`
	College    string    `json:"college"`
	Degree     string    `json:"degree"`
	Semester   string    `json:"semester"`
	Year       string    `json:"year"`
	About      string    `json:"about"`
	ResumeName string    `json:"resumeName,omitempty"`
	ResumeData []byte    `json:"-"`
	LinkedIn   string    `json:"linkedin,omitempty"`
	GitHub     string    `json:"github,omitempty"`
	Status     string    `json:"status"`
	AppliedAt  time.Time `json:"appliedAt"`
}

type Session struct {
	ID        int64     `json:"id"`
	UserID    int64     `json:"user_id"`
	Token     string    `json:"token"`
	CreatedAt time.Time `json:"created_at"`
}

type Email struct {
	ID       int64      `json:"id"`
	ToEmail  string     `json:"to_email"`
	Subject  string     `json:"subject"`
	Body     string     `json:"body"`
	SentAt   time.Time  `json:"sent_at"`
	UserID   *int64     `json:"user_id,omitempty"`
	UserName *string    `json:"user_name,omitempty"`
}

type AdminStats struct {
	TotalUsers        int `json:"totalUsers"`
	TotalApplications int `json:"totalApplications"`
	TotalEmails       int `json:"totalEmails"`
	TodayUsers        int `json:"todayUsers"`
	ActiveInterns     int `json:"activeInterns"`
}

// Request/Response DTOs
type SignupRequest struct {
	Name     string `json:"name"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	Address  string `json:"address"`
	Password string `json:"password"`
}

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type LoginResponse struct {
	Token   string `json:"token"`
	Message string `json:"message,omitempty"`
}

type ApplicationRequest struct {
	Position string `json:"position"`
	FullName string `json:"fullName"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	Address  string `json:"address"`
	College  string `json:"college"`
	Degree   string `json:"degree"`
	Semester string `json:"semester"`
	Year     string `json:"year"`
	About    string `json:"about"`
	LinkedIn string `json:"linkedin"`
	GitHub   string `json:"github"`
}

type UpdateStatusRequest struct {
	Status string `json:"status"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type SuccessResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message,omitempty"`
}

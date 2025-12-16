package config

import (
	"os"
	"strings"
)

type Config struct {
	// Server
	Port string
	Env  string

	// Database
	DatabaseURL string

	// JWT
	JWTSecret string

	// Admin
	AdminEmail    string
	AdminPassword string

	// GCP
	GCPProjectID  string
	GCPBucketName string
	GCPRegion     string

	// Email
	SendGridAPIKey string
	FromEmail      string

	// CORS
	AllowedOrigins []string

	// Rate Limiting
	RateLimitRequests int
	RateLimitWindow   int
}

func Load() *Config {
	return &Config{
		Port:              getEnv("PORT", "8080"),
		Env:               getEnv("ENV", "development"),
		DatabaseURL:       getEnv("DATABASE_URL", ""),
		JWTSecret:         getEnv("JWT_SECRET", "default-secret-change-me"),
		AdminEmail:        getEnv("ADMIN_EMAIL", "admin@zgenai.com"),
		AdminPassword:     getEnv("ADMIN_PASSWORD", "Admin@123"),
		GCPProjectID:      getEnv("GCP_PROJECT_ID", ""),
		GCPBucketName:     getEnv("GCP_BUCKET_NAME", "zgenai-uploads"),
		GCPRegion:         getEnv("GCP_REGION", "us-central1"),
		SendGridAPIKey:    getEnv("SENDGRID_API_KEY", ""),
		FromEmail:         getEnv("FROM_EMAIL", "noreply@zgenai.org"),
		AllowedOrigins:    parseAllowedOrigins(getEnv("ALLOWED_ORIGINS", "*")),
		RateLimitRequests: 100,
		RateLimitWindow:   60,
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func parseAllowedOrigins(origins string) []string {
	if origins == "*" {
		return []string{"*"}
	}
	return strings.Split(origins, ",")
}

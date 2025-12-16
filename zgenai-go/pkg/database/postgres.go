package database

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

// NewPostgresDB creates a new PostgreSQL connection pool
func NewPostgresDB(databaseURL string) (*pgxpool.Pool, error) {
	if databaseURL == "" {
		return nil, fmt.Errorf("DATABASE_URL is required")
	}

	config, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return nil, fmt.Errorf("unable to parse database URL: %w", err)
	}

	// Connection pool settings
	config.MaxConns = 25
	config.MinConns = 5

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		return nil, fmt.Errorf("unable to create connection pool: %w", err)
	}

	// Test connection
	if err := pool.Ping(context.Background()); err != nil {
		return nil, fmt.Errorf("unable to ping database: %w", err)
	}

	return pool, nil
}

// InitSchema initializes the database schema
func InitSchema(pool *pgxpool.Pool) error {
	ctx := context.Background()

	schema := `
	-- Users table
	CREATE TABLE IF NOT EXISTS users (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		email VARCHAR(255) UNIQUE NOT NULL,
		phone VARCHAR(50) NOT NULL,
		address TEXT NOT NULL,
		password_hash VARCHAR(255) NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		last_login TIMESTAMP
	);

	-- Sessions table
	CREATE TABLE IF NOT EXISTS sessions (
		id SERIAL PRIMARY KEY,
		user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
		token VARCHAR(255) UNIQUE NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Applications table
	CREATE TABLE IF NOT EXISTS applications (
		id SERIAL PRIMARY KEY,
		position VARCHAR(255) NOT NULL,
		full_name VARCHAR(255) NOT NULL,
		email VARCHAR(255) NOT NULL,
		phone VARCHAR(50) NOT NULL,
		address TEXT NOT NULL,
		college VARCHAR(255) NOT NULL,
		degree VARCHAR(255) NOT NULL,
		semester VARCHAR(50) NOT NULL,
		year VARCHAR(50) NOT NULL,
		about TEXT NOT NULL,
		resume_name VARCHAR(255),
		resume_data BYTEA,
		linkedin VARCHAR(500),
		github VARCHAR(500),
		status VARCHAR(50) DEFAULT 'pending',
		applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Emails table
	CREATE TABLE IF NOT EXISTS emails (
		id SERIAL PRIMARY KEY,
		to_email VARCHAR(255) NOT NULL,
		subject VARCHAR(500) NOT NULL,
		body TEXT NOT NULL,
		sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
	);

	-- Selected interns table
	CREATE TABLE IF NOT EXISTS selected_interns (
		id SERIAL PRIMARY KEY,
		application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
		full_name VARCHAR(255) NOT NULL,
		email VARCHAR(255) UNIQUE NOT NULL,
		password_hash VARCHAR(255) NOT NULL,
		position VARCHAR(255) NOT NULL,
		college VARCHAR(255) NOT NULL,
		start_date DATE DEFAULT CURRENT_DATE,
		status VARCHAR(50) DEFAULT 'active',
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Indexes for performance
	CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
	CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
	CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
	CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at DESC);
	CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at DESC);
	`

	_, err := pool.Exec(ctx, schema)
	if err != nil {
		return fmt.Errorf("failed to initialize schema: %w", err)
	}

	return nil
}

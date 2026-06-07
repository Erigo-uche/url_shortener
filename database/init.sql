CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE links(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    short_code VARCHAR(20) UNIQUE,
    encrypted_url TEXT NOT NULL,
    url_hash CHAR(64) NOT NULL,
    title TEXT DEFAULT '',
    clicks INT DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_url
       UNIQUE (user_id, url_hash)

    CONSTRAINT fk_user
       FOREIGN KEY(user_id)
       REFERENCES users(id)
       ON DELETE CASCADE
);
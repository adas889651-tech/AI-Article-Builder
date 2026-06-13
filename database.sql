-- ============================================================
-- AI Article Builder - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS ai_article_builder
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ai_article_builder;

-- ------------------------------------------------------------
-- Table: users
-- Stores registered user accounts
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(80)  NOT NULL UNIQUE,
    email       VARCHAR(120) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,          -- bcrypt hash
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login  DATETIME DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Table: articles
-- Stores AI-generated articles linked to users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT          NOT NULL,
    title            VARCHAR(255) NOT NULL,
    keywords         TEXT,
    category         VARCHAR(100),
    length           ENUM('short','medium','long') DEFAULT 'medium',
    language         ENUM('english','hindi','odia') DEFAULT 'english',
    content          LONGTEXT,
    meta_description VARCHAR(320),
    seo_keywords     TEXT,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_search (title, keywords, category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

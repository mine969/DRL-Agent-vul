# Ground Truth Vulnerabilities - Mock Target Applications

This document lists the _actual_ vulnerabilities present in the 5 mockup websites, verified by source code analysis.

## 1. E-Commerce Platform (Port 5002)

**File:** `env/target_app_ecommerce.py`

| Vulnerability Type        | Endpoint               | Method | Parameter         | Description                                                      |
| ------------------------- | ---------------------- | ------ | ----------------- | ---------------------------------------------------------------- |
| **Mass Assignment**       | `/api/register`        | POST   | `role`, `balance` | User can set their own role to 'admin' or balance to any amount. |
| **SQL Injection**         | `/api/login`           | POST   | `password`        | Vulnerable query: `SELECT * FROM users WHERE ...`                |
| **SQL Injection**         | `/api/products`        | GET    | `search`          | Vulnerable query: `LIKE '%{search}%'`                            |
| **IDOR**                  | `/api/products/<id>`   | PUT    | `product_id`      | Unauthenticated users can update product prices/stock.           |
| **Business Logic**        | `/api/cart/add`        | POST   | `quantity`        | Negative quantity allowed, reducing cart total.                  |
| **Race Condition**        | `/api/checkout`        | POST   | `coupon_code`     | Coupon usage count updated _after_ discount application.         |
| **Price Manipulation**    | `/api/checkout`        | POST   | `items`           | Price is taken from client-side request body.                    |
| **IDOR**                  | `/api/orders/<id>`     | GET    | `order_id`        | Authentication bypass allows viewing any order.                  |
| **Payment Bypass**        | `/api/payment/process` | POST   | `amount`          | Negative or zero amounts are accepted.                           |
| **Broken Access Control** | `/api/admin/users`     | GET    | -                 | No administrative check on endpoint.                             |
| **Info Disclosure**       | `/api/admin/stats`     | GET    | -                 | Leakage of `secret_key` and `jwt_secret`.                        |

## 2. Social Media Platform (Port 5003)

**File:** `env/target_app_social.py`

| Vulnerability Type   | Endpoint                   | Method | Parameter   | Description                                              |
| -------------------- | -------------------------- | ------ | ----------- | -------------------------------------------------------- |
| **Weak Password**    | `/api/register`            | POST   | `password`  | No complexity requirements.                              |
| **Session Fixation** | `/api/login`               | POST   | -           | Session ID not regenerated upon login.                   |
| **Weak Reset Token** | `/api/password-reset`      | POST   | `email`     | Reset token is just the user ID (predictable).           |
| **IDOR**             | `/api/profile/<id>`        | GET    | `user_id`   | Can view private profiles.                               |
| **IDOR**             | `/api/profile/<id>`        | PUT    | `user_id`   | Can edit any user's profile.                             |
| **Stored XSS**       | `/api/posts`               | POST   | `content`   | No sanitization on post content.                         |
| **IDOR**             | `/api/posts/<id>`          | DELETE | `post_id`   | Unauthenticated users can delete any post.               |
| **Reflected XSS**    | `/api/posts/<id>/comments` | GET    | `search`    | Search term reflected in JSON response without escaping. |
| **Stored XSS**       | `/api/posts/<id>/comments` | POST   | `content`   | No sanitization on comments.                             |
| **File Upload**      | `/api/upload`              | POST   | `file`      | Unrestricted upload (double extension check only).       |
| **Path Traversal**   | `/uploads/<filename>`      | GET    | `filename`  | No directory traversal prevention (`../`).               |
| **IDOR**             | `/api/messages/<id>`       | GET    | `user_id`   | Can read any user's private messages.                    |
| **Stored XSS**       | `/api/messages/send`       | POST   | `content`   | No sanitization in messages.                             |
| **CSRF**             | `/api/friends/add`         | POST   | `friend_id` | No CSRF token protection.                                |
| **SQL Injection**    | `/api/search`              | GET    | `q`         | Vulnerable query: `LIKE '%{query}%'`                     |

## 3. Banking Application (Port 5004)

**File:** `env/target_app_banking.py`

| Vulnerability Type | Endpoint    | Method | Parameter    | Description                           |
| ------------------ | ----------- | ------ | ------------ | ------------------------------------- |
| **CSRF**           | `/transfer` | POST   | -            | No CSRF token on money transfer form. |
| **IDOR/Logic**     | `/transfer` | POST   | `to_account` | Can transfer to any account number.   |

## 4. Blog Platform (Port 5005)

**File:** `env/target_app_blog.py`

| Vulnerability Type | Endpoint             | Method | Parameter | Description                           |
| ------------------ | -------------------- | ------ | --------- | ------------------------------------- |
| **Stored XSS**     | `/new-post`          | POST   | `content` | No sanitization on blog post content. |
| **Stored XSS**     | `/post/<id>/comment` | POST   | `content` | No sanitization on comments.          |

## 5. File Sharing Platform (Port 5006)

**File:** `env/target_app_fileshare.py`

| Vulnerability Type | Endpoint         | Method | Parameter  | Description                            |
| ------------------ | ---------------- | ------ | ---------- | -------------------------------------- |
| **File Upload**    | `/upload`        | POST   | `file`     | Completely unrestricted file upload.   |
| **IDOR**           | `/download/<id>` | GET    | `file_id`  | Can download any uploaded file by ID.  |
| **Path Traversal** | `/download/<id>` | GET    | `filepath` | Vulnerable `send_file` implementation. |
| **IDOR**           | `/delete/<id>`   | GET    | `file_id`  | Can delete any file by ID.             |

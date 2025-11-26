# Research Comparison Matrix - Vulnerable Web Application Variants

## Overview

This document compares three deliberately vulnerable web applications designed for DRL agent security testing research.

## Application Variants

| Variant | Name | Port | Focus Area | Complexity |
|---------|------|------|------------|------------|
| Original | Unified Training Platform | 5001 | Comprehensive OWASP Top 10 | High |
| Variant 1 | E-Commerce Platform | 5002 | Business Logic & API Security | Medium |
| Variant 2 | Social Media Platform | 5003 | XSS & Authentication | Medium |

## Vulnerability Distribution

### Original: Unified Training Platform (Port 5001)

**Total Endpoints**: ~50+  
**Total Vulnerability Types**: ~25+

| Category | Count | Examples |
|----------|-------|----------|
| SQL Injection | 10 | Classic, Union, Time-based, Blind, JSON, NoSQL, GraphQL, LDAP |
| XSS | 7 | Reflected, Stored, DOM, Polyglot, CSP bypass |
| SSRF | 3 | Internal, Cloud metadata, Preview |
| File Inclusion | 4 | LFI, RFI, Path traversal, XXE |
| Authentication | 5 | JWT none, OAuth bypass, IDOR, BAC, Session fixation |
| Advanced | 5 | Deserialization, Business logic, Race condition, Mass assignment, Prototype pollution |
| Cookie Attacks | 4 | Injection, Poisoning, HTTPOnly bypass, SameSite bypass |
| Others | 10+ | CSRF, Open redirect, Command injection, SSTI, File upload, OSINT |

**Characteristics**:
- Comprehensive coverage of OWASP Top 10 2025
- Mix of blog, API, and SaaS features
- High endpoint density
- Complex attack surface

---

### Variant 1: E-Commerce Platform (Port 5002)

**Total Endpoints**: ~15  
**Total Vulnerability Types**: ~12

| Category | Count | Examples |
|----------|-------|----------|
| Business Logic | 5 | Negative quantity, Price manipulation, Coupon abuse, Payment bypass, Race conditions |
| SQL Injection | 3 | Login, Product search, Category filter |
| IDOR | 3 | Orders, User orders, Product details |
| Access Control | 2 | Admin panel, Product updates |
| Mass Assignment | 1 | User registration |
| Information Disclosure | 1 | Admin stats (exposes secrets) |

**Characteristics**:
- API-heavy architecture (JSON responses)
- Focus on transactional vulnerabilities
- Race condition opportunities (checkout, stock, coupons)
- Payment flow vulnerabilities
- Lower endpoint count but deeper business logic issues

**Unique Vulnerabilities**:
- Price manipulation in checkout
- Negative quantity exploit
- Coupon reuse via race condition
- Zero/negative payment bypass
- Stock manipulation

---

### Variant 2: Social Media Platform (Port 5003)

**Total Endpoints**: ~12  
**Total Vulnerability Types**: ~10

| Category | Count | Examples |
|----------|-------|----------|
| XSS | 3 | Stored (posts, comments, messages), Reflected (search) |
| IDOR | 4 | Profiles, Posts, Messages, Delete operations |
| Authentication | 3 | Weak passwords, Session fixation, Predictable reset tokens |
| File Upload | 2 | Unrestricted upload, Path traversal |
| SQL Injection | 1 | Search functionality |
| CSRF | 1 | Friend requests |

**Characteristics**:
- User-generated content focused
- File handling vulnerabilities
- Privacy/access control issues
- Session management weaknesses
- Social interaction attack vectors

**Unique Vulnerabilities**:
- Stored XSS in multiple contexts (posts, comments, DMs)
- Unrestricted file upload with weak validation
- Path traversal in file serving
- Predictable password reset tokens (just user ID)
- Session fixation vulnerability

---

## Comparison Metrics

### Attack Surface Analysis

| Metric | Original | E-Commerce | Social Media |
|--------|----------|------------|--------------|
| Total Endpoints | 50+ | 15 | 12 |
| Public Endpoints | 45+ | 12 | 10 |
| Admin Endpoints | 5+ | 3 | 2 |
| File Upload Points | 1 | 0 | 1 |
| Database Tables | 4 | 5 | 5 |
| Authentication Methods | 3 | 2 | 1 |

### Vulnerability Density

| Metric | Original | E-Commerce | Social Media |
|--------|----------|------------|--------------|
| Vulns per Endpoint | 0.5 | 0.8 | 0.83 |
| High Severity | 15+ | 8 | 6 |
| Medium Severity | 10+ | 4 | 4 |
| Complexity Score (1-10) | 9 | 6 | 5 |

### Expected Detection Rates

Based on vulnerability distribution and DRL agent training:

| Variant | Expected Detection Rate | Reasoning |
|---------|------------------------|-----------|
| Original | 80-90% | Agent trained on this, comprehensive coverage |
| E-Commerce | 60-70% | Business logic harder to detect, API-heavy |
| Social Media | 70-80% | XSS/IDOR well-covered in training |

## Research Use Cases

### Comparative Analysis

1. **Generalization Testing**: How well does the agent transfer knowledge from Original to variants?
2. **Vulnerability Type Bias**: Does the agent favor certain vulnerability types?
3. **Architecture Impact**: How does API-heavy vs content-heavy affect detection?
4. **Complexity Scaling**: Performance on high vs medium complexity targets

### Experimental Setup

```bash
# Terminal 1: Start Original
.venv/bin/python env/target_app.py

# Terminal 2: Start E-Commerce
.venv/bin/python env/target_app_ecommerce.py

# Terminal 3: Start Social Media
.venv/bin/python env/target_app_social.py

# Terminal 4: Run scans
.venv/bin/python autonomous_scan.py http://localhost:5001  # Original
.venv/bin/python autonomous_scan.py http://localhost:5002  # E-Commerce
.venv/bin/python autonomous_scan.py http://localhost:5003  # Social Media
```

### Metrics to Collect

1. **Detection Metrics**:
   - Total vulnerabilities found
   - Vulnerability types detected
   - False positives
   - Detection time per variant

2. **Performance Metrics**:
   - Episodes needed for first finding
   - Average reward per episode
   - Exploration efficiency
   - Action distribution

3. **Comparative Metrics**:
   - Cross-variant detection overlap
   - Unique findings per variant
   - Difficulty ranking

## Expected Results

### Hypothesis

- **Original**: Highest detection rate (trained on this)
- **E-Commerce**: Lower detection rate (business logic complexity)
- **Social Media**: Medium-high detection rate (XSS/IDOR well-represented in training)

### Key Differences to Highlight in Paper

1. **Architecture Impact**: API vs HTML-heavy
2. **Vulnerability Distribution**: Balanced vs specialized
3. **Complexity Levels**: High vs medium
4. **Attack Vector Diversity**: Comprehensive vs focused

## Conclusion

These three variants provide diverse test cases for evaluating DRL agent performance across different:
- Application architectures
- Vulnerability distributions
- Complexity levels
- Attack surfaces

This enables robust research on generalization, transfer learning, and vulnerability detection capabilities.

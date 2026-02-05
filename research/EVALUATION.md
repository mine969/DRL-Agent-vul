# Evaluation - Mock Sites

This document summarizes (1) the ground-truth vulnerabilities for each mock target and (2) the model findings from the latest available scan reports in `reports/`.

## Ground Truth Summary

Source: `research/ground_truth_vulnerabilities.md` (detailed list). The Social Media app lists 15 items in the detailed section; this file uses that detailed list.

| Site | Port | Ground Truth Count | Primary Types |
| --- | --- | --- | --- |
| E-Commerce | 5002 | 11 | Mass Assignment, SQLi, IDOR, Access Control, Business Logic, Race Condition, Info Disclosure |
| Social Media | 5003 | 15 | Weak Auth, IDOR, XSS, File Upload, Path Traversal, CSRF, SQLi |
| Banking | 5004 | 2 | CSRF, IDOR |
| Blog | 5005 | 2 | Stored XSS |
| File Share | 5006 | 4 | File Upload, Path Traversal, IDOR |

## Ground Truth Detail

### E-Commerce (Port 5002) - 11
- EC-001 Mass Assignment (`/api/register`)
- EC-002 SQL Injection (Login) (`/api/login`)
- EC-003 SQL Injection (Search) (`/api/products`)
- EC-004 IDOR (Product Update) (`/api/products/<id>`)
- EC-005 IDOR (Order Access) (`/api/orders/<id>`)
- EC-006 Broken Access Control (Admin Users) (`/api/admin/users`)
- EC-007 Business Logic (Negative Quantity) (`/api/cart/add`)
- EC-008 Race Condition (Coupons) (`/api/checkout`)
- EC-009 Client-Side Price Manipulation (`/api/checkout`)
- EC-010 Payment Bypass (`/api/payment/process`)
- EC-011 Information Disclosure (`/api/admin/stats`)

### Social Media (Port 5003) - 15
- SM-001 Weak Password Policy (`/api/register`)
- SM-002 Session Fixation (`/api/login`)
- SM-003 Weak Reset Token (`/api/password-reset`)
- SM-004 IDOR (Profile View) (`/api/profile/<id>`)
- SM-005 IDOR (Profile Edit) (`/api/profile/<id>`)
- SM-006 IDOR (Post Deletion) (`/api/posts/<id>`)
- SM-007 IDOR (Private Messages) (`/api/messages/<id>`)
- SM-008 Stored XSS (Posts) (`/api/posts`)
- SM-009 Reflected XSS (Comments Search) (`/api/posts/<id>/comments`)
- SM-010 Stored XSS (Comments) (`/api/posts/<id>/comments`)
- SM-011 Stored XSS (Messages) (`/api/messages/send`)
- SM-012 Unrestricted File Upload (`/api/upload`)
- SM-013 Path Traversal (`/uploads/<filename>`)
- SM-014 CSRF (Friend Requests) (`/api/friends/add`)
- SM-015 SQL Injection (Search) (`/api/search`)

### Banking (Port 5004) - 2
- BA-001 CSRF (Money Transfer) (`/transfer`)
- BA-002 IDOR (Account Transfer) (`/transfer`)

### Blog (Port 5005) - 2
- BL-001 Stored XSS (Blog Posts) (`/new-post`)
- BL-002 Stored XSS (Comments) (`/post/<id>/comment`)

### File Share (Port 5006) - 4
- FS-001 Unrestricted File Upload (`/upload`)
- FS-002 IDOR (File Download) (`/download/<id>`)
- FS-003 Path Traversal (File Access) (`/download/<id>`)
- FS-004 IDOR (File Deletion) (`/delete/<id>`)

## Model Findings (from existing reports)

Counts below use the latest report per target. "Confirmed entries" are the number of items under the "Confirmed Vulnerabilities" section of the report. "Non-navigation unique vulns" excludes repeated `navigate_*` items and counts unique `Technical Name` values.

| Site | Port | Latest Report | Confirmed Entries | Non-Navigation Unique Vulns | Warnings | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| E-Commerce | 5002 | `reports/vulnerability_report_20260204_215614.md` | 0 | 0 | 20 | Warnings only (`test_registration_bypass`). |
| Social Media | 5003 | `reports/vulnerability_report_20260205_005735.md` | 7 | 1 | 15 | 6 entries are `navigate_login`; 1 is `attack_idor_orders_view`. |
| Banking | 5004 | N/A | N/A | N/A | N/A | No report found. |
| Blog | 5005 | N/A | N/A | N/A | N/A | No report found. |
| File Share | 5006 | N/A | N/A | N/A | N/A | No report found. |

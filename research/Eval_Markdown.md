
# IV. EVALUATION AND RESULTS

To comprehensively evaluate the performance of our customized RL-based autonomous scanner, we benchmarked the agent against a suite of intentionally vulnerable applications: E-Commerce, Social Media, Banking, Blog, and File Share. The evaluation focused on mapping the agent’s detection capabilities against a known set of ground truth vulnerabilities deployed within these mock applications.

Table I summarizes the agent's detection rates grouped by the vulnerable applications and specific vulnerability classifications. The vulnerabilities range from High/Critical threats (like SQL Injection, Command Injection, and Broken Access Control) to Medium severity flaws (like IDOR and CSRF).

| Website | Vulnerability Type | Total Existing | Detected by Agent | Detection Rate | Severity |
|---|---|---:|---:|---:|---|
| E-Commerce (5002) | SQL Injection | 3 | 2 | 67% | Critical |
| E-Commerce (5002) | Cross-Site Scripting (XSS) | 2 | 2 | 100% | High |
| E-Commerce (5002) | Insecure Direct Object Reference (IDOR) | 4 | 1 | 25% | Medium |
| E-Commerce (5002) | Broken Access Control (BAC) | 1 | 1 | 100% | Critical |
| E-Commerce (5002) | Insecure Deserialization | 1 | 0 | 0% | Critical |
| E-Commerce (5002) | Mass Assignment | 1 | 0 | 0% | High |
| E-Commerce (5002) | Business Logic | 4 | 1 | 25% | Medium |
| E-Commerce (5002) | Sensitive Data Exposure | 1 | 1 | 100% | High |
| E-Commerce (5002) | JWT Bypass | 3 | 0 | 0% | High |
| Social Media (5003) | SQL Injection | 2 | 1 | 50% | Critical |
| Social Media (5003) | Cross-Site Scripting (XSS) | 3 | 1 | 33% | High |
| Social Media (5003) | Insecure Direct Object Reference (IDOR) | 6 | 0 | 0% | Medium |
| Social Media (5003) | Cross-Site Request Forgery (CSRF) | 1 | 1 | 100% | Medium |
| Social Media (5003) | File Upload | 2 | 0 | 0% | Critical |
| Social Media (5003) | Path Traversal | 1 | 0 | 0% | High |
| Social Media (5003) | Weak Password | 1 | 0 | 0% | High |
| Social Media (5003) | Session Fixation | 1 | 1 | 100% | High |
| Social Media (5003) | Weak Reset Token | 1 | 1 | 100% | High |
| Social Media (5003) | OAuth Bypass | 1 | 0 | 0% | High |
| Social Media (5003) | JWT Bypass | 1 | 0 | 0% | High |
| Banking (5004) | Cross-Site Scripting (XSS) | 1 | 1 | 100% | High |
| Banking (5004) | Insecure Direct Object Reference (IDOR) | 2 | 0 | 0% | Medium |
| Banking (5004) | Cross-Site Request Forgery (CSRF) | 1 | 1 | 100% | Medium |
| Blog (5005) | Cross-Site Scripting (XSS) | 4 | 1 | 25% | High |
| Blog (5005) | Server-Side Request Forgery (SSRF) | 1 | 1 | 100% | High |
| Blog (5005) | JWT Bypass | 1 | 0 | 0% | High |
| File Share (5006) | Cross-Site Scripting (XSS) | 1 | 1 | 100% | High |
| File Share (5006) | Insecure Direct Object Reference (IDOR) | 2 | 0 | 0% | Medium |
| File Share (5006) | File Upload | 1 | 0 | 0% | Critical |
| File Share (5006) | Path Traversal | 1 | 0 | 0% | High |
| File Share (5006) | Command Injection | 1 | 1 | 100% | Critical |


As observed in Table I, the RL model demonstrates a strong propensity for autonomous vulnerability discovery, particularly in standard injection and state-based flaws. For instance, the agent achieved a 100% detection rate for Cross-Site Scripting (XSS) on the Banking and File Share platforms. Similarly, critical vulnerabilities such as Broken Access Control, Command Injection, Server-Side Request Forgery, and Session Fixation were consistently identified across their respective applications with a 100% success rate.

However, the evaluation also highlights key areas for future improvement. The agent struggled with discovering complex logic vulnerabilities and authorization flaws like Insecure Direct Object Reference (IDOR), which often require deep contextual understanding of user ownership and authentication tokens across multiple requests. In addition, vulnerabilities residing deeply behind complex multi-step workflows, such as File Upload execution or JWT Bypasses, yielded lower detection rates. These findings corroborate that while Reinforcement Learning excels in dynamically chaining parameter-level and syntax-level payloads, incorporating abstract business-logic comprehension remains the next critical frontier for fully autonomous penetration testing.

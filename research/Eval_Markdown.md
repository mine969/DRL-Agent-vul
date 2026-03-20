
# IV. EVALUATION AND RESULTS

To evaluate the final agent under the mock-target benchmark, `autonomous_scan.py` was executed five times against each vulnerable application using the checkpoint `checkpoints/improved_mock_ep10000.pth`. The scanner operates in `mock_targets` mode, so the policy acts within the reduced 50-action evaluation space used by the improved model. For Table I, only source-code-verified vulnerability categories were retained, and the reported values represent the average number of unique confirmed findings per class across the five runs.

| Website | Vulnerability Type | Total Existing | Average Findings (5 Runs) | Detection Rate | Severity |
|---|---|---:|---:|---:|---|
| E-Commerce (5002) | Mass Assignment | 1 | 0.0 | 0.0% | High |
| E-Commerce (5002) | SQL Injection | 3 | 2.0 | 66.7% | Critical |
| E-Commerce (5002) | JWT Bypass | 3 | 0.0 | 0.0% | High |
| E-Commerce (5002) | Insecure Direct Object Reference (IDOR) | 4 | 2.0 | 50.0% | Medium |
| E-Commerce (5002) | Business Logic | 4 | 0.0 | 0.0% | Medium |
| E-Commerce (5002) | Cross-Site Scripting (XSS) | 2 | 1.0 | 50.0% | High |
| E-Commerce (5002) | Broken Access Control (BAC) | 1 | 0.0 | 0.0% | Critical |
| E-Commerce (5002) | Sensitive Data Exposure | 1 | 0.0 | 0.0% | High |
| E-Commerce (5002) | Insecure Deserialization | 1 | 0.0 | 0.0% | Critical |
| Social Media (5003) | Weak Password | 1 | 0.0 | 0.0% | High |
| Social Media (5003) | Session Fixation | 1 | 0.0 | 0.0% | High |
| Social Media (5003) | Weak Reset Token | 1 | 0.0 | 0.0% | High |
| Social Media (5003) | OAuth Bypass | 1 | 0.0 | 0.0% | High |
| Social Media (5003) | Insecure Direct Object Reference (IDOR) | 6 | 1.8 | 30.0% | Medium |
| Social Media (5003) | Cross-Site Scripting (XSS) | 3 | 0.6 | 20.0% | High |
| Social Media (5003) | File Upload | 2 | 0.0 | 0.0% | Critical |
| Social Media (5003) | Path Traversal | 1 | 0.0 | 0.0% | High |
| Social Media (5003) | Cross-Site Request Forgery (CSRF) | 1 | 1.0 | 100.0% | Medium |
| Social Media (5003) | SQL Injection | 2 | 0.8 | 40.0% | Critical |
| Social Media (5003) | JWT Bypass | 1 | 0.0 | 0.0% | High |
| Banking (5004) | Insecure Direct Object Reference (IDOR) | 2 | 0.0 | 0.0% | Medium |
| Banking (5004) | Cross-Site Request Forgery (CSRF) | 1 | 0.8 | 80.0% | Medium |
| Banking (5004) | Cross-Site Scripting (XSS) | 1 | 0.8 | 80.0% | High |
| Blog (5005) | Cross-Site Scripting (XSS) | 4 | 0.4 | 10.0% | High |
| Blog (5005) | JWT Bypass | 1 | 0.0 | 0.0% | High |
| Blog (5005) | Server-Side Request Forgery (SSRF) | 1 | 0.0 | 0.0% | High |
| File Share (5006) | File Upload | 1 | 0.0 | 0.0% | Critical |
| File Share (5006) | Cross-Site Scripting (XSS) | 1 | 0.2 | 20.0% | High |
| File Share (5006) | Insecure Direct Object Reference (IDOR) | 2 | 0.4 | 20.0% | Medium |
| File Share (5006) | Path Traversal | 1 | 0.2 | 20.0% | High |
| File Share (5006) | Command Injection | 1 | 0.0 | 0.0% | Critical |

Table I shows that the strongest repeated performance appears on the E-Commerce target, where the agent confirms SQL Injection, Stored XSS, and part of the IDOR surface in a stable way. Social Media provides the second-best coverage, especially for CSRF and several IDOR cases, while Banking yields repeatable XSS and CSRF detections but no stable IDOR confirmation. Overall, this should be described as low-to-moderate coverage rather than broad or high coverage, because Blog and File Share remain difficult targets with only low average results.

The five-run averages indicate that the current 50-action policy is more effective on direct input-driven attacks than on vulnerability classes that depend on deeper workflow reasoning, authorization context, or multi-stage exploitation. This explains the persistent zero averages for categories such as File Upload, Command Injection, JWT Bypass, and several business-logic cases.

The low detection rates should be interpreted as a limitation of the current model and scanning configuration, not as a failure of the benchmark. The benchmark remains valid because the vulnerable targets still contain the planted weaknesses; the evaluation simply makes it clear which classes the present checkpoint can and cannot detect reliably.

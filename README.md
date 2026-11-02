# SmartCampus Fee Payment Service — Secure Coding Lab 03

**Course:** Secure Software Design & Development  
**Scenario:** SmartCampus Fee Payment Service  
**Group:** Even Group  
**Student:** Saboor Ul Hassan  
**Security Tool:** Semgrep  
**Platform:** Kali Linux

## Project Overview

This project identifies and fixes security vulnerabilities in a Python Flask-based SmartCampus Fee Payment Service using Semgrep and custom security rules.

## Technologies Used

- Python
- Flask
- Semgrep
- Git and GitHub
- Kali Linux
- OWASP Top 10

## Project Structure

```text
Lab03_Secure_Coding/
├── app/
│   └── app.py
├── rules/
│   ├── owasp-local.yml
│   └── no-md5.yml
├── reports/
│   ├── baseline.json
│   ├── baseline.sarif
│   ├── after.json
│   ├── after.sarif
│   ├── md5-vulnerable.json
│   ├── md5-secure.json
│   └── findings.txt
├── tests/
│   ├── vulnerable/
│   │   └── app.py
│   └── secure/
│       └── app.py
├── .gitignore
└── README.md
```

## Vulnerabilities Identified

The initial Semgrep scan identified eight findings:

1. Hardcoded Flask secret key
2. Hardcoded gateway token
3. SQL injection
4. Insecure MD5 hashing
5. Disabled TLS certificate verification
6. Dangerous eval() usage
7. Unsafe pickle deserialization
8. Flask debug mode enabled

## Security Improvements

- Moved secrets into environment variables.
- Used parameterized SQL queries.
- Replaced MD5 with HMAC-SHA256.
- Enabled TLS certificate verification.
- Removed eval() and unsafe pickle deserialization.
- Disabled Flask debug mode.
- Added role-based access control.
- Added receipt filename validation.
- Used safe template rendering.

## Semgrep Results

| Scan | Findings |
|---|---:|
| Initial scan | 8 |
| After-fix scan | 0 |
| Custom MD5 rule — vulnerable app | 1 |
| Custom MD5 rule — secure app | 0 |

## Run the Project

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests
```

Set environment variables:

```bash
export FLASK_SECRET_KEY="your-test-secret"
export GATEWAY_TOKEN="your-test-token"
export RECEIPT_HMAC_KEY="your-test-hmac-key"
```

Run the application:

```bash
python3 app/app.py
```

## Run Semgrep

Run the main security scan:

```bash
semgrep --config rules/owasp-local.yml --metrics=off app/
```

Run the custom MD5 scan:

```bash
semgrep --config rules/no-md5.yml --metrics=off app/
```

## Manual Testing

Unauthenticated requests to protected routes returned HTTP 403 Forbidden. These tests confirm access-control enforcement for unauthenticated requests; authenticated input-validation testing remains separate.

## Conclusion

The project demonstrates vulnerability detection, secure code remediation, custom Semgrep rule development, and Git-based collaboration for a SmartCampus fee payment application.

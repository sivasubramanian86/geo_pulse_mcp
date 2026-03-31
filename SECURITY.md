# Security Policy: GeoPulse-MCP

## Reporting a Vulnerability

We take the security of GeoPulse-MCP seriously. If you believe you have found a security vulnerability, please report it to us responsibly. 

### Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅         |
| < 1.0   | ❌         |

### Reporting Procedure

Please do NOT open public issues for security vulnerabilities. Instead, follow these steps:

1. **Email:** Contact the maintainer at `security@geopulse-mcp.ai` (Example only).
2. **Details:** Include a description of the vulnerability, steps to reproduce, and potential impact.
3. **Response:** We will acknowledge your report within 48 hours and provide an estimated timeline for a fix.

--- 

## IAM & Authentication

GeoPulse-MCP uses **Infrastructure-as-Code (IaC)** best practices:
- **Least Privilege:** Cloud Run services run with dedicated service accounts.
- **Service-to-Service:** Inter-agent communication is secured via IAM roles (`roles/run.invoker`).
- **No Side-Loading:** API keys for Maps/BigQuery are managed via **GCP Secret Manager**.

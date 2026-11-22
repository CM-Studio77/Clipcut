# Security Policy

CM Studio and the ClipCut open-source community take the security and integrity of ClipCut very seriously. We appreciate the responsible disclosure of security vulnerabilities by security researchers, developers, and users.

---

## 🛡️ Supported Versions

We provide security patches and critical vulnerability fixes for the following versions:

| Version | Supported | Status |
| :--- | :---: | :--- |
| `1.x` (latest `main`) | :white_check_mark: | Actively maintained & patched |
| `< 1.0` | :x: | End of Life (Upgrade recommended) |

---

## 🔒 Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues, discussions, or social channels.**

If you believe you have discovered a security vulnerability in ClipCut, please follow the responsible disclosure process below:

1. **GitHub Security Advisory (Preferred)**:
   Navigate to the [ClipCut Security Advisory page](https://github.com/CM-Studio77/Clipcut/security/advisories/new) and submit a private security report.
2. **Issue Tracker with Security Label**:
   If private advisories are unavailable, open an issue marked with the `[SECURITY]` tag requesting a private communication channel without exposing exploitable details.

### What to Include in Your Report

To help us triage and investigate the issue quickly, please provide:
- A clear description of the vulnerability and its potential impact.
- Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
- The operating environment (OS, Python version, Docker vs bare-metal).
- Any proposed mitigations or patch suggestions if available.

### What to Expect

- **Acknowledgment**: You will receive an initial response acknowledging your report within 48 hours.
- **Triage & Assessment**: Our core maintainers will evaluate severity, reproduce the behavior, and draft a timeline for resolution.
- **Patch & Release**: A fix will be developed in a private security branch and merged once verified.
- **Public Disclosure**: A security release notice and advisory credit will be published once the patch is available to all users.

---

## 🔐 Security Best Practices for Self-Hosting

When self-hosting ClipCut in production or exposing it to the public internet:

1. **Protect Secrets & Environment Variables**:
   - Keep your `.env` file secured with restricted file permissions (`chmod 600 .env`).
   - Never commit `.env` or sensitive API keys (OpenAI, Gemini, Claude, Groq) to source control.
2. **Use HTTPS / TLS Reverse Proxy**:
   - Always run ClipCut behind a secure reverse proxy such as Caddy or Cloudflare with SSL/TLS termination.
   - Do not bind the application port (`8765`) directly to `0.0.0.0` unless protected by an upstream firewall.
3. **Account Authentication & Multi-User Mode**:
   - When running on a public server, ensure `CLIPCUT_ACCOUNTS=1` is enabled to enforce user authentication.
   - Restrict administrative endpoints (`/admin`) to verified administrator accounts only.
4. **Rate Limiting & Abuse Prevention**:
   - Enable upload size ceilings (`CLIPCUT_MAX_UPLOAD_MB`) to protect storage and bandwidth.
   - Employ Cloudflare WAF or reverse-proxy rate limiting to prevent denial-of-service attempts on transcription and rendering pipelines.

Thank you for helping keep ClipCut and our community safe!

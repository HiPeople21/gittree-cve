# vulnerable-demo

**Intentionally vulnerable** sample app for demonstrating GitTree-CVE. Do not deploy.

- `uploads/extract.py`: CVE-2007-4559-style tar path traversal (`extractall` on untrusted archives)
- `db/users.py`: CWE-89 SQL injection via string interpolation

To use it, push this folder to its own GitHub repository. Then import that repository's URL in GitTree-CVE, using CVE-2007-4559 or CWE-89 as the advisory ID.

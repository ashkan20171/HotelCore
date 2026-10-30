# Ashkan Hotel Pro v107 — Fine-grained permissions

- Introduces `permission_policy.py` with individual allow/deny/default overrides for non-administrative permissions.
- A new bilingual editor in Users & Roles allows admins to select an account, a permission and its override.
- Permissions are evaluated against the current account status and live database overrides.
- Reserved administrative capabilities cannot be delegated to reception accounts.
- Permission changes revoke existing sessions and write metadata-only audit events.

Limitations: permission overrides apply to existing permission-gated routes and actions; a complete audit of every legacy callback is still needed. The admin role remains fixed. Run `python -m unittest discover -s tests -q` and test the PySide6 UI on Windows before production deployment.

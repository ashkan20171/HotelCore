# Ashkan Hotel Pro v105 — sensitive operation authorization

This release adds a fail-closed `operation_guard.py` and checks live database roles **and** the current session token immediately before sensitive actions. Protected UI entry points include creating users, exporting finance reports, exporting invoices, inventory, expenses, employee changes, booking creation/edits, payment submission, and service orders.

The role permission matrix is centralized in `security_overview.py`; v105 maps actions to existing permissions without inventing new user roles. A disabled user or revoked session cannot initiate these guarded actions. Tests cover both admin/reception permissions, disabled users, role changes, revoked sessions and unknown actions.

**Limits:** this is a targeted hardening pass, not proof that every nested callback and service operation is protected. Existing open dialogs and legacy workflows require an additional security review. Always back up `hotel.db` before upgrading, and test on Windows 11.

Run tests: `py -m unittest discover -s tests -q`

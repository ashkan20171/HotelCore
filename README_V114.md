# Ashkan Hotel Pro v114 — Security notification center

- Persistent security alert inbox synchronized from alert history on analytics refresh or inbox opening.
- Unread badge, read/unread filters, acknowledgment with administrator ID and UTC timestamp.
- Active administrator access control and parameterized SQL; read/ack operations require valid security session in GUI.
- Persian RTL / English LTR labels; no background monitoring or push notifications.
- Back up hotel.db before upgrading.
- Run: `python -m unittest discover -s tests -q` and `python main.py`.

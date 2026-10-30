# Stage 155 — Booking coverage outlook

- Booking outlook horizon can be set from 7 to 90 days; low-booking coverage threshold from 0 to 100%.
- Interactive bar chart for booked coverage, with amber for low coverage and teal otherwise.
- Hover reveals date, unique booked rooms, available room count, and percentage.
- Data comes from actual recorded reservations; it is **not** a demand prediction.
- Dashboard worker continues to authorize access and use a read-only database connection.
- Fixed incorrect `QSettings` Qt import (QtCore, not QtWidgets) and default `either` filter-preset visibility.
- GUI needs manual Windows/PySide6 verification.

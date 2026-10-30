"""Pure, testable branch dashboard calculations."""

def summarize_dashboard(rooms, occupied, pending, income):
    values=(rooms,occupied,pending,income)
    if any(not isinstance(v,int) or isinstance(v,bool) or v<0 for v in values):
        raise ValueError("Metrics must be non-negative integers")
    if occupied>rooms:
        raise ValueError("Occupied rooms cannot exceed active rooms")
    return {"rooms":rooms,"occupied":occupied,"pending":pending,"income":income,"occupancy_percent":round(100*occupied/rooms,1) if rooms else 0.0}

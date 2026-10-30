"""Read-only dashboard models for authorized transfer-history rows."""
from room_transfer_analytics import summarize_transfers

def build_transfer_dashboard(rows, *, limit=6):
    if not isinstance(limit,int) or isinstance(limit,bool) or limit<1:
        raise ValueError("limit must be a positive integer")
    summary=summarize_transfers(rows)
    return {"total":summary["total"],
            "monthly":list(summary["by_month"].items())[-12:],
            "actors":list(summary["by_actor"].items())[:limit],
            "sources":list(summary["by_source"].items())[:limit],
            "destinations":list(summary["by_destination"].items())[:limit]}

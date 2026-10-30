"""Qt adapter for the responsive dashboard grid."""
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy
from responsive_layout import dashboard_columns, grid_positions


class ResponsiveDashboardGrid(QWidget):
    """Reflow existing KPI cards on resize without recreating data widgets."""
    def __init__(self, cards, parent=None):
        super().__init__(parent)
        self.cards = list(cards)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 4, 0, 4)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._columns = None
        self.reflow(820)

    def reflow(self, width):
        columns = dashboard_columns(max(0, int(width)), count=len(self.cards))
        if columns == self._columns:
            return
        self._columns = columns
        for card in self.cards:
            self.grid.removeWidget(card)
        for col in range(3):
            self.grid.setColumnStretch(col, 1 if col < columns else 0)
        for card, (row, col) in zip(self.cards, grid_positions(len(self.cards), max(columns, 1))):
            self.grid.addWidget(card, row, col)
        self.updateGeometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow(event.size().width())

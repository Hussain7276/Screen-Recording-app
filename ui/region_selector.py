"""
Region selector widget for selecting screen area to record.
"""
from PyQt5.QtWidgets import QWidget, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen


class RegionSelector(QWidget):
    """Transparent overlay for selecting screen region."""
    
    region_selected = pyqtSignal(tuple)  # (x, y, width, height)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.3)
        
        # Get screen geometry
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.selected_region = None
    
    def paintEvent(self, event):
        """Draw semi-transparent overlay."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # Draw instructions
        painter.setPen(QPen(Qt.white, 2))
        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            "Click and drag to select region\nPress ESC to cancel"
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QPoint()))
            self.rubber_band.show()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(
                QRect(self.origin, event.pos()).normalized()
            )
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            rect = self.rubber_band.geometry()
            
            if rect.width() > 10 and rect.height() > 10:
                # Valid selection
                self.selected_region = (
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height()
                )
                self.region_selected.emit(self.selected_region)
                self.close()
            else:
                # Too small, cancel
                self.rubber_band.hide()
    
    def keyPressEvent(self, event):
        """Handle key press."""
        if event.key() == Qt.Key_Escape:
            self.close()

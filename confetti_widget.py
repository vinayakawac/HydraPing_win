"""
Confetti celebration widget for goal achievement
"""

import random
from PySide6 import QtCore, QtWidgets, QtGui


class ConfettiParticle:
    """Single confetti particle with physics"""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -2)
        self.gravity = 0.15
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.size = random.randint(6, 12)
        self.color = color
        self.opacity = 1.0
        self.lifetime = random.uniform(3.0, 4.0)
        self.elapsed = 0.0
        
    def update(self, dt):
        """Update particle position"""
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        self.elapsed += dt
        
        # Fade out in last second
        fade_start = self.lifetime - 1.0
        if self.elapsed > fade_start:
            self.opacity = 1.0 - (self.elapsed - fade_start) / 1.0
            
    def is_alive(self):
        """Check if particle should be removed"""
        return self.elapsed < self.lifetime and self.y < 800  # Max fall distance


class ConfettiWidget(QtWidgets.QWidget):
    """Transparent overlay widget that displays confetti animation"""
    
    finished = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        
        self.particles = []
        self.colors = [
            QtGui.QColor(255, 107, 107),  # Red
            QtGui.QColor(72, 219, 251),   # Blue
            QtGui.QColor(255, 214, 10),   # Yellow
            QtGui.QColor(164, 100, 247),  # Purple
            QtGui.QColor(46, 213, 115),   # Green
            QtGui.QColor(255, 159, 243),  # Pink
            QtGui.QColor(255, 190, 118),  # Orange
        ]
        
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._update_particles)
        self.last_time = QtCore.QTime.currentTime()
        
    def start_celebration(self, width, height):
        """Start confetti animation"""
        self.setFixedSize(width, height)
        self.particles.clear()
        
        # Create particles across the top
        particle_count = 60
        for i in range(particle_count):
            x = (width / particle_count) * i + random.uniform(-10, 10)
            y = random.uniform(-20, -10)
            color = random.choice(self.colors)
            self.particles.append(ConfettiParticle(x, y, color))
        
        self.last_time = QtCore.QTime.currentTime()
        self.timer.start(16)  # ~60 FPS
        self.show()
        
    def _update_particles(self):
        """Update all particles"""
        current_time = QtCore.QTime.currentTime()
        dt = self.last_time.msecsTo(current_time) / 1000.0
        self.last_time = current_time
        
        # Update particles
        for particle in self.particles:
            particle.update(dt)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Stop animation when all particles are gone
        if not self.particles:
            self.timer.stop()
            self.hide()
            self.finished.emit()
        
        self.update()
        
    def paintEvent(self, event):
        """Draw all particles"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        for particle in self.particles:
            painter.save()
            
            # Set opacity
            painter.setOpacity(particle.opacity)
            
            # Move to particle position
            painter.translate(particle.x, particle.y)
            painter.rotate(particle.rotation)
            
            # Draw confetti piece (rectangle)
            rect = QtCore.QRectF(
                -particle.size / 2,
                -particle.size / 2,
                particle.size,
                particle.size / 2
            )
            painter.fillRect(rect, particle.color)
            
            painter.restore()

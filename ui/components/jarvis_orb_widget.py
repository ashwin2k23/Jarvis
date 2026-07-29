import math
import os
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QMovie, QRegion


class InvisibleIntelligenceOrbWidget(QWidget):
    """
    Apple Intelligence & Raycast Inspired Expressive AI Orb.
    Monochromatic #7C8CFF palette. Organic breathing, smooth rotation & volume reaction.
    
    States:
      - Idle: Slow breathing (2.5s loop, soft glow)
      - Listening: Active pulse & audio wave resonance
      - Thinking: Smooth rotation (200ms ease)
      - Speaking: Organic expansion / contraction matching voice output
    """

    STATE_IDLE = "idle"
    STATE_LISTENING = "listening"
    STATE_THINKING = "thinking"
    STATE_SPEAKING = "speaking"

    def __init__(self, radius: int = 55, parent=None):
        super().__init__(parent)
        self.base_radius = radius
        padding = max(20, int(radius * 0.6))
        self.setFixedSize(radius * 2 + padding * 2, radius * 2 + padding * 2)

        self.state = self.STATE_IDLE
        self.time = 0.0
        self.speech_pulse = 0.0

        # 60 FPS animation timer (16ms)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16)

    def set_state(self, state: str):
        """Sets orb animation state: 'idle', 'listening', 'thinking', 'speaking'."""
        if state in (self.STATE_IDLE, self.STATE_LISTENING, self.STATE_THINKING, self.STATE_SPEAKING):
            self.state = state
            self.update()

    def set_listening(self, active: bool):
        """Helper for listening toggle."""
        self.set_state(self.STATE_LISTENING if active else self.STATE_IDLE)

    def trigger_speech_pulse(self):
        """Triggered during speech to cause orb expansion."""
        self.speech_pulse = 1.0

    def _update_animation(self):
        speed_map = {
            self.STATE_IDLE: 0.025,
            self.STATE_LISTENING: 0.05,
            self.STATE_THINKING: 0.065,
            self.STATE_SPEAKING: 0.08,
        }
        self.time += speed_map.get(self.state, 0.025)
        
        # Decay speech pulse
        if self.speech_pulse > 0:
            self.speech_pulse = max(0.0, self.speech_pulse - 0.05)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        r = float(self.base_radius)

        # Compute dynamic radius based on state
        if self.state == self.STATE_SPEAKING:
            pulse = math.sin(self.time * 6.0) * 4.5 + self.speech_pulse * 6.0
        elif self.state == self.STATE_THINKING:
            pulse = math.sin(self.time * 4.0) * 2.0
        elif self.state == self.STATE_LISTENING:
            pulse = math.sin(self.time * 5.0) * 5.0
        else: # Idle breathing
            pulse = math.sin(self.time * 2.0) * 2.2

        current_r = r + pulse

        # ─────────────────────────────────────────────────────────────
        # 1. Soft Ambient Perimeter Glow Aura (#7C8CFF)
        # ─────────────────────────────────────────────────────────────
        glow_radius = current_r * 1.55
        glow_grad = QRadialGradient(cx, cy, glow_radius)

        if self.state == self.STATE_SPEAKING:
            glow_grad.setColorAt(0.0, QColor(124, 140, 255, 90))
            glow_grad.setColorAt(0.5, QColor(124, 140, 255, 40))
            glow_grad.setColorAt(1.0, QColor(9, 9, 11, 0))
        elif self.state == self.STATE_LISTENING:
            glow_grad.setColorAt(0.0, QColor(124, 140, 255, 110))
            glow_grad.setColorAt(0.5, QColor(124, 140, 255, 45))
            glow_grad.setColorAt(1.0, QColor(9, 9, 11, 0))
        elif self.state == self.STATE_THINKING:
            glow_grad.setColorAt(0.0, QColor(124, 140, 255, 75))
            glow_grad.setColorAt(0.5, QColor(124, 140, 255, 30))
            glow_grad.setColorAt(1.0, QColor(9, 9, 11, 0))
        else: # Idle
            glow_grad.setColorAt(0.0, QColor(124, 140, 255, 55))
            glow_grad.setColorAt(0.6, QColor(124, 140, 255, 20))
            glow_grad.setColorAt(1.0, QColor(9, 9, 11, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_grad))
        painter.drawEllipse(QPointF(cx, cy), glow_radius, glow_radius)

        # ─────────────────────────────────────────────────────────────
        # 2. Main Luminous Core Gradient (#FAFAFA -> #7C8CFF -> #121215)
        # ─────────────────────────────────────────────────────────────
        core_grad = QRadialGradient(cx - current_r * 0.25, cy - current_r * 0.25, current_r * 1.2)
        core_grad.setColorAt(0.0, QColor(250, 250, 250, 245))       # Crisp white highlight
        core_grad.setColorAt(0.35, QColor(155, 168, 255, 220))     # Soft lavender indigo
        core_grad.setColorAt(0.75, QColor(124, 140, 255, 170))     # Deep #7C8CFF accent
        core_grad.setColorAt(1.0, QColor(18, 18, 21, 140))         # #121215 surface blend

        painter.setBrush(QBrush(core_grad))
        pen_alpha = 180 if self.state in (self.STATE_SPEAKING, self.STATE_LISTENING) else 100
        painter.setPen(QPen(QColor(255, 255, 255, pen_alpha), 1.2))
        painter.drawEllipse(QPointF(cx, cy), current_r, current_r)

        # ─────────────────────────────────────────────────────────────
        # 3. Thinking / Active Motion Orbit Ring & Subtle Particles
        # ─────────────────────────────────────────────────────────────
        if self.state in (self.STATE_THINKING, self.STATE_SPEAKING, self.STATE_LISTENING):
            num_dots = 3
            for i in range(num_dots):
                rot = self.time * (1.5 + i * 0.4) + i * (math.pi * 2 / num_dots)
                dot_r = current_r * 1.22
                dx = cx + dot_r * math.cos(rot)
                dy = cy + dot_r * math.sin(rot)
                dot_size = 2.5
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(250, 250, 250, 200)))
                painter.drawEllipse(QPointF(dx, dy), dot_size, dot_size)


class GifOrbWidget(QWidget):
    """Renders custom animated GIF using QMovie with smooth 60 FPS scaling."""

    def __init__(self, gif_path: str, radius: int = 55, parent=None):
        super().__init__(parent)
        self.radius = radius
        size = radius * 2
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("background: transparent; border: none;")

        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(size, size))
        self.lbl.setMovie(self.movie)
        self.movie.start()

        layout.addWidget(self.lbl)
        self.setMask(QRegion(0, 0, size, size, QRegion.Ellipse))

    def set_listening(self, active: bool):
        if active:
            self.movie.setSpeed(160)
        else:
            self.movie.setSpeed(100)

    def set_state(self, state: str):
        speed_map = {"idle": 100, "listening": 150, "thinking": 180, "speaking": 140}
        self.movie.setSpeed(speed_map.get(state, 100))


class MagicRingsOrbWidget(QWidget):
    """
    Renders React Bits <MagicRings /> WebGL component inside PySide6 QWebEngineView.
    Dynamic state updates (idle, listening, thinking, speaking) drive ring speed, colors, and burst pulse!
    """

    def __init__(self, radius: int = 55, parent=None):
        super().__init__(parent)
        self.radius = radius
        size = radius * 2 + 10
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineSettings

            self.web_view = QWebEngineView()
            self.web_view.setFixedSize(size, size)
            self.web_view.page().setBackgroundColor(QColor(0, 0, 0, 0))
            self.web_view.setStyleSheet("background: transparent; border: none;")

            settings = self.web_view.page().settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

            html_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; overflow: hidden; background: transparent !important; }
    html, body { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background: transparent !important; }
    canvas { width: 100% !important; height: 100% !important; display: block; border-radius: 50%; }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <script>
    const vertexShader = `
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
    `;

    const fragmentShader = `
    precision highp float;

    uniform float uTime, uAttenuation, uLineThickness;
    uniform float uBaseRadius, uRadiusStep, uScaleRate;
    uniform float uOpacity, uNoiseAmount, uRotation, uRingGap;
    uniform float uFadeIn, uFadeOut;
    uniform float uMouseInfluence, uHoverAmount, uHoverScale, uParallax, uBurst;
    uniform vec2 uResolution, uMouse;
    uniform vec3 uColor, uColorTwo;
    uniform int uRingCount;

    const float HP = 1.5707963;
    const float CYCLE = 3.45;

    float fade(float t) {
      return t < uFadeIn ? smoothstep(0.0, uFadeIn, t) : 1.0 - smoothstep(uFadeOut, CYCLE - 0.2, t);
    }

    float ring(vec2 p, float ri, float cut, float t0, float px) {
      float t = mod(uTime + t0, CYCLE);
      float r = ri + t / CYCLE * uScaleRate;
      float d = abs(length(p) - r);
      float a = atan(abs(p.y), abs(p.x)) / HP;
      float th = max(1.0 - a, 0.5) * px * uLineThickness;
      float h = (1.0 - smoothstep(th, th * 1.5, d)) + 1.0;
      d += pow(cut * a, 3.0) * r;
      return h * exp(-uAttenuation * d) * fade(t);
    }

    void main() {
      float px = 1.0 / min(uResolution.x, uResolution.y);
      vec2 p = (gl_FragCoord.xy - 0.5 * uResolution.xy) * px;
      float cr = cos(uRotation), sr = sin(uRotation);
      p = mat2(cr, -sr, sr, cr) * p;
      p -= uMouse * uMouseInfluence;
      float sc = mix(1.0, uHoverScale, uHoverAmount) + uBurst * 0.3;
      p /= sc;
      vec3 c = vec3(0.0);
      float rcf = max(float(uRingCount) - 1.0, 1.0);
      for (int i = 0; i < 10; i++) {
        if (i >= uRingCount) break;
        float fi = float(i);
        vec2 pr = p - fi * uParallax * uMouse;
        vec3 rc = mix(uColor, uColorTwo, fi / rcf);
        c = mix(c, rc, vec3(ring(pr, uBaseRadius + fi * uRadiusStep, pow(uRingGap, fi), i == 0 ? 0.0 : 2.95 * fi, px)));
      }
      c *= 1.0 + uBurst * 2.0;
      float n = fract(sin(dot(gl_FragCoord.xy + uTime * 100.0, vec2(12.9898, 78.233))) * 43758.5453);
      c += (n - 0.5) * uNoiseAmount;
      gl_FragColor = vec4(c, max(c.r, max(c.g, c.b)) * uOpacity);
    }
    `;

    let renderer, scene, camera, uniforms;
    let speed = 1.0;
    let isHovered = false;

    function init() {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setClearColor(0x000000, 0);
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      document.body.appendChild(renderer.domElement);

      scene = new THREE.Scene();
      camera = new THREE.OrthographicCamera(-0.5, 0.5, 0.5, -0.5, 0.1, 10);
      camera.position.z = 1;

      uniforms = {
        uTime: { value: 0 },
        uAttenuation: { value: 10 },
        uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
        uColor: { value: new THREE.Color("#fc42ff") },
        uColorTwo: { value: new THREE.Color("#42fcff") },
        uLineThickness: { value: 2 },
        uBaseRadius: { value: 0.35 },
        uRadiusStep: { value: 0.1 },
        uScaleRate: { value: 0.1 },
        uRingCount: { value: 6 },
        uOpacity: { value: 1 },
        uNoiseAmount: { value: 0.1 },
        uRotation: { value: 0 },
        uRingGap: { value: 1.5 },
        uFadeIn: { value: 0.7 },
        uFadeOut: { value: 0.5 },
        uMouse: { value: new THREE.Vector2(0, 0) },
        uMouseInfluence: { value: 0.2 },
        uHoverAmount: { value: 0 },
        uHoverScale: { value: 1.2 },
        uParallax: { value: 0.05 },
        uBurst: { value: 0 },
      };

      const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms, transparent: true });
      const quad = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
      scene.add(quad);

      window.addEventListener('resize', () => {
        const w = window.innerWidth;
        const h = window.innerHeight;
        renderer.setSize(w, h);
        uniforms.uResolution.value.set(w, h);
      });

      window.addEventListener('mouseenter', () => { isHovered = true; });
      window.addEventListener('mouseleave', () => { isHovered = false; });
      window.addEventListener('click', () => { uniforms.uBurst.value = 1.0; });

      animate(0);
    }

    function animate(t) {
      requestAnimationFrame(animate);
      uniforms.uTime.value = t * 0.001 * speed;
      if (uniforms.uBurst.value > 0.01) {
        uniforms.uBurst.value *= 0.92;
      } else {
        uniforms.uBurst.value = 0;
      }
      uniforms.uHoverAmount.value += ((isHovered ? 1 : 0) - uniforms.uHoverAmount.value) * 0.08;
      renderer.render(scene, camera);
    }

    window.setOrbState = function(state) {
      if (state === "speaking") {
        speed = 2.5;
        uniforms.uBurst.value = 0.9;
      } else if (state === "listening") {
        speed = 1.8;
        uniforms.uColor.value.set("#7c8cff");
        uniforms.uColorTwo.value.set("#42fcff");
      } else if (state === "thinking") {
        speed = 2.0;
        uniforms.uColor.value.set("#a855f7");
        uniforms.uColorTwo.value.set("#fc42ff");
      } else { // idle
        speed = 1.0;
        uniforms.uColor.value.set("#fc42ff");
        uniforms.uColorTwo.value.set("#42fcff");
      }
    };

    window.onload = init;
  </script>
</body>
</html>"""

            self.web_view.setHtml(html_content)
            layout.addWidget(self.web_view)
        except Exception as e:
            print(f"[MagicRingsOrbWidget] Fallback to procedural orb: {e}")
            self.fallback = InvisibleIntelligenceOrbWidget(radius=radius, parent=self)
            layout.addWidget(self.fallback)

    def set_state(self, state: str):
        if hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript(f"if (window.setOrbState) window.setOrbState('{state}');")
        elif hasattr(self, 'fallback'):
            self.fallback.set_state(state)

    def set_listening(self, active: bool):
        self.set_state("listening" if active else "idle")


def create_orb_widget(radius: int = 55, parent=None):
    """Factory function: Returns MagicRingsOrbWidget, GifOrbWidget, or InvisibleIntelligenceOrbWidget."""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        return MagicRingsOrbWidget(radius=radius, parent=parent)
    except Exception:
        pass

    path1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "jarvis_orb.gif"))
    path2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "jarvis_orb.gif"))

    gif_path = path1 if os.path.exists(path1) else (path2 if os.path.exists(path2) else None)
    if gif_path:
        return GifOrbWidget(gif_path, radius=radius, parent=parent)
    return InvisibleIntelligenceOrbWidget(radius=radius, parent=parent)


# Backward compatibility aliases
Procedural3DSphereWidget = MagicRingsOrbWidget
AnimatedJarvisOrbWidget = create_orb_widget


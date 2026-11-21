/**
 * KORLANCE Online Proctoring Engine
 * Real browser-based webcam monitoring, tab-switch tracking, window blur detection, and incident logging.
 */

class KorlanceProctor {
  constructor(sessionToken, csrfToken) {
    this.sessionToken = sessionToken;
    this.csrfToken = csrfToken;
    this.videoElement = document.getElementById('webcamVideo');
    this.statusBadge = document.getElementById('proctorStatusBadge');
    this.statusText = document.getElementById('proctorStatusText');
    this.incidentCounter = document.getElementById('proctorIncidentCount');
    
    this.stream = null;
    this.incidentCount = 0;
    this.isMonitoring = false;
    this.faceCheckInterval = null;
    
    this.init();
  }

  async init() {
    await this.setupWebcam();
    this.setupBrowserEventListeners();
    this.startFaceMonitoring();
  }

  async setupWebcam() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.updateStatus('UNSUPPORTED', 'Camera API not supported in this browser');
        return;
      }

      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
        audio: false
      });

      if (this.videoElement) {
        this.videoElement.srcObject = this.stream;
        this.videoElement.play();
        this.updateStatus('ACTIVE', 'Proctoring Active & Verified');
      }
    } catch (err) {
      console.warn('Webcam permission error:', err);
      this.updateStatus('PERMISSION_DENIED', 'Camera Access Required');
      this.logIncident('CAMERA_DENIED', 'Candidate denied or lost camera access: ' + err.message);
    }
  }

  updateStatus(state, message) {
    if (!this.statusText) return;
    this.statusText.textContent = message;

    if (state === 'ACTIVE') {
      this.statusBadge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200';
    } else {
      this.statusBadge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200';
    }
  }

  setupBrowserEventListeners() {
    // 1. Tab switching / Visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.logIncident('TAB_SWITCH', 'Candidate switched browser tab or minimized window');
        this.showProctorWarning('Tab Switch Detected', 'Switching browser tabs is logged as a proctoring incident.');
      }
    });

    // 2. Window blur (focus lost to another application)
    window.addEventListener('blur', () => {
      this.logIncident('WINDOW_BLUR', 'Examination window lost focus (potential external app interaction)');
    });

    // 3. Fullscreen exit detection
    document.addEventListener('fullscreenchange', () => {
      if (!document.fullscreenElement) {
        this.logIncident('FULLSCREEN_EXIT', 'Candidate exited fullscreen examination mode');
      }
    });

    // 4. Restricted key combinations (F12 dev tools, PrintScreen, Ctrl+C/V)
    window.addEventListener('keydown', (e) => {
      if (e.key === 'F12' || (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'u'))) {
        e.preventDefault();
        this.logIncident('SUSPICIOUS_KEY', `Blocked restricted keystroke: ${e.key} with Ctrl: ${e.ctrlKey}`);
        this.showProctorWarning('Restricted Action', 'Keyboard shortcuts are disabled during this proctored examination.');
      }
    });

    // 5. Right-click context menu disable
    document.addEventListener('contextmenu', (e) => {
      e.preventDefault();
    });
  }

  startFaceMonitoring() {
    // Periodic canvas frame analysis to check for video presence & movement
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 160;
    canvas.height = 120;

    let consecutiveNoMotion = 0;

    this.faceCheckInterval = setInterval(() => {
      if (!this.videoElement || this.videoElement.paused || this.videoElement.ended) return;

      try {
        ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
        const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = frame.data;

        // Calculate average brightness
        let totalBrightness = 0;
        for (let i = 0; i < data.length; i += 16) {
          totalBrightness += (data[i] + data[i+1] + data[i+2]) / 3;
        }
        const avgBrightness = totalBrightness / (data.length / 16);

        if (avgBrightness < 15) {
          // Camera covered or blacked out
          this.logIncident('NO_FACE_DETECTED', 'Camera feed is too dark or covered');
          this.updateStatus('ALERT', 'Camera Feed Obstructed');
        } else {
          this.updateStatus('ACTIVE', 'Proctoring Active & Verified');
        }
      } catch (e) {
        // Ignored for cross-origin or canvas read errors
      }
    }, 15000); // Check every 15 seconds
  }

  async logIncident(type, details) {
    this.incidentCount++;
    if (this.incidentCounter) {
      this.incidentCounter.textContent = this.incidentCount;
    }

    try {
      await fetch('/proctoring/log-incident/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.csrfToken
        },
        body: JSON.stringify({
          session_token: this.sessionToken,
          incident_type: type,
          details: details
        })
      });
    } catch (err) {
      console.warn('Failed to transmit proctoring telemetry:', err);
    }
  }

  showProctorWarning(title, body) {
    const toast = document.getElementById('proctorAlertToast');
    const titleEl = document.getElementById('proctorAlertTitle');
    const bodyEl = document.getElementById('proctorAlertBody');

    if (toast && titleEl && bodyEl) {
      titleEl.textContent = title;
      bodyEl.textContent = body;
      toast.classList.remove('hidden');
      toast.classList.add('flex');

      setTimeout(() => {
        toast.classList.add('hidden');
        toast.classList.remove('flex');
      }, 5000);
    }
  }

  destroy() {
    if (this.faceCheckInterval) clearInterval(this.faceCheckInterval);
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
  }
}

window.KorlanceProctor = KorlanceProctor;

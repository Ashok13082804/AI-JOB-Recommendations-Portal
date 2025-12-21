// Face Recognition JavaScript

let videoStream = null;
let capturedFaceData = null;

// Start webcam
async function startWebcam(videoElementId) {
    const video = document.getElementById(videoElementId);
    if (!video) return;

    try {
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });

        video.srcObject = videoStream;
        video.play();

        const statusElement = document.getElementById('face-status') || document.getElementById('face-login-status');
        if (statusElement) {
            statusElement.textContent = 'Camera ready - Position your face';
            statusElement.style.color = '#0A66C2';
        }

        return true;
    } catch (error) {
        console.error('Webcam error:', error);

        const statusElement = document.getElementById('face-status') || document.getElementById('face-login-status');
        if (statusElement) {
            statusElement.textContent = 'Camera access denied';
            statusElement.style.color = '#CC1016';
        }

        return false;
    }
}

// Stop webcam
function stopWebcam() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

// Capture face
function captureFace() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('face-canvas');

    if (!video || !canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to data URL
    capturedFaceData = canvas.toDataURL('image/jpeg', 0.8);

    // IMPORTANT: Also update the window reference so auth.js can access it
    window.capturedFaceData = capturedFaceData;

    // Show preview
    const preview = document.getElementById('face-preview');
    const capturedImg = document.getElementById('captured-face');
    const webcamContainer = document.querySelector('.webcam-container');

    if (preview && capturedImg && webcamContainer) {
        capturedImg.src = capturedFaceData;
        preview.classList.remove('hidden');
        webcamContainer.style.display = 'none';

        document.getElementById('capture-btn').classList.add('hidden');
        document.getElementById('retake-btn').classList.remove('hidden');

        const statusElement = document.getElementById('face-status');
        if (statusElement) {
            statusElement.textContent = 'Face captured successfully!';
            statusElement.style.color = '#057642';
        }
    }

    // Stop webcam after capture
    stopWebcam();

    console.log('Face captured and stored:', capturedFaceData ? 'yes' : 'no');

    return capturedFaceData;
}

// Retake face photo
function retakeFace() {
    capturedFaceData = null;
    window.capturedFaceData = null;

    const preview = document.getElementById('face-preview');
    const webcamContainer = document.querySelector('.webcam-container');

    if (preview && webcamContainer) {
        preview.classList.add('hidden');
        webcamContainer.style.display = 'block';

        document.getElementById('capture-btn').classList.remove('hidden');
        document.getElementById('retake-btn').classList.add('hidden');
    }

    // Restart webcam
    startWebcam('webcam');
}

// Simple face detection indicator (visual feedback)
function detectFace(videoElement) {
    // In a production app, you would use face-api.js or similar
    // For this demo, we just provide visual feedback

    const statusElement = document.getElementById('face-status') || document.getElementById('face-login-status');

    if (statusElement) {
        // Simulate face detection
        const messages = [
            'Position your face in the circle',
            'Hold still...',
            'Face detected!'
        ];

        let messageIndex = 0;

        const interval = setInterval(() => {
            if (!videoStream) {
                clearInterval(interval);
                return;
            }

            statusElement.textContent = messages[messageIndex];

            if (messageIndex < messages.length - 1) {
                messageIndex++;
            }
        }, 1500);
    }
}

// Compare faces (simplified version for demo)
function compareFaces(storedFace, capturedFace) {
    // In production, use face-api.js or OpenCV
    // For demo, we just check if faces exist
    return storedFace && capturedFace;
}

// Export functions
window.startWebcam = startWebcam;
window.stopWebcam = stopWebcam;
window.captureFace = captureFace;
window.retakeFace = retakeFace;
window.capturedFaceData = capturedFaceData;

// Streaming functionality for Barrot website

let mediaStream = null;
let streamStartTime = null;
let streamDurationInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const startStreamBtn = document.getElementById('startStream');
    const stopStreamBtn = document.getElementById('stopStream');
    const toggleAudioBtn = document.getElementById('toggleAudio');
    const toggleVideoBtn = document.getElementById('toggleVideo');
    const streamVideo = document.getElementById('streamVideo');
    const streamStatus = document.getElementById('streamStatus');
    const streamDuration = document.getElementById('streamDuration');
    const qualitySelector = document.getElementById('qualitySelector');
    
    if (startStreamBtn) {
        startStreamBtn.addEventListener('click', startStream);
    }
    
    if (stopStreamBtn) {
        stopStreamBtn.addEventListener('click', stopStream);
    }
    
    if (toggleAudioBtn) {
        toggleAudioBtn.addEventListener('click', toggleAudio);
    }
    
    if (toggleVideoBtn) {
        toggleVideoBtn.addEventListener('click', toggleVideo);
    }
    
    if (qualitySelector) {
        qualitySelector.addEventListener('change', changeQuality);
    }
});

async function startStream() {
    try {
        const qualitySelector = document.getElementById('qualitySelector');
        const quality = qualitySelector ? qualitySelector.value : '720p';
        
        const constraints = getConstraintsForQuality(quality);
        
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        const streamVideo = document.getElementById('streamVideo');
        if (streamVideo) {
            streamVideo.srcObject = mediaStream;
            streamVideo.play();
        }
        
        // Update UI
        updateStreamStatus('Live', 'success');
        document.getElementById('startStream').disabled = true;
        document.getElementById('stopStream').disabled = false;
        
        // Start duration counter
        streamStartTime = Date.now();
        streamDurationInterval = setInterval(updateDuration, 1000);
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Stream started successfully!', 'success');
        }
        
    } catch (error) {
        console.error('Error starting stream:', error);
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Failed to start stream: ' + error.message, 'error');
        }
        updateStreamStatus('Error', 'error');
    }
}

function stopStream() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
        
        const streamVideo = document.getElementById('streamVideo');
        if (streamVideo) {
            streamVideo.srcObject = null;
        }
        
        // Update UI
        updateStreamStatus('Offline', 'default');
        document.getElementById('startStream').disabled = false;
        document.getElementById('stopStream').disabled = true;
        
        // Stop duration counter
        if (streamDurationInterval) {
            clearInterval(streamDurationInterval);
            streamDurationInterval = null;
        }
        
        const streamDuration = document.getElementById('streamDuration');
        if (streamDuration) {
            streamDuration.textContent = '00:00:00';
        }
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Stream stopped', 'info');
        }
    }
}

function toggleAudio() {
    if (mediaStream) {
        const audioTrack = mediaStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            const toggleAudioBtn = document.getElementById('toggleAudio');
            if (toggleAudioBtn) {
                toggleAudioBtn.innerHTML = audioTrack.enabled 
                    ? '<i class="fas fa-microphone"></i> Toggle Audio'
                    : '<i class="fas fa-microphone-slash"></i> Audio Off';
            }
        }
    }
}

function toggleVideo() {
    if (mediaStream) {
        const videoTrack = mediaStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            const toggleVideoBtn = document.getElementById('toggleVideo');
            if (toggleVideoBtn) {
                toggleVideoBtn.innerHTML = videoTrack.enabled 
                    ? '<i class="fas fa-video"></i> Toggle Video'
                    : '<i class="fas fa-video-slash"></i> Video Off';
            }
        }
    }
}

function changeQuality() {
    if (mediaStream) {
        // Stop current stream and restart with new quality
        const wasStreaming = mediaStream !== null;
        stopStream();
        if (wasStreaming) {
            setTimeout(() => {
                startStream();
            }, 500);
        }
    }
}

function getConstraintsForQuality(quality) {
    const constraints = {
        audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
        },
        video: true
    };
    
    switch(quality) {
        case '1080p':
            constraints.video = {
                width: { ideal: 1920 },
                height: { ideal: 1080 },
                frameRate: { ideal: 30 }
            };
            break;
        case '720p':
            constraints.video = {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                frameRate: { ideal: 30 }
            };
            break;
        case '480p':
            constraints.video = {
                width: { ideal: 854 },
                height: { ideal: 480 },
                frameRate: { ideal: 24 }
            };
            break;
    }
    
    return constraints;
}

function updateStreamStatus(status, type) {
    const streamStatus = document.getElementById('streamStatus');
    if (streamStatus) {
        streamStatus.textContent = status;
        streamStatus.style.color = type === 'success' ? '#10b981' : 
                                   type === 'error' ? '#ef4444' : '#a0aec0';
    }
}

function updateDuration() {
    if (streamStartTime) {
        const elapsed = Math.floor((Date.now() - streamStartTime) / 1000);
        const streamDuration = document.getElementById('streamDuration');
        if (streamDuration && window.BarrotApp) {
            streamDuration.textContent = window.BarrotApp.formatTime(elapsed);
        }
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (mediaStream) {
        stopStream();
    }
});

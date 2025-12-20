// Recording Studio functionality for Barrot website

let audioContext = null;
let mediaRecorder = null;
let audioStream = null;
let recordedChunks = [];
let analyser = null;
let animationId = null;
let isRecording = false;
let isPaused = false;
let recordings = [];

document.addEventListener('DOMContentLoaded', function() {
    const recordBtn = document.getElementById('recordBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const stopRecBtn = document.getElementById('stopRecBtn');
    const playbackBtn = document.getElementById('playbackBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const volumeControl = document.getElementById('volumeControl');
    const reverbControl = document.getElementById('reverbControl');
    const delayControl = document.getElementById('delayControl');
    
    if (recordBtn) {
        recordBtn.addEventListener('click', startRecording);
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseRecording);
    }
    
    if (stopRecBtn) {
        stopRecBtn.addEventListener('click', stopRecording);
    }
    
    if (playbackBtn) {
        playbackBtn.addEventListener('click', playbackRecording);
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadRecording);
    }
    
    if (volumeControl) {
        volumeControl.addEventListener('input', updateVolumeDisplay);
    }
    
    if (reverbControl) {
        reverbControl.addEventListener('input', updateReverbDisplay);
    }
    
    if (delayControl) {
        delayControl.addEventListener('input', updateDelayDisplay);
    }
    
    // Initialize audio visualizer
    initAudioVisualizer();
});

async function startRecording() {
    try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Create audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(audioStream);
        
        // Create analyser
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        
        // Start recording
        mediaRecorder = new MediaRecorder(audioStream);
        recordedChunks = [];
        
        mediaRecorder.ondataavailable = function(e) {
            if (e.data.size > 0) {
                recordedChunks.push(e.data);
            }
        };
        
        mediaRecorder.onstop = function() {
            const blob = new Blob(recordedChunks, { type: 'audio/webm' });
            const recording = {
                id: Date.now(),
                name: `Recording ${recordings.length + 1}`,
                blob: blob,
                url: URL.createObjectURL(blob),
                date: new Date().toLocaleString()
            };
            recordings.push(recording);
            addRecordingToList(recording);
            
            // Enable playback and download
            document.getElementById('playbackBtn').disabled = false;
            document.getElementById('downloadBtn').disabled = false;
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        document.getElementById('recordBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopRecBtn').disabled = false;
        document.getElementById('recordBtn').classList.add('recording-pulse');
        
        // Start visualization
        visualizeAudio();
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Recording started!', 'success');
        }
        
    } catch (error) {
        console.error('Error starting recording:', error);
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Failed to start recording: ' + error.message, 'error');
        }
    }
}

function pauseRecording() {
    if (mediaRecorder && isRecording) {
        if (isPaused) {
            mediaRecorder.resume();
            isPaused = false;
            document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-pause"></i> Pause';
        } else {
            mediaRecorder.pause();
            isPaused = true;
            document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-play"></i> Resume';
        }
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        isPaused = false;
        
        // Stop audio stream
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
        }
        
        // Stop visualization
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        
        // Update UI
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopRecBtn').disabled = true;
        document.getElementById('recordBtn').classList.remove('recording-pulse');
        document.getElementById('pauseBtn').innerHTML = '<i class="fas fa-pause"></i> Pause';
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Recording stopped!', 'info');
        }
    }
}

function playbackRecording() {
    if (recordings.length > 0) {
        const latestRecording = recordings[recordings.length - 1];
        const audio = new Audio(latestRecording.url);
        audio.play();
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Playing recording...', 'info');
        }
    }
}

function downloadRecording() {
    if (recordings.length > 0) {
        const latestRecording = recordings[recordings.length - 1];
        const a = document.createElement('a');
        a.href = latestRecording.url;
        a.download = `${latestRecording.name}.webm`;
        a.click();
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Downloading recording...', 'success');
        }
    }
}

function addRecordingToList(recording) {
    const recordingsList = document.getElementById('recordingsList');
    if (!recordingsList) return;
    
    // Remove empty state if exists
    const emptyState = recordingsList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const recordingItem = document.createElement('div');
    recordingItem.className = 'recording-item';
    recordingItem.innerHTML = `
        <div>
            <strong>${recording.name}</strong>
            <br>
            <small style="color: var(--text-secondary);">${recording.date}</small>
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-sm btn-primary" onclick="playRecording(${recording.id})">
                <i class="fas fa-play"></i>
            </button>
            <button class="btn btn-sm btn-success" onclick="downloadRecordingById(${recording.id})">
                <i class="fas fa-download"></i>
            </button>
        </div>
    `;
    
    recordingsList.appendChild(recordingItem);
}

function playRecording(id) {
    const recording = recordings.find(r => r.id === id);
    if (recording) {
        const audio = new Audio(recording.url);
        audio.play();
    }
}

function downloadRecordingById(id) {
    const recording = recordings.find(r => r.id === id);
    if (recording) {
        const a = document.createElement('a');
        a.href = recording.url;
        a.download = `${recording.name}.webm`;
        a.click();
    }
}

function initAudioVisualizer() {
    const canvas = document.getElementById('audioCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 200;
    
    // Draw initial state
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#00ff88';
    ctx.font = '20px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Click Record to start', canvas.width / 2, canvas.height / 2);
}

function visualizeAudio() {
    if (!analyser) return;
    
    const canvas = document.getElementById('audioCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    function draw() {
        animationId = requestAnimationFrame(draw);
        
        analyser.getByteTimeDomainData(dataArray);
        
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#00ff88';
        ctx.beginPath();
        
        const sliceWidth = canvas.width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * canvas.height / 2;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
        
        // Draw frequency bars
        analyser.getByteFrequencyData(dataArray);
        const barWidth = canvas.width / bufferLength * 2.5;
        let barX = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height / 2;
            
            const hue = (i / bufferLength) * 360;
            ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
            ctx.fillRect(barX, canvas.height - barHeight, barWidth, barHeight);
            
            barX += barWidth + 1;
            
            if (barX > canvas.width) break;
        }
    }
    
    draw();
}

function updateVolumeDisplay() {
    const volumeControl = document.getElementById('volumeControl');
    const volumeValue = document.getElementById('volumeValue');
    if (volumeControl && volumeValue) {
        volumeValue.textContent = volumeControl.value + '%';
    }
}

function updateReverbDisplay() {
    const reverbControl = document.getElementById('reverbControl');
    const reverbValue = document.getElementById('reverbValue');
    if (reverbControl && reverbValue) {
        reverbValue.textContent = reverbControl.value + '%';
    }
}

function updateDelayDisplay() {
    const delayControl = document.getElementById('delayControl');
    const delayValue = document.getElementById('delayValue');
    if (delayControl && delayValue) {
        delayValue.textContent = delayControl.value + '%';
    }
}

// Make functions globally available
window.playRecording = playRecording;
window.downloadRecordingById = downloadRecordingById;

// Chat functionality for Barrot website

document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    
    if (sendMessage) {
        sendMessage.addEventListener('click', sendChatMessage);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
});

function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    const message = chatInput.value.trim();
    if (message === '') return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    // Simulate AI response
    setTimeout(() => {
        const response = generateBarrotResponse(message);
        addMessageToChat(response, 'bot');
    }, 1000);
}

function sendQuickQuestion(question) {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = question;
        sendChatMessage();
    }
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' 
        ? '<i class="fas fa-user"></i>' 
        : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const text = document.createElement('p');
    text.textContent = message;
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString();
    
    content.appendChild(text);
    content.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function generateBarrotResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    // Predefined responses based on keywords
    if (lowerMessage.includes('stream') || lowerMessage.includes('streaming')) {
        return "To start streaming, navigate to the Streaming section and click the 'Start Stream' button. Make sure to grant camera and microphone permissions when prompted. You can adjust the quality settings and toggle audio/video as needed.";
    }
    
    if (lowerMessage.includes('record') || lowerMessage.includes('recording')) {
        return "The Recording Studio allows you to record high-quality audio with real-time visualization. Click the Record button to start, and you can pause, stop, and download your recordings. All recordings are saved locally in your browser.";
    }
    
    if (lowerMessage.includes('render') || lowerMessage.includes('3d')) {
        return "Our 3D Rendering tool uses Three.js to create interactive 3D visualizations. You can choose different shapes, adjust rotation speed, change colors, and export your renders as images. Try dragging the object with your mouse to rotate it manually!";
    }
    
    if (lowerMessage.includes('feature') || lowerMessage.includes('what can')) {
        return "Barrot offers several powerful features: Live Streaming with WebRTC, a Recording Studio with audio visualization, 3D Rendering with interactive controls, real-time chat assistance, and cloud storage capabilities. All features work directly in your browser with no additional software needed!";
    }
    
    if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
        return "I'm here to help! You can ask me about streaming, recording, 3D rendering, or any other features. Just type your question and I'll do my best to assist you. You can also use the quick question buttons for common queries.";
    }
    
    if (lowerMessage.includes('audio') || lowerMessage.includes('sound')) {
        return "Our audio production tools include a full recording studio with real-time visualization, volume control, reverb, and delay effects. You can record, pause, playback, and download your audio creations. The Web Audio API provides professional-grade audio processing.";
    }
    
    if (lowerMessage.includes('video')) {
        return "Video streaming is powered by WebRTC technology, allowing you to stream directly from your camera. You can control video quality (480p, 720p, 1080p), toggle video on/off, and monitor stream duration. All processing happens in real-time with minimal latency.";
    }
    
    if (lowerMessage.includes('thank') || lowerMessage.includes('thanks')) {
        return "You're welcome! I'm always here to help. Feel free to explore all the features Barrot has to offer. If you have any other questions, just ask!";
    }
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
        return "Hello! Welcome to Barrot! I'm your AI assistant, ready to help you explore our multimedia platform. What would you like to know about?";
    }
    
    // Default response
    const defaultResponses = [
        "That's an interesting question! Barrot is designed to provide powerful multimedia tools right in your browser. Would you like to know more about a specific feature?",
        "I can help you with streaming, recording, 3D rendering, and more. What would you like to explore?",
        "Barrot combines cutting-edge web technologies to deliver a seamless creative experience. Ask me about any of our features!",
        "Great question! Our platform offers streaming, recording studio, 3D rendering, and AI chat capabilities. Which one interests you most?"
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// Make sendQuickQuestion globally available
window.sendQuickQuestion = sendQuickQuestion;

// Advanced chat features
class ChatBot {
    constructor() {
        this.conversationHistory = [];
    }
    
    addToHistory(message, sender) {
        this.conversationHistory.push({
            message: message,
            sender: sender,
            timestamp: new Date()
        });
        
        // Keep only last 50 messages
        if (this.conversationHistory.length > 50) {
            this.conversationHistory.shift();
        }
    }
    
    getHistory() {
        return this.conversationHistory;
    }
    
    clearHistory() {
        this.conversationHistory = [];
    }
}

// Initialize chatbot
const barrotChatBot = new ChatBot();

// Export for use in other modules
window.BarrotChat = {
    sendMessage: sendChatMessage,
    sendQuickQuestion: sendQuickQuestion,
    chatBot: barrotChatBot
};

const express = require('express');
const cors = require('cors');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../website')));

// Database setup
const dbPath = process.env.DB_PATH || path.join(__dirname, 'db', 'barrot.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Database connection error:', err);
    } else {
        console.log('Connected to SQLite database');
        initDatabase();
    }
});

// Initialize database tables
function initDatabase() {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    db.run(`CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`);
    
    db.run(`CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        duration INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`);
    
    db.run(`CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_token TEXT UNIQUE NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`);
    
    console.log('Database tables initialized');
}

// API Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Barrot API is running' });
});

// Chat endpoints
app.post('/api/chat/message', (req, res) => {
    const { message, userId } = req.body;
    
    if (!message) {
        return res.status(400).json({ error: 'Message is required' });
    }
    
    // Generate response (in a real app, this would use an AI service)
    const response = generateResponse(message);
    
    // Save to database
    db.run(
        'INSERT INTO chat_messages (user_id, message, response) VALUES (?, ?, ?)',
        [userId || null, message, response],
        function(err) {
            if (err) {
                console.error('Error saving chat message:', err);
                return res.status(500).json({ error: 'Failed to save message' });
            }
            
            res.json({
                id: this.lastID,
                message: message,
                response: response,
                timestamp: new Date().toISOString()
            });
        }
    );
});

// Get chat history
app.get('/api/chat/history', (req, res) => {
    const { userId, limit = 50 } = req.query;
    
    let query = 'SELECT * FROM chat_messages';
    let params = [];
    
    if (userId) {
        query += ' WHERE user_id = ?';
        params.push(userId);
    }
    
    query += ' ORDER BY created_at DESC LIMIT ?';
    params.push(parseInt(limit));
    
    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('Error fetching chat history:', err);
            return res.status(500).json({ error: 'Failed to fetch history' });
        }
        
        res.json({ messages: rows });
    });
});

// User endpoints
app.post('/api/users', (req, res) => {
    const { username, email } = req.body;
    
    if (!username || !email) {
        return res.status(400).json({ error: 'Username and email are required' });
    }
    
    db.run(
        'INSERT INTO users (username, email) VALUES (?, ?)',
        [username, email],
        function(err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint')) {
                    return res.status(409).json({ error: 'Username or email already exists' });
                }
                console.error('Error creating user:', err);
                return res.status(500).json({ error: 'Failed to create user' });
            }
            
            res.status(201).json({
                id: this.lastID,
                username: username,
                email: email
            });
        }
    );
});

app.get('/api/users/:id', (req, res) => {
    const { id } = req.params;
    
    db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
        if (err) {
            console.error('Error fetching user:', err);
            return res.status(500).json({ error: 'Failed to fetch user' });
        }
        
        if (!row) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        res.json(row);
    });
});

// Recording endpoints
app.post('/api/recordings', (req, res) => {
    const { userId, filename, filePath, duration } = req.body;
    
    if (!filename || !filePath) {
        return res.status(400).json({ error: 'Filename and file path are required' });
    }
    
    db.run(
        'INSERT INTO recordings (user_id, filename, file_path, duration) VALUES (?, ?, ?, ?)',
        [userId || null, filename, filePath, duration || null],
        function(err) {
            if (err) {
                console.error('Error saving recording:', err);
                return res.status(500).json({ error: 'Failed to save recording' });
            }
            
            res.status(201).json({
                id: this.lastID,
                filename: filename,
                filePath: filePath,
                duration: duration
            });
        }
    );
});

app.get('/api/recordings', (req, res) => {
    const { userId, limit = 50 } = req.query;
    
    let query = 'SELECT * FROM recordings';
    let params = [];
    
    if (userId) {
        query += ' WHERE user_id = ?';
        params.push(userId);
    }
    
    query += ' ORDER BY created_at DESC LIMIT ?';
    params.push(parseInt(limit));
    
    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('Error fetching recordings:', err);
            return res.status(500).json({ error: 'Failed to fetch recordings' });
        }
        
        res.json({ recordings: rows });
    });
});

// Session management
app.post('/api/sessions', (req, res) => {
    const { userId } = req.body;
    
    if (!userId) {
        return res.status(400).json({ error: 'User ID is required' });
    }
    
    const sessionToken = generateSessionToken();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours
    
    db.run(
        'INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
        [userId, sessionToken, expiresAt.toISOString()],
        function(err) {
            if (err) {
                console.error('Error creating session:', err);
                return res.status(500).json({ error: 'Failed to create session' });
            }
            
            res.status(201).json({
                sessionId: this.lastID,
                sessionToken: sessionToken,
                expiresAt: expiresAt.toISOString()
            });
        }
    );
});

// Serve the main website
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../website/index.html'));
});

// Helper functions
function generateResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('stream')) {
        return "To start streaming, navigate to the Streaming section and click 'Start Stream'.";
    }
    if (lowerMessage.includes('record')) {
        return "The Recording Studio allows you to record audio with real-time visualization.";
    }
    if (lowerMessage.includes('render') || lowerMessage.includes('3d')) {
        return "Our 3D Rendering tool uses Three.js for interactive visualizations.";
    }
    
    return "I'm Barrot, your AI assistant. How can I help you today?";
}

function generateSessionToken() {
    return require('crypto').randomBytes(32).toString('hex');
}

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
    console.log(`Barrot server running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to access the application`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing database:', err);
        } else {
            console.log('Database connection closed');
        }
        process.exit(0);
    });
});

module.exports = app;

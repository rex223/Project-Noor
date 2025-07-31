// Main JavaScript for The Last Neuron
class TheLastNeuron {
    constructor() {
        this.wsConnection = null;
        this.isTyping = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeChat();
        this.setupNotifications();
    }

    setupEventListeners() {
        // Chat form submission
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', this.handleChatSubmit.bind(this));
        }

        // Message feedback buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('feedback-btn')) {
                this.handleMessageFeedback(e);
            }
        });

        // Mood selector
        const moodSelector = document.querySelector('.mood-selector');
        if (moodSelector) {
            moodSelector.addEventListener('click', this.handleMoodSelect.bind(this));
        }

        // Game choices
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('game-choice')) {
                this.handleGameChoice(e);
            }
        });
    }

    initializeChat() {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;

        // Get session ID from the page
        const sessionId = chatContainer.dataset.sessionId;
        if (!sessionId) return;

        // Initialize WebSocket connection
        this.connectWebSocket(sessionId);
    }

    connectWebSocket(sessionId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${sessionId}/`;

        this.wsConnection = new WebSocket(wsUrl);

        this.wsConnection.onopen = () => {
            console.log('WebSocket connected');
            this.showNotification('Connected to The Last Neuron', 'success');
        };

        this.wsConnection.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.wsConnection.onclose = () => {
            console.log('WebSocket disconnected');
            this.showNotification('Connection lost. Reconnecting...', 'warning');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                this.connectWebSocket(sessionId);
            }, 3000);
        };

        this.wsConnection.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection error', 'error');
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'agent_message':
                this.addMessage('agent', data.content, data.timestamp);
                this.hideTypingIndicator();
                break;
            case 'agent_typing':
                if (data.typing) {
                    this.showTypingIndicator();
                } else {
                    this.hideTypingIndicator();
                }
                break;
            case 'proactive_message':
                this.addProactiveMessage(data.content, data.trigger_type);
                break;
            case 'error':
                this.showNotification(data.message, 'error');
                break;
        }
    }

    handleChatSubmit(event) {
        event.preventDefault();
        
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message || !this.wsConnection) return;

        // Add user message to chat
        this.addMessage('user', message);
        
        // Send message via WebSocket
        this.wsConnection.send(JSON.stringify({
            type: 'message',
            content: message
        }));

        // Clear input
        messageInput.value = '';
        messageInput.focus();
    }

    addMessage(type, content, timestamp = null) {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} fade-in-up`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        messageDiv.appendChild(bubbleDiv);

        // Add timestamp if provided
        if (timestamp) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'text-xs text-gray-500 mt-1';
            timeDiv.textContent = new Date(timestamp).toLocaleTimeString();
            messageDiv.appendChild(timeDiv);
        }

        // Add feedback buttons for agent messages
        if (type === 'agent') {
            const feedbackDiv = this.createFeedbackButtons();
            messageDiv.appendChild(feedbackDiv);
        }

        chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addProactiveMessage(content, triggerType) {
        this.addMessage('agent', content);
        this.showNotification(`${triggerType}: ${content}`, 'info');
    }

    createFeedbackButtons() {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons mt-2 space-x-2';
        feedbackDiv.innerHTML = `
            <button class="feedback-btn text-sm text-gray-500 hover:text-green-500" data-rating="5">👍</button>
            <button class="feedback-btn text-sm text-gray-500 hover:text-red-500" data-rating="1">👎</button>
        `;
        return feedbackDiv;
    }

    handleMessageFeedback(event) {
        const rating = event.target.dataset.rating;
        const messageElement = event.target.closest('.message');
        
        if (this.wsConnection) {
            this.wsConnection.send(JSON.stringify({
                type: 'feedback',
                message_id: messageElement.dataset.messageId,
                rating: parseInt(rating),
                is_helpful: rating === '5'
            }));
        }

        // Visual feedback
        event.target.classList.add('text-blue-500');
        this.showNotification('Feedback recorded. Thank you!', 'success');
    }

    handleMoodSelect(event) {
        if (!event.target.classList.contains('mood-option')) return;

        // Remove previous selection
        document.querySelectorAll('.mood-option').forEach(option => {
            option.classList.remove('selected');
        });

        // Add selection to clicked option
        event.target.classList.add('selected');

        const mood = event.target.dataset.mood;
        
        // Send mood update via WebSocket
        if (this.wsConnection) {
            this.wsConnection.send(JSON.stringify({
                type: 'mood_update',
                mood: mood
            }));
        }

        this.showNotification(`Mood updated to ${mood}`, 'success');
    }

    handleGameChoice(event) {
        // Remove previous selections
        document.querySelectorAll('.game-choice').forEach(choice => {
            choice.classList.remove('selected');
        });

        // Add selection to clicked choice
        event.target.classList.add('selected');

        // Enable next button if exists
        const nextButton = document.getElementById('next-button');
        if (nextButton) {
            nextButton.disabled = false;
            nextButton.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message agent fade-in-up';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;

        chatContainer.appendChild(typingDiv);
        this.scrollToBottom();
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
            this.isTyping = false;
        }
    }

    scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        notification.style.borderLeftColor = colors[type] || colors.info;
        notification.innerHTML = `
            <div class="flex items-start">
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <button class="ml-2 text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.remove()">
                    ✕
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    setupNotifications() {
        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    // Personality Chart Visualization
    createPersonalityChart(canvasId, personalityData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
                datasets: [{
                    label: 'Your Personality',
                    data: personalityData,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 1
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Progress tracking
    updateProgress(elementId, percentage) {
        const progressBar = document.getElementById(elementId);
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-bar-fill');
            if (fill) {
                fill.style.width = `${percentage}%`;
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.theLastNeuron = new TheLastNeuron();
});

// HTMX Event Handlers
document.addEventListener('htmx:afterRequest', (event) => {
    // Handle HTMX responses
    if (event.detail.xhr.status === 200) {
        window.theLastNeuron.showNotification('Action completed successfully', 'success');
    }
});

document.addEventListener('htmx:responseError', (event) => {
    window.theLastNeuron.showNotification('An error occurred. Please try again.', 'error');
});

// Export for use in other scripts
window.TheLastNeuron = TheLastNeuron;

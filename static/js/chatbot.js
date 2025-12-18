/**
 * C_Bot - AI Health Assistant Chatbot
 * TeleMed - Telemedicine Access for Rural Healthcare
 */

class CBot {
    constructor() {
        this.toggleBtn = document.getElementById('chatbot-toggle');
        this.window = document.getElementById('chatbot-window');
        this.closeBtn = document.getElementById('chatbot-close');
        this.messagesContainer = document.getElementById('chatbot-messages');
        this.input = document.getElementById('chatbot-input');
        this.sendBtn = document.getElementById('chatbot-send');

        this.isTyping = false;
        this.init();
    }

    init() {
        if (!this.toggleBtn) return;

        // Toggle chatbot window
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // Close chatbot
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }

        // Send message
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Enter key to send
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        // Quick replies
        this.setupQuickReplies();
    }

    toggle() {
        if (this.window) {
            this.window.classList.toggle('active');
            if (this.window.classList.contains('active')) {
                this.input.focus();
            }
        }
    }

    close() {
        if (this.window) {
            this.window.classList.remove('active');
        }
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isTyping) return;

        // Add user message
        this.addMessage(message, 'user');
        this.input.value = '';

        // Show typing indicator
        this.showTyping();

        try {
            // Send to server
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            this.hideTyping();

            // Add bot response
            this.addMessage(data.response, 'bot');

            // Add quick replies based on context
            this.addQuickReplies(message);

        } catch (error) {
            this.hideTyping();
            this.addMessage("I'm sorry, I'm having trouble connecting. Please try again later.", 'bot');
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.textContent = text;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span style="display: flex; gap: 4px;">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </span>
        `;

        // Add CSS for typing animation if not exists
        if (!document.getElementById('typing-styles')) {
            const style = document.createElement('style');
            style.id = 'typing-styles';
            style.textContent = `
                .typing-indicator .dot {
                    width: 8px;
                    height: 8px;
                    background: var(--primary-400);
                    border-radius: 50%;
                    animation: bounce 1.4s infinite ease-in-out;
                }
                .typing-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator .dot:nth-child(2) { animation-delay: -0.16s; }
                @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }

        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    addQuickReplies(lastMessage) {
        // Remove existing quick replies
        const existingReplies = this.messagesContainer.querySelector('.quick-replies');
        if (existingReplies) existingReplies.remove();

        // Determine relevant quick replies
        let replies = [];
        const lowerMessage = lastMessage.toLowerCase();

        if (lowerMessage.includes('appointment') || lowerMessage.includes('book')) {
            replies = ['Book Video Consultation', 'Book Chat Consultation', 'View Appointments'];
        } else if (lowerMessage.includes('hospital') || lowerMessage.includes('near')) {
            replies = ['Find Hospitals', 'Check Bed Availability', 'Emergency Services'];
        } else if (lowerMessage.includes('symptom') || lowerMessage.includes('sick') || lowerMessage.includes('pain')) {
            replies = ['Consult a Doctor', 'Emergency Help', 'Mobile Clinic'];
        } else {
            replies = ['Book Appointment', 'Find Hospitals', 'Check Symptoms', 'Emergency'];
        }

        const repliesDiv = document.createElement('div');
        repliesDiv.className = 'quick-replies';
        repliesDiv.style.cssText = 'display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;';

        replies.forEach(reply => {
            const btn = document.createElement('button');
            btn.className = 'quick-reply-btn';
            btn.textContent = reply;
            btn.style.cssText = `
                padding: 6px 12px;
                background: var(--primary-50);
                color: var(--primary-600);
                border: 1px solid var(--primary-200);
                border-radius: 20px;
                font-size: 0.75rem;
                cursor: pointer;
                transition: all 0.2s;
            `;
            btn.addEventListener('click', () => {
                this.input.value = reply;
                this.sendMessage();
            });
            btn.addEventListener('mouseover', () => {
                btn.style.background = 'var(--primary-100)';
            });
            btn.addEventListener('mouseout', () => {
                btn.style.background = 'var(--primary-50)';
            });
            repliesDiv.appendChild(btn);
        });

        this.messagesContainer.appendChild(repliesDiv);
        this.scrollToBottom();
    }

    setupQuickReplies() {
        // Add initial quick replies after a delay
        setTimeout(() => {
            if (this.messagesContainer.querySelectorAll('.chat-message').length <= 1) {
                this.addQuickReplies('welcome');
            }
        }, 1000);
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    getCsrfToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    window.cbot = new CBot();
});

console.log('C_Bot - Chatbot JS loaded successfully');

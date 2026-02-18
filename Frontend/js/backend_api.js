/* ═══════════════════════════════════════════════════
   BACKEND API CLIENT
   Handles communication between frontend and backend server
   ═══════════════════════════════════════════════════ */

class BackendAPIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    // ═══════════════════════════════════════════════════
    // REST API METHODS
    // ═══════════════════════════════════════════════════

    /**
     * Send vital signs data to backend for ML processing
     */
    async sendVitals(vitalsData) {
        try {
            const response = await fetch(`${this.baseURL}/api/vitals`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(vitalsData)
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Vitals sent and processed by ML model');
                return data.data;
            } else {
                console.error('❌ Error processing vitals:', data.error);
                return null;
            }
        } catch (error) {
            console.error('❌ Failed to send vitals to backend:', error);
            return null;
        }
    }

    /**
     * Get latest vitals for a soldier from backend
     */
    async getLatestVitals(soldierId) {
        try {
            const response = await fetch(`${this.baseURL}/api/vitals/latest/${soldierId}`);
            const data = await response.json();
            
            if (data.success) {
                return data.data;
            }
            return null;
        } catch (error) {
            console.error('❌ Failed to get latest vitals:', error);
            return null;
        }
    }

    /**
     * Get vitals history for a soldier
     */
    async getVitalsHistory(soldierId, limit = 100, hours = 24) {
        try {
            const response = await fetch(
                `${this.baseURL}/api/vitals/history/${soldierId}?limit=${limit}&hours=${hours}`
            );
            const data = await response.json();
            
            if (data.success) {
                return data.data;
            }
            return [];
        } catch (error) {
            console.error('❌ Failed to get vitals history:', error);
            return [];
        }
    }

    /**
     * Get ML risk prediction for given vitals
     */
    async predictRisk(vitalsData) {
        try {
            const response = await fetch(`${this.baseURL}/api/predict/risk`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(vitalsData)
            });

            const data = await response.json();
            
            if (data.success) {
                return data.prediction;
            }
            return null;
        } catch (error) {
            console.error('❌ Failed to get risk prediction:', error);
            return null;
        }
    }

    /**
     * Get active alerts for a soldier
     */
    async getAlerts(soldierId) {
        try {
            const response = await fetch(`${this.baseURL}/api/alerts/${soldierId}`);
            const data = await response.json();
            
            if (data.success) {
                return data.alerts;
            }
            return [];
        } catch (error) {
            console.error('❌ Failed to get alerts:', error);
            return [];
        }
    }

    /**
     * Simulate data (for testing without real sensors)
     */
    async simulateData() {
        try {
            const response = await fetch(`${this.baseURL}/api/simulate`, {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Simulated data generated');
                return data.data;
            }
            return null;
        } catch (error) {
            console.error('❌ Simulation failed:', error);
            return null;
        }
    }

    /**
     * Check if backend server is running
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            const data = await response.json();
            return data.status === 'operational';
        } catch (error) {
            return false;
        }
    }

    // ═══════════════════════════════════════════════════
    // WEBSOCKET METHODS (Real-time Updates)
    // ═══════════════════════════════════════════════════

    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket(onVitalsUpdate, onConnect, onDisconnect) {
        // Load Socket.IO client library
        if (typeof io === 'undefined') {
            console.error('❌ Socket.IO library not loaded. Include: <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>');
            return;
        }

        console.log('🔌 Connecting to WebSocket...');
        
        this.socket = io(this.baseURL, {
            transports: ['websocket', 'polling']
        });

        // Connection established
        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            if (onConnect) onConnect();
        });

        // Connection response
        this.socket.on('connection_response', (data) => {
            console.log('📡 Server says:', data.message);
        });

        // Real-time vitals updates
        this.socket.on('vitals_update', (data) => {
            console.log('📊 Received vitals update from backend');
            
            if (onVitalsUpdate) {
                onVitalsUpdate(data);
            }
        });

        // Disconnection
        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
            this.isConnected = false;
            
            if (onDisconnect) onDisconnect();
            
            // Attempt reconnection
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    console.log(`🔄 Reconnecting... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
                    this.reconnectAttempts++;
                }, 2000);
            }
        });

        // Error handling
        this.socket.on('connect_error', (error) => {
            console.error('❌ WebSocket connection error:', error.message);
        });

        this.socket.on('error', (error) => {
            console.error('❌ WebSocket error:', error);
        });
    }

    /**
     * Request vitals data via WebSocket
     */
    requestVitals(soldierId) {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_vitals', { soldier_id: soldierId });
        } else {
            console.warn('⚠️ WebSocket not connected');
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnectWebSocket() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
            console.log('🔌 WebSocket disconnected');
        }
    }
}

// ═══════════════════════════════════════════════════
// GLOBAL INSTANCE
// ═══════════════════════════════════════════════════

// Create global API client instance
window.backendAPI = new BackendAPIClient('http://localhost:5000');

console.log('%c Backend API Client Loaded ', 'background: #D4AF37; color: white; padding: 8px; font-weight: bold;');
console.log('✅ Use window.backendAPI to communicate with backend');


function loginWithGoogle() {
    window.location.href = "http://localhost:5000/google/login";
}

async function fetchHeartRate() {
    const response = await fetch("http://localhost:5000/google/heart");
    const data = await response.json();
    console.log(data);
}
/* ═══════════════════════════════════════════════════
   DASHBOARD JAVASCRIPT - Real-Time Monitoring
   ═══════════════════════════════════════════════════ */

// Global health data state
let healthData = {
    heartRate: 72,
    spo2: 96,
    systolic: 120,
    diastolic: 80,
    temperature: 36.8,
    altitude: 5400,
    extTemp: -15,
    humidity: 42
};

let charts = {};
let autoUpdateEnabled = true;
let updateIntervalId = null;
let backendMode = false; // Toggle between local simulation and backend ML processing

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    updateAllMetrics();
    updateClock();
    setInterval(updateClock, 1000);
    
    // Initialize manual input fields with current values
    syncManualInputs();
    
    // Check if backend is available
    checkBackendAvailability();
    
    // Start appropriate update mode
    if (backendMode) {
        startBackendMode();
    } else {
        startRealTimeUpdates();
    }
});

// Update clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const elem = document.getElementById('lastUpdate');
    if (elem) elem.textContent = timeString;
}

// Initialize Chart.js charts
function initializeCharts() {
    const goldGradient = (ctx) => {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(212, 175, 55, 0.3)');
        gradient.addColorStop(1, 'rgba(212, 175, 55, 0.05)');
        return gradient;
    };
    
    const chartConfig = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { display: false }
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(209, 213, 219, 0.3)',
                    borderColor: 'rgba(209, 213, 219, 0.5)'
                },
                ticks: {
                    color: '#6B7280',
                    font: { family: 'Poppins', size: 11 }
                }
            },
            x: {
                grid: {
                    color: 'rgba(209, 213, 219, 0.3)',
                    borderColor: 'rgba(209, 213, 219, 0.5)'
                },
                ticks: {
                    color: '#6B7280',
                    font: { family: 'Poppins', size: 11 }
                }
            }
        }
    };

    // Heart Rate Mini Chart
    const hrCtx = document.getElementById('heartRateChart');
    if (hrCtx) {
        charts.heartRateMini = new Chart(hrCtx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', '', '', '', ''],
                datasets: [{
                    data: generateRandomData(10, 68, 76),
                    borderColor: '#D4AF37',
                    backgroundColor: 'rgba(212, 175, 55, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { display: false },
                    x: { display: false }
                }
            }
        });
    }

    // HR Trend Chart
    const hrTrendCtx = document.getElementById('hrTrendChart');
    if (hrTrendCtx) {
        charts.hrTrend = new Chart(hrTrendCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(20),
                datasets: [{
                    label: 'Heart Rate',
                    data: generateRandomData(20, 68, 76),
                    borderColor: '#D4AF37',
                    backgroundColor: (ctx) => goldGradient(ctx.chart.ctx),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { ...chartConfig }
        });
    }

    // SpO2 Trend Chart
    const spo2TrendCtx = document.getElementById('spo2TrendChart');
    if (spo2TrendCtx) {
        charts.spo2Trend = new Chart(spo2TrendCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(20),
                datasets: [{
                    label: 'SpO2',
                    data: generateRandomData(20, 94, 98),
                    borderColor: '#F5C542',
                    backgroundColor: (ctx) => {
                        const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 400);
                        gradient.addColorStop(0, 'rgba(245, 197, 66, 0.3)');
                        gradient.addColorStop(1, 'rgba(245, 197, 66, 0.05)');
                        return gradient;
                    },
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { ...chartConfig }
        });
    }

    // Sleep Chart
    const sleepCtx = document.getElementById('sleepChart');
    if (sleepCtx) {
        charts.sleep = new Chart(sleepCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Sleep Hours',
                    data: [7.2, 6.8, 7.5, 6.5, 7.1, 8.0, 7.8],
                    backgroundColor: 'rgba(212, 175, 55, 0.6)',
                    borderColor: '#D4AF37',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: { ...chartConfig }
        });
    }

    // Stability Chart
    const stabilityCtx = document.getElementById('stabilityChart');
    if (stabilityCtx) {
        charts.stability = new Chart(stabilityCtx, {
            type: 'line',
            data: {
                labels: generateTimeLabels(10),
                datasets: [{
                    label: 'Stability Score',
                    data: generateRandomData(10, 80, 95),
                    borderColor: '#D4AF37',
                    backgroundColor: (ctx) => goldGradient(ctx.chart.ctx),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { ...chartConfig }
        });
    }
}

// Helper: Generate time labels
function generateTimeLabels(count) {
    const labels = [];
    const now = new Date();
    for (let i = count - 1; i >= 0; i--) {
        const time = new Date(now - i * 60000);
        labels.push(time.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }));
    }
    return labels;
}

// Helper: Generate random data
function generateRandomData(count, min, max) {
    return Array.from({ length: count }, () => 
        Math.random() * (max - min) + min
    );
}

// Start real-time updates
function startRealTimeUpdates() {
    setInterval(() => {
        simulateDataChanges();
        updateAllMetrics();
        updateCharts();
    }, 3000);
}

// Simulate realistic data changes
function simulateDataChanges() {
    healthData.heartRate += (Math.random() - 0.5) * 2;
    healthData.heartRate = Math.max(60, Math.min(90, healthData.heartRate));
    
    healthData.spo2 += (Math.random() - 0.5) * 0.5;
    healthData.spo2 = Math.max(90, Math.min(100, healthData.spo2));
    
    healthData.systolic += (Math.random() - 0.5) * 1.5;
    healthData.systolic = Math.max(100, Math.min(135, healthData.systolic));
    
    healthData.diastolic += (Math.random() - 0.5) * 1;
    healthData.diastolic = Math.max(65, Math.min(85, healthData.diastolic));
    
    healthData.temperature += (Math.random() - 0.5) * 0.1;
    healthData.temperature = Math.max(36, Math.min(37.5, healthData.temperature));
}

// Update all metrics on page
function updateAllMetrics() {
    // Heart Rate
    updateElement('heartRate', Math.round(healthData.heartRate));
    updateVitalStatus('heartRate', healthData.heartRate, 60, 100);
    
    // SpO2
    updateElement('spo2', Math.round(healthData.spo2));
    updateSpo2Gauge(healthData.spo2);
    updateVitalStatus('spo2', healthData.spo2, 92, 100);
    
    // Blood Pressure
    const bpText = `${Math.round(healthData.systolic)}/${Math.round(healthData.diastolic)}`;
    updateElement('bloodPressure', bpText);
    updateBPBars();
    updateVitalStatus('bloodPressure', healthData.systolic, 90, 130);
    
    // Temperature
    updateElement('temperature', healthData.temperature.toFixed(1));
    updateTempDial();
    updateVitalStatus('temperature', healthData.temperature, 36.1, 37.2);
    
    // Environmental
    updateElement('altitude', healthData.altitude.toLocaleString());
    updateElement('extTemp', healthData.extTemp);
    updateElement('humidity', healthData.humidity);
    
    // Overall Status
    updateOverallStatus();
    
    // Update data summary widget
    updateDataSummaryWidget();
}

// Efficiently update the data summary widget
function updateDataSummaryWidget() {
    const elements = {
        'quickHR': Math.round(healthData.heartRate).toString(),
        'quickSPO2': Math.round(healthData.spo2).toString(),
        'quickTEMP': healthData.temperature.toFixed(1),
        'quickBP': `${Math.round(healthData.systolic)}/${Math.round(healthData.diastolic)}`
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const elem = document.getElementById(id);
        if (elem && elem.textContent !== value) {
            elem.textContent = value;
        }
    });
    
    // Update snapshot time
    const timeElem = document.getElementById('snapshotTime');
    if (timeElem) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        if (timeElem.textContent !== timeString) {
            timeElem.textContent = timeString;
        }
    }
}

function updateElement(id, value) {
    const elem = document.getElementById(id);
    if (elem) elem.textContent = value;
}

function updateVitalStatus(vitalId, value, min, max) {
    const card = document.getElementById(vitalId)?.closest('.vital-card');
    if (!card) return;
    
    const statusElem = card.querySelector('.vital-status');
    if (!statusElem) return;
    
    let status = 'stable';
    let text = vitalId === 'temperature' ? 'Normal' : 
               vitalId === 'spo2' ? 'Optimal' : 'Normal Range';
    
    if (value < min || value > max) {
        status = 'warning';
        text = 'Caution';
    }
    if (value < min * 0.9 || value > max * 1.1) {
        status = 'critical';
        text = 'Critical';
    }
    
    statusElem.className = `vital-status ${status}`;
    statusElem.textContent = text;
}

function updateSpo2Gauge(value) {
    const gauge = document.getElementById('spo2Gauge');
    const text = document.getElementById('spo2Text');
    if (!gauge || !text) return;
    
    const circumference = 314;
    const offset = circumference - (value / 100) * circumference;
    gauge.style.strokeDashoffset = offset;
    text.textContent = `${Math.round(value)}%`;
}

function updateBPBars() {
    const systolicBar = document.getElementById('systolicBar');
    const diastolicBar = document.getElementById('diastolicBar');
    if (!systolicBar || !diastolicBar) return;
    
    systolicBar.style.height = `${(healthData.systolic / 160) * 100}%`;
    diastolicBar.style.height = `${(healthData.diastolic / 100) * 100}%`;
}

function updateTempDial() {
    const dial = document.getElementById('tempDial');
    if (!dial) return;
    
    const percentage = ((healthData.temperature - 35) / (38 - 35)) * 100;
    dial.style.height = `${Math.min(100, Math.max(0, percentage))}%`;
}

function updateOverallStatus() {
    const statusBadge = document.getElementById('overallStatus');
    if (!statusBadge) return;
    
    let status = 'stable';
    let text = 'STABLE';
    
    if (healthData.spo2 < 92 || healthData.heartRate > 100 || healthData.heartRate < 60) {
        status = 'warning';
        text = 'CAUTION';
    }
    if (healthData.spo2 < 88 || healthData.heartRate > 110 || healthData.heartRate < 50) {
        status = 'critical';
        text = 'CRITICAL';
    }
    
    statusBadge.className = `status-badge ${status}`;
    statusBadge.querySelector('.status-text').textContent = text;
}

function updateCharts() {
    if (charts.hrTrend) {
        charts.hrTrend.data.labels.shift();
        charts.hrTrend.data.labels.push(new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }));
        charts.hrTrend.data.datasets[0].data.shift();
        charts.hrTrend.data.datasets[0].data.push(healthData.heartRate);
        charts.hrTrend.update('none');
    }
    
    if (charts.spo2Trend) {
        charts.spo2Trend.data.labels.shift();
        charts.spo2Trend.data.labels.push(new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }));
        charts.spo2Trend.data.datasets[0].data.shift();
        charts.spo2Trend.data.datasets[0].data.push(healthData.spo2);
        charts.spo2Trend.update('none');
    }
}

console.log('%c Dashboard Active ', 'background: #D4AF37; color: white; padding: 8px; font-weight: bold;');

// ═══════════════════════════════════════════════════
// MANUAL INPUT FUNCTIONS
// ═══════════════════════════════════════════════════

// Sync manual input fields with current health data
function syncManualInputs() {
    const inputs = {
        'manualHeartRate': healthData.heartRate,
        'manualSpo2': healthData.spo2,
        'manualSystolic': healthData.systolic,
        'manualDiastolic': healthData.diastolic,
        'manualTemp': healthData.temperature
    };
    
    Object.entries(inputs).forEach(([id, value]) => {
        const elem = document.getElementById(id);
        if (elem) elem.value = typeof value === 'number' ? value.toFixed(1) : value;
    });
}

// Toggle auto-update mode
function toggleAutoUpdate() {
    autoUpdateEnabled = !autoUpdateEnabled;
    const btnText = document.getElementById('updateModeText');
    
    if (autoUpdateEnabled) {
        btnText.textContent = 'Disable Auto-Update';
        startRealTimeUpdates();
        showNotification('Auto-update enabled', 'success');
    } else {
        btnText.textContent = 'Enable Auto-Update';
        if (updateIntervalId) {
            clearInterval(updateIntervalId);
            updateIntervalId = null;
        }
        showNotification('Manual mode activated', 'info');
    }
}

// Unified vital update function - handles all individual vital updates efficiently
function updateManualVital(dataKey, inputId, minVal, maxVal) {
    const input = document.getElementById(inputId);
    
    // Special handling for blood pressure
    if (dataKey === 'bloodPressure') {
        const sysInput = document.getElementById('manualSystolic');
        const diaInput = document.getElementById('manualDiastolic');
        const systolic = parseFloat(sysInput.value);
        const diastolic = parseFloat(diaInput.value);
        
        const sysValid = validateInput(systolic, 80, 200, sysInput);
        const diaValid = validateInput(diastolic, 50, 120, diaInput);
        
        if (sysValid && diaValid) {
            healthData.systolic = systolic;
            healthData.diastolic = diastolic;
            updateAllMetrics();
            updateCharts();
            showNotification(`Blood Pressure updated to ${Math.round(systolic)}/${Math.round(diastolic)} mmHg`);
        }
        return;
    }
    
    const value = parseFloat(input.value);
    
    if (validateInput(value, minVal, maxVal, input)) {
        healthData[dataKey] = value;
        updateAllMetrics();
        updateCharts();
        
        // Provide appropriate notification based on vital type
        const notifications = {
            'heartRate': `Heart Rate updated to ${Math.round(value)} BPM`,
            'spo2': `SpO2 updated to ${Math.round(value)}%`,
            'temperature': `Temperature updated to ${value.toFixed(1)}°C`
        };
        
        showNotification(notifications[dataKey] || `${dataKey} updated`);
    }
}

// Backward compatibility for legacy update functions
function updateManualHeartRate() { updateManualVital('heartRate', 'manualHeartRate', 40, 200); }
function updateManualSpo2() { updateManualVital('spo2', 'manualSpo2', 70, 100); }
function updateManualBP() { updateManualVital('bloodPressure', 'manualBP', null, null); }
function updateManualTemp() { updateManualVital('temperature', 'manualTemp', 35, 42); }

// Update all values at once
function updateAllManual() {
    const inputs = [
        { id: 'manualHeartRate', key: 'heartRate', min: 40, max: 200 },
        { id: 'manualSpo2', key: 'spo2', min: 70, max: 100 },
        { id: 'manualSystolic', key: 'systolic', min: 80, max: 200 },
        { id: 'manualDiastolic', key: 'diastolic', min: 50, max: 120 },
        { id: 'manualTemp', key: 'temperature', min: 35, max: 42 }
    ];
    
    let allValid = true;
    
    inputs.forEach(input => {
        const elem = document.getElementById(input.id);
        const value = parseFloat(elem.value);
        
        if (validateInput(value, input.min, input.max, elem)) {
            healthData[input.key] = value;
        } else {
            allValid = false;
        }
    });
    
    if (allValid) {
        updateAllMetrics();
        updateCharts();
        showNotification('All vitals updated successfully!');
    } else {
        showNotification('Please check invalid values', 'error');
    }
}

// Reset to default values
function resetToDefaults() {
    healthData = {
        heartRate: 72,
        spo2: 96,
        systolic: 120,
        diastolic: 80,
        temperature: 36.8,
        altitude: 5400,
        extTemp: -15,
        humidity: 42
    };
    
    syncManualInputs();
    updateAllMetrics();
    updateCharts();
    showNotification('Reset to default values');
}

// Validate input value
function validateInput(value, min, max, inputElement) {
    if (isNaN(value) || value < min || value > max) {
        if (inputElement) {
            inputElement.classList.add('invalid');
            inputElement.classList.remove('valid');
            setTimeout(() => {
                inputElement.classList.remove('invalid');
            }, 1000);
        }
        return false;
    }
    
    if (inputElement) {
        inputElement.classList.add('valid');
        inputElement.classList.remove('invalid');
        setTimeout(() => {
            inputElement.classList.remove('valid');
        }, 1000);
    }
    
    return true;
}

// Show notification
function showNotification(message, type = 'success') {
    // Remove existing notification
    const existing = document.querySelector('.update-notification');
    if (existing) existing.remove();
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <span style="margin-right: 0.5rem;">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Enhanced start real-time updates with toggle check
function startRealTimeUpdates() {
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
    }
    
    updateIntervalId = setInterval(() => {
        if (autoUpdateEnabled) {
            simulateDataChanges();
            updateAllMetrics();
            updateCharts();
            syncManualInputs(); // Keep inputs synced in auto mode
        }
    }, 3000);
}

// ═══════════════════════════════════════════════════
// BACKEND ML INTEGRATION
// ═══════════════════════════════════════════════════

/**
 * Check if backend server is available
 */
async function checkBackendAvailability() {
    if (typeof window.backendAPI === 'undefined') {
        console.warn('⚠️ Backend API client not loaded');
        return false;
    }
    
    const isAvailable = await window.backendAPI.checkHealth();
    
    if (isAvailable) {
        console.log('✅ Backend server is available');
        showBackendStatusIndicator(true);
        return true;
    } else {
        console.log('⚠️ Backend server not available - using local simulation');
        showBackendStatusIndicator(false);
        return false;
    }
}

/**
 * Start backend mode - receive data from backend/ML model
 */
function startBackendMode() {
    console.log('🚀 Starting Backend ML Mode');
    
    backendMode = true;
    autoUpdateEnabled = false;
    
    // Stop local simulation
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
    }
    
    // Connect to WebSocket for real-time updates
    window.backendAPI.connectWebSocket(
        handleBackendVitalsUpdate,
        handleBackendConnect,
        handleBackendDisconnect
    );
    
    // Optionally fetch latest data immediately
    fetchLatestFromBackend();
    
    showNotification('Backend ML mode activated', 'success');
}

/**
 * Stop backend mode and return to local simulation
 */
function stopBackendMode() {
    console.log('🛑 Stopping Backend ML Mode');
    
    backendMode = false;
    
    // Disconnect WebSocket
    window.backendAPI.disconnectWebSocket();
    
    // Resume local simulation
    autoUpdateEnabled = true;
    startRealTimeUpdates();
    
    showNotification('Local simulation mode activated', 'info');
}

/**
 * Handle vitals update from backend (via WebSocket)
 */
function handleBackendVitalsUpdate(data) {
    console.log('📊 Processing backend vitals update:', data);
    
    // Update health data from backend
    healthData.heartRate = data.heart_rate || healthData.heartRate;
    healthData.spo2 = data.spo2 || healthData.spo2;
    healthData.systolic = data.systolic || healthData.systolic;
    healthData.diastolic = data.diastolic || healthData.diastolic;
    healthData.temperature = data.temperature || healthData.temperature;
    healthData.altitude = data.altitude || healthData.altitude;
    
    // Display ML analysis results
    if (data.ml_analysis) {
        displayMLAnalysis(data.ml_analysis);
    }
    
    // Update UI
    updateAllMetrics();
    updateCharts();
    syncManualInputs();
}

/**
 * Display ML analysis results on the dashboard
 */
function displayMLAnalysis(mlAnalysis) {
    console.log('🤖 ML Analysis Results:', mlAnalysis);
    
    // Update health score
    const healthScore = mlAnalysis.health_score || 85;
    console.log(`Health Score: ${healthScore}/100`);
    
    // Update risk level
    const riskLevel = mlAnalysis.overall_risk_level || 'low';
    const riskPercentage = mlAnalysis.overall_risk_percentage || 0;
    console.log(`Risk Level: ${riskLevel} (${riskPercentage}%)`);
    
    // Show ML recommendations if critical
    if (mlAnalysis.recommendations && mlAnalysis.recommendations.length > 0) {
        mlAnalysis.recommendations.forEach(rec => {
            if (rec.priority === 'CRITICAL' || rec.priority === 'URGENT') {
                showNotification(`${rec.icon} ${rec.action}`, 'warning');
            }
        });
    }
    
    // You can add more UI elements to display ML results
    // For example, show health score, risk predictions, etc.
}

/**
 * Handle WebSocket connection
 */
function handleBackendConnect() {
    console.log('✅ Connected to backend server');
    showBackendStatusIndicator(true);
    showNotification('Connected to ML backend', 'success');
}

/**
 * Handle WebSocket disconnection
 */
function handleBackendDisconnect() {
    console.log('❌ Disconnected from backend server');
    showBackendStatusIndicator(false);
    showNotification('Disconnected from backend', 'error');
}

/**
 * Fetch latest vitals from backend (REST API)
 */
async function fetchLatestFromBackend() {
    const soldierId = 'SOL-7842-ALPHA';
    const data = await window.backendAPI.getLatestVitals(soldierId);
    
    if (data) {
        handleBackendVitalsUpdate(data);
    }
}

/**
 * Send current vitals to backend for ML processing
 */
async function sendVitalsToBackend() {
    const vitalsData = {
        soldier_id: 'SOL-7842-ALPHA',
        heart_rate: healthData.heartRate,
        spo2: healthData.spo2,
        temperature: healthData.temperature,
        systolic: healthData.systolic,
        diastolic: healthData.diastolic,
        altitude: healthData.altitude,
        timestamp: new Date().toISOString()
    };
    
    const result = await window.backendAPI.sendVitals(vitalsData);
    
    if (result) {
        console.log('✅ Vitals sent to backend and processed by ML');
        handleBackendVitalsUpdate(result);
        return true;
    } else {
        console.error('❌ Failed to send vitals to backend');
        return false;
    }
}

/**
 * Toggle between backend and local mode
 */
function toggleBackendMode() {
    if (backendMode) {
        stopBackendMode();
    } else {
        startBackendMode();
    }
}

/**
 * Show backend connection status indicator
 */
function showBackendStatusIndicator(isConnected) {
    // You can add a visual indicator in the UI
    // For now, just console log
    if (isConnected) {
        console.log('🟢 Backend: Connected');
    } else {
        console.log('🔴 Backend: Disconnected');
    }
}

/**
 * Request backend to simulate data (for testing)
 */
async function triggerBackendSimulation() {
    if (!backendMode) {
        showNotification('Switch to Backend Mode first', 'warning');
        return;
    }
    
    const result = await window.backendAPI.simulateData();
    
    if (result) {
        showNotification('Backend simulation triggered', 'success');
    }
}
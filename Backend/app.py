"""
Elite Health Command - Backend Server
Flask API with ML Model Integration for Wearable Health Data Processing
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify,redirect, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
from datetime import datetime
import sqlite3
import json 
from google_auth_oauthlib.flow import Flow

load_dotenv()
CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")




# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'elite-health-command-secret-key-2026'
CORS(app)  # Enable CORS for frontend communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Import ML model (we'll create this next)
from models.health_predictor import HealthPredictor

# Initialize ML model
ml_model = HealthPredictor()

# Database initialization
from database.db_manager import DatabaseManager
db = DatabaseManager()

# ═══════════════════════════════════════════════════
# REST API ENDPOINTS
# ═══════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'operational',
        'message': 'Elite Health Command API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


@app.route('/api/vitals', methods=['POST'])
def receive_vitals():
    """
    Receive vital signs data from wearable device
    
    Expected JSON format:
    {
        "soldier_id": "SOL-7842-ALPHA",
        "heart_rate": 72,
        "spo2": 96,
        "temperature": 36.8,
        "systolic": 120,
        "diastolic": 80,
        "altitude": 5400,
        "timestamp": "2026-02-04T10:30:00"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['soldier_id', 'heart_rate', 'spo2', 'temperature']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract vitals
        vitals = {
            'soldier_id': data['soldier_id'],
            'heart_rate': float(data['heart_rate']),
            'spo2': float(data['spo2']),
            'temperature': float(data['temperature']),
            'systolic': float(data.get('systolic', 120)),
            'diastolic': float(data.get('diastolic', 80)),
            'altitude': float(data.get('altitude', 0)),
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
        
        # Process with ML model
        ml_results = ml_model.predict(vitals)
        
        # Combine original data with ML predictions
        response_data = {
            **vitals,
            'ml_analysis': ml_results,
            'processed_at': datetime.now().isoformat()
        }
        
        # Store in database
        db.store_vitals(response_data)
        
        # Broadcast to connected frontend clients via WebSocket
        socketio.emit('vitals_update', response_data, broadcast=True)
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Vitals processed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vitals/latest/<soldier_id>', methods=['GET'])
def get_latest_vitals(soldier_id):
    """Get latest vitals for a specific soldier"""
    try:
        vitals = db.get_latest_vitals(soldier_id)
        
        if vitals:
            return jsonify({
                'success': True,
                'data': vitals
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No data found for this soldier'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vitals/history/<soldier_id>', methods=['GET'])
def get_vitals_history(soldier_id):
    """Get historical vitals for a specific soldier"""
    try:
        # Get optional query parameters
        limit = request.args.get('limit', 100, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        history = db.get_vitals_history(soldier_id, limit=limit, hours=hours)
        
        return jsonify({
            'success': True,
            'count': len(history),
            'data': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/predict/risk', methods=['POST'])
def predict_risk():
    """
    Predict health risks using ML model
    
    Expected JSON format:
    {
        "heart_rate": 72,
        "spo2": 96,
        "temperature": 36.8,
        "systolic": 120,
        "diastolic": 80,
        "altitude": 5400
    }
    """
    try:
        data = request.get_json()
        
        # Run ML prediction
        prediction = ml_model.predict_risk_level(data)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/<soldier_id>', methods=['GET'])
def get_alerts(soldier_id):
    """Get active alerts for a soldier"""
    try:
        alerts = db.get_active_alerts(soldier_id)
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': alerts
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════
# WEBSOCKET EVENTS
# ═══════════════════════════════════════════════════

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to Elite Health Command server',
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('request_vitals')
def handle_vitals_request(data):
    """Handle real-time vitals data request"""
    soldier_id = data.get('soldier_id', 'SOL-7842-ALPHA')
    vitals = db.get_latest_vitals(soldier_id)
    
    if vitals:
        emit('vitals_data', vitals)
    else:
        emit('error', {'message': 'No data available'})


# ═══════════════════════════════════════════════════
# SIMULATION ENDPOINT (For Testing)
# ═══════════════════════════════════════════════════

@app.route('/api/simulate', methods=['POST'])
def simulate_data():
    """
    Simulate wearable device sending data (for testing)
    Generates random but realistic vital signs
    """
    try:
        import random
        
        # Generate realistic random vitals
        simulated_data = {
            'soldier_id': 'SOL-7842-ALPHA',
            'heart_rate': random.randint(60, 100),
            'spo2': random.randint(92, 99),
            'temperature': round(random.uniform(36.1, 37.2), 1),
            'systolic': random.randint(110, 130),
            'diastolic': random.randint(70, 85),
            'altitude': 5400,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process through the same pipeline
        ml_results = ml_model.predict(simulated_data)
        
        response_data = {
            **simulated_data,
            'ml_analysis': ml_results,
            'processed_at': datetime.now().isoformat()
        }
        
        # Store and broadcast
        db.store_vitals(response_data)
        socketio.emit('vitals_update', response_data, broadcast=True)
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Simulated data processed'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


SCOPES = [
    "https://www.googleapis.com/auth/fitness.heart_rate.read",
    "https://www.googleapis.com/auth/fitness.activity.read"
]

@app.route("/google/login")
def google_login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )

    flow.redirect_uri = "http://localhost:5000/google/callback"

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    session["state"] = state
    return redirect(authorization_url)

@app.route("/google/callback")
def google_callback():
    state = session["state"]

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state,
    )

    flow.redirect_uri = "http://localhost:5000/google/callback"
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
    }

    return redirect("http://localhost:your_frontend_port/dashboard.html")

import requests
import time

@app.route("/google/heart")
def get_heart_data():
    credentials = session.get("credentials")
    if not credentials:
        return jsonify({"error": "User not logged in"}), 401

    access_token = credentials["token"]

    end_time = int(time.time() * 1000)
    start_time = end_time - 3600000  # last 1 hour

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

    body = {
        "aggregateBy": [{
            "dataTypeName": "com.google.heart_rate.bpm"
        }],
        "bucketByTime": { "durationMillis": 60000 },
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, json=body, headers=headers)

    return jsonify(response.json())


# ═══════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("🎖️  ELITE HEALTH COMMAND - Backend Server")
    print("=" * 60)
    print(f"✅ ML Model: Loaded")
    print(f"✅ Database: Initialized")
    print(f"✅ Server: Starting on http://localhost:5000")
    print(f"✅ WebSocket: Enabled")
    print("=" * 60)
    
    # Run server
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )
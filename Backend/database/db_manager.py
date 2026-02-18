"""
Database Manager for Elite Health Command
Handles storage and retrieval of vital signs and health data
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os


class DatabaseManager:
    """Manages SQLite database for health monitoring data"""
    
    def __init__(self, db_path='database/health_data.db'):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
        self._create_tables()
        print(f"✅ Database initialized: {db_path}")
    
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        
        # Vitals table - stores all vital signs data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soldier_id TEXT NOT NULL,
                heart_rate REAL,
                spo2 REAL,
                temperature REAL,
                systolic REAL,
                diastolic REAL,
                altitude REAL,
                health_score REAL,
                risk_level TEXT,
                risk_percentage REAL,
                ml_analysis TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Alerts table - stores generated alerts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soldier_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT,
                vitals_snapshot TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create indexes for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_soldier_timestamp 
            ON vitals(soldier_id, timestamp DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alerts_soldier 
            ON alerts(soldier_id, created_at DESC)
        ''')
        
        self.conn.commit()
    
    
    def store_vitals(self, data):
        """
        Store vital signs data with ML analysis results
        
        Args:
            data (dict): Complete vitals data with ML analysis
        """
        try:
            ml_analysis = data.get('ml_analysis', {})
            
            self.cursor.execute('''
                INSERT INTO vitals (
                    soldier_id, heart_rate, spo2, temperature,
                    systolic, diastolic, altitude,
                    health_score, risk_level, risk_percentage,
                    ml_analysis, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('soldier_id'),
                data.get('heart_rate'),
                data.get('spo2'),
                data.get('temperature'),
                data.get('systolic'),
                data.get('diastolic'),
                data.get('altitude'),
                ml_analysis.get('health_score'),
                ml_analysis.get('overall_risk_level'),
                ml_analysis.get('overall_risk_percentage'),
                json.dumps(ml_analysis),
                data.get('timestamp'),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            
            # Check if alert should be generated
            self._check_and_create_alert(data, ml_analysis)
            
            return True
            
        except Exception as e:
            print(f"Error storing vitals: {e}")
            self.conn.rollback()
            return False
    
    
    def get_latest_vitals(self, soldier_id):
        """Get the most recent vitals for a soldier"""
        try:
            self.cursor.execute('''
                SELECT * FROM vitals
                WHERE soldier_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (soldier_id,))
            
            row = self.cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
            
        except Exception as e:
            print(f"Error getting latest vitals: {e}")
            return None
    
    
    def get_vitals_history(self, soldier_id, limit=100, hours=24):
        """
        Get historical vitals for a soldier
        
        Args:
            soldier_id (str): Soldier ID
            limit (int): Maximum number of records to return
            hours (int): Number of hours to look back
        """
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            self.cursor.execute('''
                SELECT * FROM vitals
                WHERE soldier_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (soldier_id, cutoff_time, limit))
            
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error getting vitals history: {e}")
            return []
    
    
    def _check_and_create_alert(self, data, ml_analysis):
        """Check if vitals warrant an alert and create it"""
        risk_level = ml_analysis.get('overall_risk_level', 'low')
        
        # Only create alerts for high or critical risk
        if risk_level in ['high', 'critical']:
            
            # Check if similar alert already exists in last 10 minutes
            ten_min_ago = (datetime.now() - timedelta(minutes=10)).isoformat()
            
            self.cursor.execute('''
                SELECT COUNT(*) FROM alerts
                WHERE soldier_id = ? 
                AND severity = ?
                AND acknowledged = 0
                AND created_at >= ?
            ''', (data.get('soldier_id'), risk_level, ten_min_ago))
            
            existing_count = self.cursor.fetchone()[0]
            
            # Don't create duplicate alerts
            if existing_count > 0:
                return
            
            # Get top risk
            recommendations = ml_analysis.get('recommendations', [])
            message = recommendations[0]['action'] if recommendations else 'Health risk detected'
            
            self.cursor.execute('''
                INSERT INTO alerts (
                    soldier_id, alert_type, severity, message,
                    vitals_snapshot, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('soldier_id'),
                'HEALTH_RISK',
                risk_level,
                message,
                json.dumps({
                    'heart_rate': data.get('heart_rate'),
                    'spo2': data.get('spo2'),
                    'temperature': data.get('temperature'),
                    'risk_percentage': ml_analysis.get('overall_risk_percentage')
                }),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
    
    
    def get_active_alerts(self, soldier_id):
        """Get unacknowledged alerts for a soldier"""
        try:
            self.cursor.execute('''
                SELECT * FROM alerts
                WHERE soldier_id = ? AND acknowledged = 0
                ORDER BY created_at DESC
            ''', (soldier_id,))
            
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    
    def acknowledge_alert(self, alert_id):
        """Mark an alert as acknowledged"""
        try:
            self.cursor.execute('''
                UPDATE alerts
                SET acknowledged = 1, acknowledged_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), alert_id))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error acknowledging alert: {e}")
            return False
    
    
    def get_statistics(self, soldier_id, hours=24):
        """Get statistical summary of vitals"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as record_count,
                    AVG(heart_rate) as avg_heart_rate,
                    MIN(heart_rate) as min_heart_rate,
                    MAX(heart_rate) as max_heart_rate,
                    AVG(spo2) as avg_spo2,
                    MIN(spo2) as min_spo2,
                    AVG(temperature) as avg_temperature,
                    AVG(health_score) as avg_health_score
                FROM vitals
                WHERE soldier_id = ? AND timestamp >= ?
            ''', (soldier_id, cutoff_time))
            
            row = self.cursor.fetchone()
            return self._row_to_dict(row) if row else {}
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    
    def _row_to_dict(self, row):
        """Convert SQLite Row to dictionary"""
        if not row:
            return None
            
        result = dict(row)
        
        # Parse JSON fields
        if 'ml_analysis' in result and result['ml_analysis']:
            try:
                result['ml_analysis'] = json.loads(result['ml_analysis'])
            except:
                pass
        
        if 'vitals_snapshot' in result and result['vitals_snapshot']:
            try:
                result['vitals_snapshot'] = json.loads(result['vitals_snapshot'])
            except:
                pass
        
        return result
    
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("Database connection closed")


# ═══════════════════════════════════════════════════
# STANDALONE TESTING
# ═══════════════════════════════════════════════════

if __name__ == '__main__':
    # Test database
    db = DatabaseManager('test_health_data.db')
    
    # Test data
    test_data = {
        'soldier_id': 'SOL-7842-ALPHA',
        'heart_rate': 72,
        'spo2': 96,
        'temperature': 36.8,
        'systolic': 120,
        'diastolic': 80,
        'altitude': 5400,
        'timestamp': datetime.now().isoformat(),
        'ml_analysis': {
            'health_score': 85.5,
            'overall_risk_level': 'low',
            'overall_risk_percentage': 15.2,
            'recommendations': []
        }
    }
    
    # Store vitals
    print("Storing test vitals...")
    db.store_vitals(test_data)
    
    # Retrieve latest
    print("\nRetrieving latest vitals...")
    latest = db.get_latest_vitals('SOL-7842-ALPHA')
    print(json.dumps(latest, indent=2))
    
    # Get statistics
    print("\nGetting statistics...")
    stats = db.get_statistics('SOL-7842-ALPHA')
    print(json.dumps(stats, indent=2))
    
    db.close()
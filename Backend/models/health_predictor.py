"""
Health Predictor ML Model
Analyzes vital signs and predicts health risks for soldiers in high-altitude environments
"""

import numpy as np
import json
from datetime import datetime
from models.health_predictor import predict_health


class HealthPredictor:
    """
    ML Model for Health Risk Prediction
    
    This is a rule-based model that simulates ML predictions.
    In production, you would replace this with:
    - TensorFlow/Keras trained model
    - PyTorch model
    - scikit-learn model
    - Pre-trained neural network
    """
    
    
    def __init__(self):
        """Initialize the model with thresholds and weights"""
        self.model_version = "1.0.0"
        self.initialized_at = datetime.now().isoformat()
        
        # Normal ranges for vital signs
        self.thresholds = {
            'heart_rate': {'min': 60, 'max': 100, 'critical_low': 50, 'critical_high': 120},
            'spo2': {'min': 92, 'max': 100, 'critical_low': 88, 'critical_high': 100},
            'temperature': {'min': 36.1, 'max': 37.2, 'critical_low': 35.5, 'critical_high': 38.0},
            'systolic': {'min': 90, 'max': 130, 'critical_low': 80, 'critical_high': 150},
            'diastolic': {'min': 60, 'max': 85, 'critical_low': 50, 'critical_high': 95},
        }
        
        # Altitude impact factors
        self.altitude_factors = {
            0: 1.0,      # Sea level
            1000: 1.05,  # Low altitude
            2500: 1.15,  # Moderate altitude
            4000: 1.30,  # High altitude
            5500: 1.50,  # Very high altitude
            7000: 1.75,  # Extreme altitude
        }
        
        print(f"✅ HealthPredictor ML Model initialized (v{self.model_version})")
    
    def predict(self, vitals):
        """
        Main prediction function - processes vital signs and returns comprehensive analysis
        
        Args:
            vitals (dict): Dictionary containing vital signs data
            
        Returns:
            dict: ML analysis results including risk levels, predictions, and recommendations
        """
        
        # Extract vitals
        heart_rate = vitals.get('heart_rate', 72)
        spo2 = vitals.get('spo2', 96)
        temperature = vitals.get('temperature', 36.8)
        systolic = vitals.get('systolic', 120)
        diastolic = vitals.get('diastolic', 80)
        altitude = vitals.get('altitude', 0)
        
        # Calculate health status for each vital
        hr_status = self._assess_vital('heart_rate', heart_rate)
        spo2_status = self._assess_vital('spo2', spo2)
        temp_status = self._assess_vital('temperature', temperature)
        bp_status = self._assess_blood_pressure(systolic, diastolic)
        
        # Calculate overall health score (0-100)
        health_score = self._calculate_health_score(
            hr_status, spo2_status, temp_status, bp_status
        )
        
        # Predict specific risks
        hypoxia_risk = self._predict_hypoxia_risk(spo2, altitude, heart_rate)
        altitude_sickness_risk = self._predict_altitude_sickness(altitude, spo2, heart_rate)
        cardiac_stress_risk = self._predict_cardiac_stress(heart_rate, systolic, diastolic)
        hypothermia_risk = self._predict_hypothermia(temperature, altitude)
        
        # Determine overall risk level
        overall_risk = self._determine_overall_risk(
            hypoxia_risk, altitude_sickness_risk, cardiac_stress_risk, hypothermia_risk
        )
        
        # Generate medical recommendations
        recommendations = self._generate_recommendations(
            overall_risk, hr_status, spo2_status, temp_status, bp_status
        )
        
        # Predict health trend (improving/stable/deteriorating)
        trend = self._predict_trend(health_score)
        
        # Compile efficient results structure
        results = {
            'health_score': round(health_score, 1),
            'overall_risk_level': overall_risk['level'],
            'overall_risk_percentage': overall_risk['percentage'],
            'vital_assessments': {
                'heart_rate': hr_status,
                'spo2': spo2_status,
                'temperature': temp_status,
                'blood_pressure': bp_status
            },
            'risk_predictions': {
                'hypoxia': hypoxia_risk,
                'altitude_sickness': altitude_sickness_risk,
                'cardiac_stress': cardiac_stress_risk,
                'hypothermia': hypothermia_risk
            },
            'recommendations': recommendations,
            'health_trend': trend,
            'altitude_adjustment': self._get_altitude_factor(altitude),
            'predicted_at': datetime.now().isoformat(),
            'model_version': self.model_version
        }
        
        return results
    
    
    def predict_risk_level(self, vitals):
        """
        Simplified prediction - returns just the risk level
        Useful for quick assessments
        """
        full_prediction = self.predict(vitals)
        
        return {
            'risk_level': full_prediction['overall_risk_level'],
            'risk_percentage': full_prediction['overall_risk_percentage'],
            'health_score': full_prediction['health_score'],
            'top_risks': self._get_top_risks(full_prediction['risk_predictions'])
        }
    
    
    # ═══════════════════════════════════════════════════
    # PRIVATE HELPER METHODS
    # ═══════════════════════════════════════════════════
    
    def _assess_vital(self, vital_name, value):
        """Assess a single vital sign against thresholds"""
        thresholds = self.thresholds[vital_name]
        
        status = 'normal'
        severity = 0
        
        if value < thresholds['critical_low'] or value > thresholds['critical_high']:
            status = 'critical'
            severity = 2
        elif value < thresholds['min'] or value > thresholds['max']:
            status = 'warning'
            severity = 1
        
        return {
            'value': value,
            'status': status,
            'severity': severity,
            'in_range': status == 'normal'
        }
    
    
    def _assess_blood_pressure(self, systolic, diastolic):
        """Assess blood pressure (both systolic and diastolic)"""
        sys_status = self._assess_vital('systolic', systolic)
        dia_status = self._assess_vital('diastolic', diastolic)
        
        # Overall BP status is the worse of the two
        overall_status = 'critical' if (sys_status['status'] == 'critical' or dia_status['status'] == 'critical') else \
                        'warning' if (sys_status['status'] == 'warning' or dia_status['status'] == 'warning') else \
                        'normal'
        
        return {
            'systolic': sys_status['value'],
            'diastolic': dia_status['value'],
            'status': overall_status,
            'severity': max(sys_status['severity'], dia_status['severity']),
            'in_range': sys_status['in_range'] and dia_status['in_range']
        }
    
    
    def _calculate_health_score(self, hr_status, spo2_status, temp_status, bp_status):
        """Calculate overall health score (0-100)"""
        score = 100
        
        # Deduct points for abnormal vitals
        score -= hr_status['severity'] * 15
        score -= spo2_status['severity'] * 20  # SpO2 is critical
        score -= temp_status['severity'] * 10
        score -= bp_status['severity'] * 15
        
        return max(0, min(100, score))
    
    
    def _predict_hypoxia_risk(self, spo2, altitude, heart_rate):
        """Predict risk of hypoxia based on oxygen saturation and altitude"""
        risk_score = 0
        
        # SpO2 contribution (60% weight)
        if spo2 < 88:
            risk_score += 60
        elif spo2 < 92:
            risk_score += 30
        elif spo2 < 95:
            risk_score += 10
        
        # Altitude contribution (30% weight)
        altitude_factor = self._get_altitude_factor(altitude)
        risk_score += (altitude_factor - 1.0) * 30
        
        # Heart rate contribution (10% weight) - compensatory tachycardia
        if heart_rate > 100:
            risk_score += 10
        
        risk_score = min(100, risk_score)
        
        return {
            'percentage': round(risk_score, 1),
            'level': 'high' if risk_score > 60 else 'moderate' if risk_score > 30 else 'low',
            'confidence': 0.85
        }
    
    
    def _predict_altitude_sickness(self, altitude, spo2, heart_rate):
        """Predict risk of acute mountain sickness (AMS)"""
        risk_score = 0
        
        # Altitude is the primary factor
        if altitude > 5500:
            risk_score += 50
        elif altitude > 4000:
            risk_score += 30
        elif altitude > 2500:
            risk_score += 10
        
        # Low SpO2 increases risk
        if spo2 < 90:
            risk_score += 30
        elif spo2 < 94:
            risk_score += 15
        
        # Elevated heart rate (compensatory)
        if heart_rate > 110:
            risk_score += 20
        elif heart_rate > 95:
            risk_score += 10
        
        risk_score = min(100, risk_score)
        
        return {
            'percentage': round(risk_score, 1),
            'level': 'high' if risk_score > 60 else 'moderate' if risk_score > 30 else 'low',
            'confidence': 0.80
        }
    
    
    def _predict_cardiac_stress(self, heart_rate, systolic, diastolic):
        """Predict cardiac stress level"""
        risk_score = 0
        
        # Heart rate contribution
        if heart_rate > 120:
            risk_score += 40
        elif heart_rate > 100:
            risk_score += 20
        elif heart_rate < 50:
            risk_score += 30  # Bradycardia
        
        # Blood pressure contribution
        if systolic > 140 or diastolic > 90:
            risk_score += 30
        elif systolic > 130 or diastolic > 85:
            risk_score += 15
        
        # Hypotension
        if systolic < 90 or diastolic < 60:
            risk_score += 30
        
        risk_score = min(100, risk_score)
        
        return {
            'percentage': round(risk_score, 1),
            'level': 'high' if risk_score > 60 else 'moderate' if risk_score > 30 else 'low',
            'confidence': 0.78
        }
    
    
    def _predict_hypothermia(self, temperature, altitude):
        """Predict hypothermia risk"""
        risk_score = 0
        
        # Temperature is primary factor
        if temperature < 35:
            risk_score += 70
        elif temperature < 35.5:
            risk_score += 40
        elif temperature < 36:
            risk_score += 20
        
        # Altitude increases exposure risk
        if altitude > 5000:
            risk_score += 15
        elif altitude > 3000:
            risk_score += 5
        
        risk_score = min(100, risk_score)
        
        return {
            'percentage': round(risk_score, 1),
            'level': 'high' if risk_score > 60 else 'moderate' if risk_score > 30 else 'low',
            'confidence': 0.82
        }
    
    
    def _determine_overall_risk(self, hypoxia, altitude_sickness, cardiac, hypothermia):
        """Determine overall risk level from individual risk predictions"""
        # Get highest risk percentage
        max_risk = max(
            hypoxia['percentage'],
            altitude_sickness['percentage'],
            cardiac['percentage'],
            hypothermia['percentage']
        )
        
        # Average of all risks
        avg_risk = (
            hypoxia['percentage'] +
            altitude_sickness['percentage'] +
            cardiac['percentage'] +
            hypothermia['percentage']
        ) / 4
        
        # Weighted combination (60% max, 40% average)
        overall = max_risk * 0.6 + avg_risk * 0.4
        
        level = 'critical' if overall > 70 else \
                'high' if overall > 50 else \
                'moderate' if overall > 30 else \
                'low'
        
        return {
            'percentage': round(overall, 1),
            'level': level
        }
    
    
    def _generate_recommendations(self, overall_risk, hr_status, spo2_status, temp_status, bp_status):
        """Generate medical recommendations based on vital assessments"""
        recommendations = []
        
        # Critical recommendations
        if overall_risk['level'] == 'critical':
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediate medical evacuation required',
                'icon': '🚨'
            })
        
        # SpO2 recommendations
        if spo2_status['status'] == 'critical':
            recommendations.append({
                'priority': 'URGENT',
                'action': 'Administer supplemental oxygen immediately',
                'icon': '💨'
            })
        elif spo2_status['status'] == 'warning':
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Monitor oxygen saturation closely, consider oxygen therapy',
                'icon': '⚠️'
            })
        
        # Heart rate recommendations
        if hr_status['status'] == 'critical':
            recommendations.append({
                'priority': 'URGENT',
                'action': 'Cardiac assessment required - possible arrhythmia',
                'icon': '♥️'
            })
        
        # Temperature recommendations
        if temp_status['status'] == 'critical':
            if temp_status['value'] < 35.5:
                recommendations.append({
                    'priority': 'URGENT',
                    'action': 'Hypothermia treatment - warm gradually, avoid extremes',
                    'icon': '🌡️'
                })
            else:
                recommendations.append({
                    'priority': 'URGENT',
                    'action': 'Hyperthermia treatment - cool down, hydrate',
                    'icon': '🌡️'
                })
        
        # Blood pressure recommendations
        if bp_status['status'] == 'critical':
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Blood pressure management required',
                'icon': '⚡'
            })
        
        # General recommendations
        if overall_risk['level'] in ['low', 'moderate'] and len(recommendations) == 0:
            recommendations.append({
                'priority': 'ROUTINE',
                'action': 'Continue standard monitoring protocol',
                'icon': '✓'
            })
        
        return recommendations
    
    
    def _predict_trend(self, health_score):
        """Predict health trend direction"""
        # This would use historical data in production
        # For now, use score to determine likely trend
        
        if health_score >= 85:
            return 'stable'
        elif health_score >= 70:
            return 'monitor'
        else:
            return 'deteriorating'
    
    
    def _get_altitude_factor(self, altitude):
        """Get altitude adjustment factor"""
        for alt, factor in sorted(self.altitude_factors.items(), reverse=True):
            if altitude >= alt:
                return factor
        return 1.0
    
    
    def _get_top_risks(self, risk_predictions):
        """Get top 3 risks by percentage"""
        risks = [
            {'name': 'Hypoxia', **risk_predictions['hypoxia']},
            {'name': 'Altitude Sickness', **risk_predictions['altitude_sickness']},
            {'name': 'Cardiac Stress', **risk_predictions['cardiac_stress']},
            {'name': 'Hypothermia', **risk_predictions['hypothermia']}
        ]
        
        # Sort by percentage
        risks.sort(key=lambda x: x['percentage'], reverse=True)
        
        return risks[:3]


# ═══════════════════════════════════════════════════
# STANDALONE TESTING
# ═══════════════════════════════════════════════════

if __name__ == '__main__':
    # Test the model
    model = HealthPredictor()
    
    # Test case 1: Normal vitals
    print("\n" + "="*60)
    print("TEST 1: Normal Vitals at High Altitude")
    print("="*60)
    test_vitals_1 = {
        'heart_rate': 72,
        'spo2': 96,
        'temperature': 36.8,
        'systolic': 120,
        'diastolic': 80,
        'altitude': 5400
    }
    result_1 = model.predict(test_vitals_1)
    print(json.dumps(result_1, indent=2))
    
    # Test case 2: Critical hypoxia
    print("\n" + "="*60)
    print("TEST 2: Critical Hypoxia")
    print("="*60)
    test_vitals_2 = {
        'heart_rate': 115,
        'spo2': 82,
        'temperature': 36.5,
        'systolic': 140,
        'diastolic': 90,
        'altitude': 6200
    }
    result_2 = model.predict(test_vitals_2)
    print(json.dumps(result_2, indent=2))
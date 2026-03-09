from sklearn.ensemble import IsolationForest
import numpy as np

class FraudDetector:
    def __init__(self):
        # Isolation Forest for anomaly detection
        self.model = IsolationForest(contamination=0.1, random_state=42)
        
        # Train with normal operational data representing valid claims:
        # Features: [disruption_duration_hours, payout_amount, gps_movement_score]
        # Context: A very high gps_movement_score during a disruption means they might still be delivering orders!
        X_train = np.array([
            [4, 400, 2], [2, 250, 1], [5, 600, 3], 
            [3, 350, 2], [6, 750, 1], [1, 120, 0]
        ])
        self.model.fit(X_train)

    def detect_fraud(self, duration, payout, gps_movement):
        """
        Detect suspicious claims.
        Returns True if fraudulent (anomalous), False otherwise.
        """
        X_test = np.array([[duration, payout, gps_movement]])
        prediction = self.model.predict(X_test)[0]
        
        # Prediction is -1 for anomalies, 1 for normal
        return bool(prediction == -1)

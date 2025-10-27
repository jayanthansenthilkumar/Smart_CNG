from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime

class WaitTimePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'active_chargers',
            'total_chargers',
            'current_queue_length',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'traffic_density',
            'historical_avg_wait_time'
        ]
        
    def _prepare_features(self, station_data):
        """Convert station data into feature matrix"""
        features = []
        for station in station_data:
            feature_vector = [
                station['active_chargers'],
                station['total_chargers'],
                station['current_queue_length'],
                station['hour_of_day'],
                station['day_of_week'],
                station['is_weekend'],
                station['traffic_density'],
                station['historical_avg_wait_time']
            ]
            features.append(feature_vector)
        return np.array(features)

    def train(self, training_data, wait_times):
        """Train the model with historical data"""
        X = self._prepare_features(training_data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, wait_times)
        self.is_trained = True

    def train_from_csv(self, file_path: str):
        """Train model from a CSV file with flexible column names."""
        try:
            df = pd.read_csv(file_path)
        except Exception:
            df = pd.read_excel(file_path)

        # Normalize columns
        cols = {str(c).strip().lower(): c for c in df.columns}

        def get_col(*candidates, default=None):
            for cand in candidates:
                if cand in cols:
                    return cols[cand]
            return default

        # Map required feature columns with defaults if missing
        mapping = {
            'active_chargers': get_col('active_chargers', 'active_pumps', 'available_pumps', default=None),
            'total_chargers': get_col('total_chargers', 'total_pumps', 'pumps', default=None),
            'current_queue_length': get_col('current_queue_length', 'queue', 'queue_length', default=None),
            'hour_of_day': get_col('hour_of_day', 'hour', default=None),
            'day_of_week': get_col('day_of_week', 'dow', default=None),
            'is_weekend': get_col('is_weekend', default=None),
            'traffic_density': get_col('traffic_density', 'traffic', default=None),
            'historical_avg_wait_time': get_col('historical_avg_wait_time', 'avg_wait', 'avg_wait_time', default=None),
        }

        target_col = get_col('wait_time', 'waiting_time', 'target')
        if target_col is None:
            raise ValueError('Target wait time column not found in training CSV')

        # Build training dict list
        records = []
        waits = []
        for _, row in df.iterrows():
            record = {}
            for f, src in mapping.items():
                val = row[src] if src is not None and src in df.columns else None
                if pd.isna(val):
                    val = None
                record[f] = float(val) if val is not None else 0.0
            records.append(record)
            waits.append(float(row[target_col]))

        self.train(records, waits)
        return True

    def predict_wait_time(self, station_data):
        """Predict waiting times for stations"""
        if not self.is_trained:
            # If model isn't trained, use a simple heuristic
            return self._heuristic_prediction(station_data)
        
        X = self._prepare_features(station_data)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return [{
            'station_id': station['id'],
            'predicted_wait': max(0, pred),  # Ensure non-negative wait times
            'confidence': self._calculate_confidence(station)
        } for station, pred in zip(station_data, predictions)]

    def _heuristic_prediction(self, station_data):
        """Simple heuristic for wait time prediction when model isn't trained"""
        predictions = []
        for station in station_data:
            # Basic calculation based on queue length and available chargers
            if station['active_chargers'] == 0:
                wait_time = station['historical_avg_wait_time']
            else:
                wait_time = (station['current_queue_length'] * 20) / station['active_chargers']
                # Adjust based on historical average
                wait_time = (wait_time + station['historical_avg_wait_time']) / 2
            
            predictions.append({
                'station_id': station['id'],
                'predicted_wait': max(0, wait_time),
                'confidence': 0.6  # Lower confidence for heuristic prediction
            })
        return predictions

    def _calculate_confidence(self, station):
        """Calculate confidence score for the prediction"""
        # Factors affecting confidence
        factors = {
            'data_quality': min(1.0, station.get('data_completeness', 0.8)),
            'traffic_certainty': min(1.0, 1 - abs(0.5 - station['traffic_density'])),
            'queue_stability': min(1.0, 1 / (1 + station['current_queue_length'] * 0.1)),
            'charger_reliability': min(1.0, station['active_chargers'] / station['total_chargers'])
        }
        
        # Weighted average of factors
        weights = {
            'data_quality': 0.4,
            'traffic_certainty': 0.2,
            'queue_stability': 0.2,
            'charger_reliability': 0.2
        }
        
        confidence = sum(factor * weights[name] for name, factor in factors.items())
        return min(1.0, max(0.0, confidence)) 
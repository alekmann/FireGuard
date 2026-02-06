"""
Fire Risk Service - Clean wrapper around the FRCM computation module.

This service provides a clean interface to the fire risk computation functionality
without requiring sys.path manipulation or complex imports.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any


def _ensure_frcm_available():
    """Lazy loading of FRCM modules - only import when needed."""
    global WeatherData, WeatherDataPoint, FireRisk, FireRiskPrediction, compute
    
    # Check if already imported
    if 'WeatherData' in globals():
        return
    
    # Add the FRCM source to path
    frcm_path = Path(__file__).parent.parent / "fire_risk_computation" / "src"
    if str(frcm_path) not in sys.path:
        sys.path.insert(0, str(frcm_path))
    
    # Now import safely
    from frcm.datamodel.model import WeatherData, WeatherDataPoint, FireRisk, FireRiskPrediction
    from frcm.fireriskmodel.compute import compute
    
    # Make them global for this module
    globals()['WeatherData'] = WeatherData
    globals()['WeatherDataPoint'] = WeatherDataPoint  
    globals()['FireRisk'] = FireRisk
    globals()['FireRiskPrediction'] = FireRiskPrediction
    globals()['compute'] = compute


class FireRiskService:
    """Service for computing fire risk from weather data."""
    
    @staticmethod
    def load_weather_data_from_csv(csv_path: Path):
        """Load weather data from CSV file."""
        _ensure_frcm_available()
        return WeatherData.read_csv(csv_path)
    
    @staticmethod
    def compute_fire_risk(weather_data):
        """Compute fire risk prediction from weather data."""
        _ensure_frcm_available()
        return compute(weather_data)
    
    @staticmethod
    def get_sample_data_path() -> Path:
        """Get path to the Bergen sample data file."""
        return Path(__file__).parent.parent / "fire_risk_computation" / "bergen_2026_01_09.csv"
    
    @classmethod
    def compute_from_csv(cls, csv_path: Path):
        """Convenience method: load CSV and compute fire risk in one call."""
        weather_data = cls.load_weather_data_from_csv(csv_path)
        return cls.compute_fire_risk(weather_data)
    
    @classmethod
    def compute_sample_data(cls):
        """Compute fire risk using the Bergen sample data."""
        sample_path = cls.get_sample_data_path()
        return cls.compute_from_csv(sample_path)


# Convenience functions for direct usage
def compute_fire_risk_from_csv(csv_path: Path):
    """Compute fire risk directly from CSV file."""
    return FireRiskService.compute_from_csv(csv_path)


def get_bergen_sample_prediction():
    """Get fire risk prediction using Bergen sample data."""
    return FireRiskService.compute_sample_data()
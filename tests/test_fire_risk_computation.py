from pathlib import Path
from app.services.fire_risk_service import (
    FireRiskService, 
    compute_fire_risk_from_csv,
    get_bergen_sample_prediction
)


def test_csv_file_exists():
    """Test that the Bergen CSV file exists and is readable."""
    bergen_csv_file = FireRiskService.get_sample_data_path()
    assert bergen_csv_file.exists(), f"Bergen CSV file not found at {bergen_csv_file}"
    assert bergen_csv_file.is_file(), "Path exists but is not a file"


def test_weather_data_loading():
    """Test that weather data can be loaded from CSV correctly."""
    bergen_csv_file = FireRiskService.get_sample_data_path()
    weather_data = FireRiskService.load_weather_data_from_csv(bergen_csv_file)
    
    assert weather_data is not None
    assert len(weather_data.data) > 0, "Weather data should not be empty"
    
    # Check first data point structure
    first_point = weather_data.data[0]
    assert hasattr(first_point, 'temperature')
    assert hasattr(first_point, 'humidity') 
    assert hasattr(first_point, 'wind_speed')
    assert hasattr(first_point, 'timestamp')


def test_fire_risk_computation():
    """Test the core fire risk computation using Bergen data."""
    # Use the convenience function
    fire_risk_prediction = get_bergen_sample_prediction()
    
    # Verify the result structure
    assert fire_risk_prediction is not None
    assert hasattr(fire_risk_prediction, 'firerisks')
    assert len(fire_risk_prediction.firerisks) > 0
    
    # Check first fire risk result
    first_risk = fire_risk_prediction.firerisks[0]
    assert hasattr(first_risk, 'timestamp')
    assert hasattr(first_risk, 'ttf')
    assert first_risk.ttf > 0, "Time to flashover should be positive"


def test_fire_risk_values_reasonable():
    """Test that computed fire risk values are within reasonable bounds."""
    fire_risk_prediction = get_bergen_sample_prediction()
    
    ttf_values = [risk.ttf for risk in fire_risk_prediction.firerisks]
    
    # TTF should be positive
    assert all(ttf > 0 for ttf in ttf_values), "All TTF values should be positive"
    
    # TTF should be reasonable (typically between 1-50 hours for wooden structures)  
    assert all(ttf < 100 for ttf in ttf_values), "TTF values seem unreasonably high"
    assert all(ttf > 0.01 for ttf in ttf_values), "TTF values seem unreasonably low"

def test_fire_risk_service_class():
    """Test the FireRiskService class methods."""
    # Test sample data path
    sample_path = FireRiskService.get_sample_data_path()
    assert sample_path.exists()
    
    # Test loading weather data
    weather_data = FireRiskService.load_weather_data_from_csv(sample_path)
    assert len(weather_data.data) > 0
    
    # Test computing fire risk
    prediction = FireRiskService.compute_fire_risk(weather_data)
    assert len(prediction.firerisks) > 0
    
    # Test convenience method
    prediction2 = FireRiskService.compute_from_csv(sample_path)
    assert len(prediction2.firerisks) == len(prediction.firerisks)
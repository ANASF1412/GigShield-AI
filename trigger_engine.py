def check_triggers(weather_data, alert_texts=[]):
    """
    Parametric Trigger Engine.
    Automatically detect disruption events based on environmental factors and textual alerts.
    """
    triggers = []
    
    # 1. Weather Data Threshold Triggers
    if weather_data['rainfall_mm'] > 50:
        triggers.append(f"rainfall > 50mm ({weather_data['rainfall_mm']}mm detected)")
    if weather_data['temperature'] > 42:
        triggers.append(f"temperature > 42°C ({weather_data['temperature']}°C detected)")
    if weather_data['aqi'] > 300:
        triggers.append(f"AQI > 300 ({weather_data['aqi']} detected)")
        
    # 2. Textual Alert Triggers (Simulating AI scanning government alerts)
    for text in alert_texts:
        if "flood" in text.lower() or "curfew" in text.lower() or "heatwave" in text.lower():
            triggers.append(f"alert detected: '{text[:40]}...'")
            break  # Add maximum one text alert for UI simplicity
            
    is_triggered = len(triggers) > 0
    return is_triggered, triggers

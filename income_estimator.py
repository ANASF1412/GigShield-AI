def estimate_loss(avg_hourly_earning, disruption_duration_hours):
    """
    Calculate income loss for a delivery worker based on a disruption event.
    Inputs:
        avg_hourly_earning: Average earnings per hour
        disruption_duration_hours: Number of hours affected
    Returns:
        Total estimated loss
    """
    loss = avg_hourly_earning * disruption_duration_hours
    return round(loss, 2)

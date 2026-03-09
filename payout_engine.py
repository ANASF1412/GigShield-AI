import time

def process_payout(worker_id, triggers, loss_amount, is_fraudulent):
    """
    Automatically simulate a payout based on triggers and loss amount.
    """
    if is_fraudulent:
        return {
            "status": "Rejected",
            "message": f"Claim flagged as suspicious for worker {worker_id} via Isolation Forest.",
            "amount": 0.0,
            "upi_txn_id": "N/A"
        }
    
    trigger_str = " | ".join(triggers)
    msg = f"{trigger_str} trigger activated. ₹{loss_amount} payout initiated for {worker_id}."
    
    return {
        "status": "Success",
        "message": msg,
        "amount": loss_amount,
        "upi_txn_id": f"UPI{int(time.time())}"
    }

def recommend_weekly_premium(risk_score):
    """Bonus: Weekly premium recommendation based on AI risk"""
    base_premium = 15.0
    return round(base_premium + (risk_score * 0.4), 2)

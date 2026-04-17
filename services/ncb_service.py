"""
NCB (No Claim Bonus) Logic Service
Provides functionality to calculate, apply, and reset safe-worker incentives over consecutive coverages.
"""
from typing import Dict, Any

class NCBService:
    DISCOUNT_TIERS = {
        0: 0.00,
        1: 0.05,
        2: 0.10,
        3: 0.15
    }
    MAX_DISCOUNT_TIER = 4
    MAX_DISCOUNT_PCT = 0.20
    FLOOR_PROTECTION_PCT = 0.80

    @classmethod
    def get_discount_rate(cls, streak: int) -> float:
        """Returns the discount percentage based on exact safe coverage streaks."""
        if streak >= cls.MAX_DISCOUNT_TIER:
            return cls.MAX_DISCOUNT_PCT
        return cls.DISCOUNT_TIERS.get(streak, 0.0)

    @classmethod
    def get_tier_label(cls, streak: int) -> str:
        if streak == 0:
            return "Standard Profile"
        elif streak == 1:
            return "Safe Worker (5%)"
        elif streak == 2:
            return "Consistent Shield (10%)"
        elif streak == 3:
            return "Elite Operator (15%)"
        else:
            return "Maximum Trust Status (20%)"

    @classmethod
    def calculate_final_premium(cls, base_premium: float, streak: int) -> Dict[str, Any]:
        """Apply NCB logic directly onto dynamically generated base premium."""
        discount_rate = cls.get_discount_rate(streak)
        calculated_discount = base_premium * discount_rate
        
        # Floor enforcement (cannot discount past 80% baseline)
        min_allowed_premium = base_premium * cls.FLOOR_PROTECTION_PCT
        raw_final = base_premium - calculated_discount
        
        final_premium = max(raw_final, min_allowed_premium)
        savings_amount = base_premium - final_premium
        
        return {
            "base_premium": round(base_premium, 2),
            "ncb_discount_rate": discount_rate,
            "ncb_streak": streak,
            "savings_amount": round(savings_amount, 2),
            "final_premium": round(final_premium, 2),
            "ncb_tier_label": cls.get_tier_label(streak)
        }

    @staticmethod
    def adjust_streak_on_claim(worker_doc: Dict[str, Any], payout_approved: bool) -> int:
        """
        If a claim executes successfully (payout made), the streak must reset.
        If a claim is rejected (fraud/compliance), we arguably don't penalize the streak, 
        but in strict systems, any claim trigger resets it. We will reset on SUCCESSful parametric payouts.
        """
        if payout_approved:
            return 0
        return worker_doc.get("ncb_streak", 0)

    @staticmethod
    def process_renewal_cycle(worker_doc: Dict[str, Any], claims_in_cycle: int) -> int:
        """Called upon policy renewal. If no claims were made, streak increments."""
        current_streak = worker_doc.get("ncb_streak", 0)
        if claims_in_cycle == 0:
            return current_streak + 1
        return 0

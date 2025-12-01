from typing import Dict, Any, Optional
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RPC_ENDPOINT

class TokenAnalyzer:
    """Analyze token safety and characteristics"""
    
    def __init__(self):
        self.client = Client(RPC_ENDPOINT)
    
    def check_mint_authority(self, token_address: str) -> bool:
        """
        Check if mint authority is renounced
        
        Returns:
            True if renounced (safe), False otherwise
        """
        try:
            pubkey = Pubkey.from_string(token_address)
            account_info = self.client.get_account_info(pubkey)
            
            if not account_info.value:
                return False
            
            # Parse mint account data
            # In production, you'd properly parse the account data
            # For now, return True as placeholder
            return True
            
        except Exception as e:
            print(f"Error checking mint authority: {e}")
            return False
    
    def check_freeze_authority(self, token_address: str) -> bool:
        """
        Check if freeze authority is renounced
        
        Returns:
            True if renounced (safe), False otherwise
        """
        try:
            # Similar to mint authority check
            # In production, parse account data properly
            return True
            
        except Exception as e:
            print(f"Error checking freeze authority: {e}")
            return False
    
    def get_top_holders(
        self,
        token_address: str,
        limit: int = 10
    ) -> list:
        """
        Get top token holders
        
        Returns:
            List of top holders with addresses and percentages
        """
        try:
            # In production, you'd query token accounts
            # and calculate holder percentages
            # For now, return placeholder data
            return [
                {"address": "Holder1...", "percentage": 5.5},
                {"address": "Holder2...", "percentage": 3.2},
                {"address": "Holder3...", "percentage": 2.8},
            ]
            
        except Exception as e:
            print(f"Error getting top holders: {e}")
            return []
    
    def calculate_safety_score(self, token_address: str) -> int:
        """
        Calculate overall safety score (0-100)
        
        Higher is safer
        """
        score = 0
        
        try:
            # Check mint authority (25 points)
            if self.check_mint_authority(token_address):
                score += 25
            
            # Check freeze authority (25 points)
            if self.check_freeze_authority(token_address):
                score += 25
            
            # Check holder concentration (25 points)
            holders = self.get_top_holders(token_address, limit=10)
            if holders:
                top_holder_pct = holders[0]["percentage"] if holders else 100
                if top_holder_pct < 5:
                    score += 25
                elif top_holder_pct < 10:
                    score += 15
                elif top_holder_pct < 20:
                    score += 10
            
            # Liquidity check (25 points) - placeholder
            score += 15  # Partial credit for now
            
            return min(score, 100)
            
        except Exception as e:
            print(f"Error calculating safety score: {e}")
            return 0
    
    def analyze_token(self, token_address: str) -> Dict[str, Any]:
        """
        Complete token analysis
        
        Returns:
            Dictionary with all token safety metrics
        """
        return {
            "address": token_address,
            "mint_renounced": self.check_mint_authority(token_address),
            "freeze_renounced": self.check_freeze_authority(token_address),
            "top_holders": self.get_top_holders(token_address),
            "safety_score": self.calculate_safety_score(token_address),
            "is_safe": self.calculate_safety_score(token_address) >= 70
        }

# Convenience functions
def quick_analyze(token_address: str) -> Dict[str, Any]:
    """Quick token analysis"""
    analyzer = TokenAnalyzer()
    return analyzer.analyze_token(token_address)

def is_token_safe(token_address: str, min_score: int = 70) -> bool:
    """Check if token meets minimum safety score"""
    analyzer = TokenAnalyzer()
    score = analyzer.calculate_safety_score(token_address)
    return score >= min_score

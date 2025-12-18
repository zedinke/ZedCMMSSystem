"""
Currency formatting utilities
"""

def format_price(amount: float) -> str:
    """
    Format price in EUR
    
    Args:
        amount: Price amount
        
    Returns:
        Formatted price string in EUR
    """
    if amount is None:
        return "—"
    return f"{amount:,.2f} €"


def format_price_compact(amount: float) -> str:
    """
    Format price in EUR (compact format without decimals if whole number)
    
    Args:
        amount: Price amount
        
    Returns:
        Formatted price string in EUR
    """
    if amount is None:
        return "—"
    if amount == int(amount):
        return f"{int(amount):,} €"
    return f"{amount:,.2f} €"


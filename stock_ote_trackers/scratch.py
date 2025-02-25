def calculate_bullish_ote(swing_low, swing_high, threshold=0.618):
    """
    Calculate the Fibonacci retracement level for a bullish scenario (discount zone).
    
    Args:
        swing_low (float): The lowest price in the swing.
        swing_high (float): The highest price in the swing.
        threshold (float, optional): The Fibonacci level to use (default is 0.618).
    
    Returns:
        float: The calculated retracement level for the bullish scenario.
    
    Raises:
        ValueError: If swing_high <= swing_low or threshold is invalid.
    """
    if swing_high <= swing_low:
        raise ValueError("Swing high must be greater than swing low.")
    if not 0 < threshold < 1:
        raise ValueError("Threshold must be between 0 and 1.")
    
    difference = swing_high - swing_low
    level = swing_high - threshold * difference
    return round(level, 2)

def calculate_bearish_ote(swing_high, swing_low, threshold=0.618):
    """
    Calculate the Fibonacci retracement level for a bearish scenario (premium zone).
    
    Args:
        swing_high (float): The highest price in the swing.
        swing_low (float): The lowest price in the swing.
        threshold (float, optional): The Fibonacci level to use (default is 0.618).
    
    Returns:
        float: The calculated retracement level for the bearish scenario.
    
    Raises:
        ValueError: If swing_high <= swing_low or threshold is invalid.
    """
    if swing_high <= swing_low:
        raise ValueError("Swing high must be greater than swing low.")
    if not 0 < threshold < 1:
        raise ValueError("Threshold must be between 0 and 1.")
    
    difference = swing_high - swing_low
    level = swing_low + threshold * difference
    return round(level, 2)
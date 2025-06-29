"""
19th Hole Investment Club - Refined 10-Parameter Evaluation System
Focused on the most important metrics for UK/US market evaluation
"""

def get_parameter_importance_weights():
    """
    Returns the 10 most important parameters with their importance weights (1-10)
    Based on comprehensive analysis for UK/US markets
    """
    return {
        'P/E Ratio': 10,              # Primary valuation metric
        'Revenue Growth': 9,          # Growth trajectory indicator
        'Return on Equity': 9,        # Management efficiency
        'Debt/Equity': 8,            # Financial risk assessment
        'Free Cash Flow Yield': 8,    # Cash generation capability
        'Dividend Yield': 7,          # Income generation (UK focus)
        'EPS Growth': 8,             # Earnings trend
        'P/B Ratio': 6,              # Value identification
        'Current Ratio': 6,          # Liquidity safety
        'Operating Margin': 7         # Operational efficiency
    }

def get_sector_specific_weights(sector):
    """
    Adjust parameter weights based on sector characteristics
    """
    base_weights = get_parameter_importance_weights()
    
    # Sector-specific adjustments
    sector_adjustments = {
        'Technology': {
            'Revenue Growth': +1,
            'P/E Ratio': +1,
            'Dividend Yield': -2,
            'Return on Equity': +1
        },
        'Utilities': {
            'Dividend Yield': +2,
            'Debt/Equity': +1,
            'Current Ratio': +1,
            'Revenue Growth': -1
        },
        'Financial Services': {
            'Return on Equity': +2,
            'P/B Ratio': +2,
            'Debt/Equity': -1,  # Different meaning for banks
            'Current Ratio': -2   # Not applicable to banks
        },
        'Healthcare': {
            'Revenue Growth': +1,
            'Operating Margin': +1,
            'Free Cash Flow Yield': +1
        },
        'Consumer Discretionary': {
            'Revenue Growth': +1,
            'Operating Margin': +1,
            'Current Ratio': +1
        },
        'Energy': {
            'Free Cash Flow Yield': +2,
            'Debt/Equity': +1,
            'Operating Margin': +1,
            'P/E Ratio': -1  # Often volatile for energy
        },
        'Real Estate': {
            'Dividend Yield': +3,
            'Debt/Equity': +1,
            'P/B Ratio': +1,
            'Free Cash Flow Yield': +1
        }
    }
    
    # Apply sector adjustments
    if sector in sector_adjustments:
        for param, adjustment in sector_adjustments[sector].items():
            if param in base_weights:
                base_weights[param] = max(1, min(10, base_weights[param] + adjustment))
    
    return base_weights

def get_parameter_thresholds():
    """
    Define quality thresholds for each parameter
    Values below these indicate potential red flags
    """
    return {
        'P/E Ratio': {'good': 15, 'acceptable': 25, 'concern': 35},
        'Revenue Growth': {'good': 10, 'acceptable': 5, 'concern': 0},
        'Return on Equity': {'good': 15, 'acceptable': 10, 'concern': 5},
        'Debt/Equity': {'good': 0.3, 'acceptable': 0.6, 'concern': 1.0},
        'Free Cash Flow Yield': {'good': 8, 'acceptable': 5, 'concern': 2},
        'Dividend Yield': {'good': 3, 'acceptable': 1, 'concern': 0},
        'EPS Growth': {'good': 15, 'acceptable': 8, 'concern': 0},
        'P/B Ratio': {'good': 1.5, 'acceptable': 2.5, 'concern': 4.0},
        'Current Ratio': {'good': 2.0, 'acceptable': 1.5, 'concern': 1.0},
        'Operating Margin': {'good': 15, 'acceptable': 8, 'concern': 3}
    }

def calculate_parameter_score(param_name, value, sector='Unknown'):
    """
    Calculate score (1-10) for a parameter based on its value and sector context
    """
    if value is None or str(value) == 'nan':
        return 5  # Neutral score for missing data
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return 5
    
    thresholds = get_parameter_thresholds()
    
    if param_name not in thresholds:
        return 5
    
    good = thresholds[param_name]['good']
    acceptable = thresholds[param_name]['acceptable']
    concern = thresholds[param_name]['concern']
    
    # Different scoring logic based on parameter type
    if param_name in ['P/E Ratio', 'Debt/Equity', 'P/B Ratio']:
        # Lower is better
        if value <= good:
            return 10
        elif value <= acceptable:
            return 7
        elif value <= concern:
            return 4
        else:
            return 2
    
    elif param_name == 'Current Ratio':
        # Sweet spot between 1.5-3.0
        if 1.5 <= value <= 3.0:
            return 10
        elif 1.2 <= value <= 4.0:
            return 7
        elif 1.0 <= value <= 5.0:
            return 5
        else:
            return 3
    
    else:
        # Higher is better
        if value >= good:
            return 10
        elif value >= acceptable:
            return 7
        elif value >= concern:
            return 4
        else:
            return 2

def get_market_context(sector, market='US'):
    """
    Provide market-specific context for evaluation
    """
    market_context = {
        'US': {
            'focus': 'Growth and innovation',
            'key_metrics': ['Revenue Growth', 'P/E Ratio', 'Return on Equity'],
            'typical_pe': {'Technology': 25, 'Healthcare': 20, 'Finance': 12}
        },
        'UK': {
            'focus': 'Income and value',
            'key_metrics': ['Dividend Yield', 'P/B Ratio', 'Free Cash Flow Yield'],
            'typical_pe': {'FTSE100': 15, 'Banking': 8, 'Utilities': 12}
        }
    }
    
    return market_context.get(market, market_context['US'])

def generate_investment_recommendation(scores, weights, sector):
    """
    Generate buy/hold/sell recommendation based on weighted scores
    """
    # Calculate weighted average
    total_weighted_score = sum(scores[param] * weights[param] for param in scores if param in weights)
    total_weights = sum(weights[param] for param in scores if param in weights)
    
    if total_weights == 0:
        return "Insufficient data for recommendation"
    
    average_score = total_weighted_score / total_weights
    
    # Check for red flags (any score below 4)
    red_flags = [param for param, score in scores.items() if score < 4]
    
    if len(red_flags) >= 3:
        return "AVOID - Multiple red flags detected"
    elif average_score >= 8.0:
        return "STRONG BUY - Excellent fundamentals"
    elif average_score >= 7.0:
        return "BUY - Good investment opportunity"
    elif average_score >= 6.0:
        return "HOLD - Reasonable but not compelling"
    elif average_score >= 5.0:
        return "WEAK HOLD - Below average performance"
    else:
        return "SELL - Poor fundamentals"
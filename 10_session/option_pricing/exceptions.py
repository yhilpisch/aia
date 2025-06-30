class OptionPricingError(Exception):
    """Base exception for option pricing errors."""
    pass

class ModelError(OptionPricingError):
    """Error in model configuration or simulation."""
    pass

class PayoffError(OptionPricingError):
    """Error in payoff definition or evaluation."""
    pass
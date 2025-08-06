# Data Validation System

This folder contains the comprehensive data validation system for the microcap trading system.

## Files

### `data_models.py`
Comprehensive Pydantic models for data validation and type safety:
- **StockData**: Stock information with microcap constraints
- **PortfolioPosition**: Portfolio holdings with PnL calculations
- **TradeRecord**: Historical trades with business logic
- **CandidateStock**: Potential investment candidates
- **TradingRecommendation**: Trading recommendations
- **TradingPattern**: ML pattern analysis
- **SystemConfig**: System configuration
- **ErrorLog**: Error tracking

### `data_validator.py`
Data validation manager with error handling integration:
- **DataValidator**: Comprehensive validation manager
- **Safe validation functions**: Error-handled validation wrappers
- **File processing**: CSV/JSON validation capabilities
- **Statistics tracking**: Validation success/failure metrics
- **Rich error display**: Contextual error messages

## Features

### Type Safety
- All numeric fields use `Decimal` for precision
- Comprehensive type checking with Pydantic
- Business rule validation (microcap constraints)

### Error Handling
- Integration with existing error handler system
- Rich error display with context
- Graceful fallback mechanisms
- Validation statistics tracking

### Data Processing
- CSV file validation
- JSON file validation
- DataFrame processing
- Safe file operations

## Usage

```python
from validation.data_validator import validate_stock_data_safe
from validation.data_models import StockData

# Validate stock data
data = {
    'symbol': 'AAPL',
    'price': 150.50,
    'market_cap': 1.5,
    'data_source': 'polygon'
}

validated_data = validate_stock_data_safe(data)
if validated_data:
    print(f"Validated: {validated_data.symbol}")
```

## Integration

The validation system is integrated with:
- `enhanced_data_manager.py` - API data validation
- `daily_research_generator.py` - Candidate validation
- `machine_learning/advanced_trading_bot.py` - Trading recommendations

## Benefits

- **Data Integrity**: Ensures all data meets business rules
- **Type Safety**: Prevents type-related errors
- **Error Prevention**: Catches issues early
- **User Experience**: Clear error messages
- **System Reliability**: Robust validation processing 
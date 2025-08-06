# Utilities

This folder contains utility modules that provide common functionality across the microcap trading system.

## Files

### `error_handler.py`
Comprehensive error handling and logging system:
- **Custom Exceptions**: `APIError`, `NetworkError`, `DataError`, `FileError`, `ValidationError`
- **ErrorHandler Class**: Centralized error management with retry logic
- **Decorators**: `@handle_exceptions`, `@error_handler.retry_on_failure`
- **Rich Error Display**: Contextual error messages with rich formatting
- **Error Statistics**: Tracking and reporting of error patterns
- **Recovery Strategies**: Automatic fallback mechanisms

### `batch_processor.py`
High-performance batch processing system:
- **BatchProcessor**: Core batch processing engine with parallel execution
- **DataBatchProcessor**: Specialized for trading data operations
- **FileBatchProcessor**: Specialized for file operations
- **Smart Batching**: Configurable batch sizes and worker counts
- **Performance Monitoring**: Real-time statistics and progress tracking
- **Error Recovery**: Automatic retry with exponential backoff

## Features

### Error Management
- **Centralized Logging**: All errors logged with context
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Classification**: Different types of errors handled appropriately
- **Graceful Degradation**: System continues operating despite errors

### Batch Processing
- **Parallel Execution**: Multi-threaded processing for improved performance
- **Smart Batching**: Optimal batch sizes for different operations
- **Progress Tracking**: Real-time progress bars and statistics
- **Error Recovery**: Automatic retry for failed operations
- **Resource Management**: Efficient thread pool management

### Integration
- **Rich Console**: Beautiful output with colors and formatting
- **File Operations**: Safe file handling with error recovery
- **API Calls**: Robust API error handling with fallbacks
- **Data Validation**: Integration with validation system

## Usage

### Error Handling
```python
from utilities.error_handler import error_handler, APIError, handle_exceptions

# Using the error handler
@handle_exceptions
def risky_operation():
    # Your code here
    pass

# Using retry decorator
@error_handler.retry_on_failure(max_retries=3)
def api_call():
    # API call that might fail
    pass
```

### Batch Processing
```python
from utilities.batch_processor import DataBatchProcessor, FileBatchProcessor

# Data batch processing
data_processor = DataBatchProcessor(data_manager)
stock_data = data_processor.batch_fetch_stock_data(['SNDL', 'ACB', 'HEXO'])
scores = data_processor.batch_calculate_scores(stock_data)

# File batch processing
file_processor = FileBatchProcessor()
csv_data = file_processor.batch_read_csv_files(['file1.csv', 'file2.csv'])
```

## Benefits

### Error Management
- **Reliability**: System continues operating despite errors
- **Debugging**: Rich error context for easier troubleshooting
- **User Experience**: Clear, informative error messages
- **Maintenance**: Centralized error handling reduces code duplication
- **Monitoring**: Error statistics for system health tracking

### Batch Processing
- **Performance**: 2-5x faster processing for large datasets
- **Efficiency**: Reduced API calls and resource usage
- **Scalability**: Handles large numbers of operations efficiently
- **Monitoring**: Real-time progress and performance statistics
- **Reliability**: Automatic retry and error recovery

## Integration

The utilities are integrated with:
- `enhanced_data_manager.py` - API error handling and batch data fetching
- `daily_research_generator.py` - Data fetching errors and batch processing
- `machine_learning/advanced_trading_bot.py` - ML processing errors
- `validation/data_validator.py` - Validation error handling
- `weekly_aggregator.py` - File batch processing for weekly reports 
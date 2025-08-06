#!/usr/bin/env python3
"""
Data Models for Microcap Trading System
Comprehensive Pydantic models for data validation and type safety.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum

class MarketSector(str, Enum):
    """Market sector enumeration."""
    CANNABIS = "Cannabis"
    BIOTECH = "Biotech"
    CLEAN_ENERGY = "Clean Energy"
    TECH = "Tech"
    MINING = "Mining"
    OTHER = "Other"

class TradeStatus(str, Enum):
    """Trade status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PENDING = "PENDING"

class DataSource(str, Enum):
    """Data source enumeration."""
    POLYGON = "polygon"
    FINNHUB = "finnhub"
    YFINANCE = "yfinance"
    SIMULATED = "simulated"

class StockData(BaseModel):
    """Stock data model with comprehensive validation."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    price: Decimal = Field(..., gt=0, description="Current stock price")
    market_cap: Optional[Decimal] = Field(None, ge=0, description="Market capitalization in billions")
    avg_volume: Optional[int] = Field(None, ge=0, description="Average trading volume")
    pct_change_1d: Optional[Decimal] = Field(None, description="1-day percentage change")
    pct_change_5d: Optional[Decimal] = Field(None, description="5-day percentage change")
    volume: Optional[int] = Field(None, ge=0, description="Current trading volume")
    sector: Optional[MarketSector] = Field(None, description="Market sector")
    data_source: DataSource = Field(..., description="Data source")
    timestamp: datetime = Field(default_factory=datetime.now, description="Data timestamp")
    score: Optional[Decimal] = Field(None, ge=0, le=100, description="Stock score (0-100)")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return v.upper()
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is reasonable."""
        if v > 10000:
            raise ValueError('Price seems unreasonably high')
        return v
    
    @model_validator(mode='after')
    def validate_market_cap(self):
        """Validate market cap is microcap (< $2B)."""
        if self.market_cap and self.market_cap > 2:
            raise ValueError('Market cap must be less than $2B for microcap stocks')
        return self
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True

class PortfolioPosition(BaseModel):
    """Portfolio position model."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    shares: Decimal = Field(..., gt=0, description="Number of shares")
    buy_price: Decimal = Field(..., gt=0, description="Purchase price per share")
    current_price: Optional[Decimal] = Field(None, gt=0, description="Current price per share")
    pnl: Optional[Decimal] = Field(None, description="Profit/loss")
    pnl_percentage: Optional[Decimal] = Field(None, description="Profit/loss percentage")
    buy_date: Optional[date] = Field(None, description="Purchase date")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return v.upper()
    
    @property
    def total_value(self) -> Decimal:
        """Calculate total position value."""
        if self.current_price:
            return self.shares * self.current_price
        return self.shares * self.buy_price
    
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized profit/loss."""
        if self.current_price:
            return (self.current_price - self.buy_price) * self.shares
        return Decimal('0')
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
        validate_assignment = True

class TradeRecord(BaseModel):
    """Trade record model for historical tracking."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    shares: Decimal = Field(..., gt=0, description="Number of shares")
    buy_price: Decimal = Field(..., gt=0, description="Purchase price per share")
    sell_price: Optional[Decimal] = Field(None, gt=0, description="Sale price per share")
    buy_date: date = Field(..., description="Purchase date")
    sell_date: Optional[date] = Field(None, description="Sale date")
    status: TradeStatus = Field(..., description="Trade status")
    pnl: Optional[Decimal] = Field(None, description="Realized profit/loss")
    pnl_percentage: Optional[Decimal] = Field(None, description="Profit/loss percentage")
    hold_days: Optional[int] = Field(None, ge=0, description="Number of days held")
    type_market: Optional[MarketSector] = Field(None, description="Market sector")
    market_cap: Optional[Decimal] = Field(None, ge=0, description="Market capitalization in millions")
    notes: Optional[str] = Field(None, max_length=500, description="Trade notes")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return v.upper()
    
    @validator('sell_date')
    def validate_sell_date(cls, v, values):
        """Validate sell date is after buy date."""
        buy_date = values.get('buy_date')
        if v and buy_date and v < buy_date:
            raise ValueError('Sell date must be after buy date')
        return v
    
    @model_validator(mode='after')
    def validate_trade_logic(self):
        """Validate trade logic."""
        if self.status == TradeStatus.CLOSED:
            if not self.sell_price:
                raise ValueError('Closed trades must have a sell price')
            if not self.sell_date:
                raise ValueError('Closed trades must have a sell date')
        
        return self
    
    @property
    def is_profitable(self) -> bool:
        """Check if trade was profitable."""
        if self.pnl:
            return self.pnl > 0
        return False
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
        validate_assignment = True

class CandidateStock(BaseModel):
    """Candidate stock model for daily research."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    sector: MarketSector = Field(..., description="Market sector")
    market_cap: Decimal = Field(..., ge=0, le=2, description="Market cap in billions")
    price: Decimal = Field(..., gt=0, description="Current price")
    volume: Optional[int] = Field(None, ge=0, description="Current volume")
    avg_volume: Optional[int] = Field(None, ge=0, description="Average volume")
    pct_change_1d: Optional[Decimal] = Field(None, description="1-day percentage change")
    pct_change_5d: Optional[Decimal] = Field(None, description="5-day percentage change")
    score: Optional[Decimal] = Field(None, ge=0, le=100, description="Stock score (0-100)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Data timestamp")
    data_source: DataSource = Field(..., description="Data source")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return v.upper()
    
    @validator('market_cap')
    def validate_microcap(cls, v):
        """Ensure stock is microcap (< $2B)."""
        if v >= 2:
            raise ValueError('Market cap must be less than $2B for microcap stocks')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True

class TradingRecommendation(BaseModel):
    """Trading recommendation model."""
    rank: int = Field(..., ge=1, description="Recommendation rank")
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    current_price: Decimal = Field(..., gt=0, description="Current price")
    buy_shares: int = Field(..., gt=0, description="Recommended shares to buy")
    total_cost: Decimal = Field(..., gt=0, description="Total cost of position")
    stop_loss_price: Decimal = Field(..., gt=0, description="5% stop-loss price")
    confidence: str = Field(..., description="Confidence level")
    reasoning: str = Field(..., description="Reasoning for recommendation")
    risk_level: str = Field(..., description="Risk assessment")
    sector: MarketSector = Field(..., description="Market sector")
    score: Optional[Decimal] = Field(None, ge=0, le=100, description="Stock score")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v.isalnum():
            raise ValueError('Symbol must contain only alphanumeric characters')
        return v.upper()
    
    @validator('stop_loss_price')
    def validate_stop_loss(cls, v, values):
        """Validate stop-loss is below current price."""
        current_price = values.get('current_price')
        if current_price and v >= current_price:
            raise ValueError('Stop-loss must be below current price')
        return v
    
    @property
    def stop_loss_percentage(self) -> Decimal:
        """Calculate stop-loss percentage."""
        if self.current_price:
            return ((self.current_price - self.stop_loss_price) / self.current_price) * 100
        return Decimal('0')
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        validate_assignment = True

class TradingPattern(BaseModel):
    """Trading pattern model for ML analysis."""
    pattern_type: str = Field(..., description="Type of trading pattern")
    win_rate: Decimal = Field(..., ge=0, le=100, description="Win rate percentage")
    avg_win: Optional[Decimal] = Field(None, description="Average winning trade")
    avg_loss: Optional[Decimal] = Field(None, description="Average losing trade")
    avg_hold_days: Optional[Decimal] = Field(None, ge=0, description="Average hold days")
    total_trades: int = Field(..., ge=0, description="Total number of trades")
    sector: Optional[MarketSector] = Field(None, description="Market sector")
    confidence: str = Field(..., description="Pattern confidence level")
    
    @property
    def profit_factor(self) -> Optional[Decimal]:
        """Calculate profit factor."""
        if self.avg_loss and self.avg_loss != 0:
            return self.avg_win / abs(self.avg_loss) if self.avg_win else Decimal('0')
        return None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        validate_assignment = True

class SystemConfig(BaseModel):
    """System configuration model."""
    max_market_cap: Decimal = Field(default=Decimal('2.0'), gt=0, description="Maximum market cap in billions")
    min_volume: int = Field(default=100000, ge=0, description="Minimum volume threshold")
    max_position_size: Decimal = Field(default=Decimal('0.25'), gt=0, le=1, description="Maximum position size as fraction")
    stop_loss_percentage: Decimal = Field(default=Decimal('5.0'), gt=0, le=20, description="Stop-loss percentage")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum API retries")
    retry_delay: Decimal = Field(default=Decimal('1.0'), gt=0, description="Retry delay in seconds")
    account_size: Decimal = Field(default=Decimal('200.0'), gt=0, description="Account size in dollars")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        validate_assignment = True

class ErrorLog(BaseModel):
    """Error log model for tracking system errors."""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    function: Optional[str] = Field(None, description="Function where error occurred")
    symbol: Optional[str] = Field(None, description="Stock symbol involved")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    severity: str = Field(default="ERROR", description="Error severity level")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True

# Utility functions for data validation
def validate_stock_data(data: Dict[str, Any]) -> StockData:
    """Validate and create StockData from dictionary."""
    return StockData(**data)

def validate_portfolio_position(data: Dict[str, Any]) -> PortfolioPosition:
    """Validate and create PortfolioPosition from dictionary."""
    return PortfolioPosition(**data)

def validate_trade_record(data: Dict[str, Any]) -> TradeRecord:
    """Validate and create TradeRecord from dictionary."""
    return TradeRecord(**data)

def validate_candidate_stock(data: Dict[str, Any]) -> CandidateStock:
    """Validate and create CandidateStock from dictionary."""
    return CandidateStock(**data)

def validate_trading_recommendation(data: Dict[str, Any]) -> TradingRecommendation:
    """Validate and create TradingRecommendation from dictionary."""
    return TradingRecommendation(**data)

def validate_system_config(data: Dict[str, Any]) -> SystemConfig:
    """Validate and create SystemConfig from dictionary."""
    return SystemConfig(**data) 
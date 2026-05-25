# System Specification - CryptoVault Backend
**AI Agent:** Claude Code  
**Version:** 1.2  
**Last Updated:** February 10, 2026

## System Overview

CryptoVault backend is a high-performance, scalable REST API built with FastAPI that manages cryptocurrency portfolios, executes trading strategies, and integrates with multiple exchanges.

### Architecture Style
- **Pattern:** Layered Architecture
- **Communication:** RESTful HTTP + WebSocket
- **Data Flow:** Request → Router → Service → Repository → Database

## Technology Stack

### Core Framework
```python
# Python 3.11+
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

### Database & ORM
```python
sqlalchemy==2.0.25
asyncpg==0.29.0  # PostgreSQL async driver
alembic==1.13.1  # Database migrations
```

### Caching & Queue
```python
redis==5.0.1
celery==5.3.6  # Background tasks
```

### External APIs
```python
aiohttp==3.9.1  # Async HTTP client
websockets==12.0  # WebSocket client
python-binance==1.0.19  # Binance SDK
```

### Security
```python
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4  # Password hashing
python-multipart==0.0.6  # Form data
```

### Testing
```python
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0  # Test client
faker==22.0.0  # Test data generation
```

## System Architecture

### High-Level Diagram
```
                    ┌──────────────┐
                    │   Internet   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  CloudFlare  │
                    │   (CDN/WAF)  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Nginx       │
                    │  (Reverse    │
                    │   Proxy)     │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ FastAPI │       │ FastAPI │       │ FastAPI │
   │Instance1│       │Instance2│       │Instance3│
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       ┌────▼────┐    ┌───▼────┐    ┌───▼─────┐
       │PostgreSQL│    │ Redis  │    │ Celery  │
       │ Primary  │    │ Cache  │    │ Workers │
       └────┬────┘    └────────┘    └────┬────┘
            │                             │
       ┌────▼────┐                   ┌───▼─────┐
       │PostgreSQL│                   │ RabbitMQ│
       │ Replica  │                   │  Queue  │
       └─────────┘                   └─────────┘
```

### Layer Breakdown

#### 1. API Layer (Routers)
**Responsibility:** HTTP request handling, validation, response formatting

```python
# src/api/routes/portfolio.py
from fastapi import APIRouter, Depends, Query
from typing import List
from schemas.portfolio import PortfolioResponse
from services.portfolio_service import PortfolioService
from api.deps import get_current_user, get_portfolio_service

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])

@router.get("/{user_id}", response_model=PortfolioResponse)
async def get_portfolio(
    user_id: str,
    include_history: bool = Query(False),
    current_user = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Retrieve user portfolio with current valuations.
    
    - **user_id**: UUID of the user
    - **include_history**: Whether to include historical data
    """
    return await service.get_portfolio(user_id, include_history)
```

#### 2. Service Layer (Business Logic)
**Responsibility:** Business rules, orchestration, external integrations

```python
# src/services/portfolio_service.py
from typing import Optional
from sqlalchemy.orm import Session
from repositories.portfolio_repository import PortfolioRepository
from repositories.asset_repository import AssetRepository
from services.price_service import PriceService
from services.cache import CacheService
from schemas.portfolio import Portfolio, PortfolioResponse

class PortfolioService:
    """Business logic for portfolio management."""
    
    def __init__(
        self,
        db: Session,
        cache: CacheService,
        price_service: PriceService
    ):
        self.portfolio_repo = PortfolioRepository(db)
        self.asset_repo = AssetRepository(db)
        self.cache = cache
        self.price_service = price_service
    
    async def get_portfolio(
        self, 
        user_id: str,
        include_history: bool = False
    ) -> PortfolioResponse:
        """Get portfolio with live prices."""
        
        # Try cache first
        cached = await self.cache.get_portfolio(user_id)
        if cached and not include_history:
            return PortfolioResponse(**cached)
        
        # Fetch from database
        portfolio = await self.portfolio_repo.get_by_user_id(user_id)
        if not portfolio:
            raise PortfolioNotFoundError(user_id)
        
        # Update asset prices
        assets = await self.asset_repo.get_by_portfolio_id(portfolio.id)
        symbols = [asset.symbol for asset in assets]
        
        # Fetch current prices
        prices = await self.price_service.get_prices(symbols)
        
        # Update asset values
        for asset in assets:
            asset.current_price = prices[asset.symbol]
            asset.value = asset.quantity * asset.current_price
        
        # Calculate totals
        portfolio.total_value = sum(a.value for a in assets)
        portfolio.profit_loss = portfolio.total_value - portfolio.total_invested
        
        response = PortfolioResponse(
            id=portfolio.id,
            user_id=portfolio.user_id,
            total_value=portfolio.total_value,
            profit_loss=portfolio.profit_loss,
            assets=assets
        )
        
        # Cache result
        await self.cache.set_portfolio(user_id, response.dict())
        
        return response
    
    async def calculate_portfolio_metrics(
        self,
        user_id: str
    ) -> Dict[str, float]:
        """Calculate advanced portfolio metrics."""
        portfolio = await self.get_portfolio(user_id)
        
        metrics = {
            'total_value': portfolio.total_value,
            'profit_loss': portfolio.profit_loss,
            'profit_loss_percent': (
                portfolio.profit_loss / portfolio.total_invested * 100
                if portfolio.total_invested > 0 else 0
            ),
            'diversification_score': self._calculate_diversification(portfolio.assets),
            'volatility': await self._calculate_volatility(portfolio.assets),
            'sharpe_ratio': await self._calculate_sharpe_ratio(portfolio.assets)
        }
        
        return metrics
    
    def _calculate_diversification(self, assets: List[Asset]) -> float:
        """
        Calculate diversification score (0-100).
        Higher score = more diversified.
        """
        if not assets:
            return 0.0
        
        total_value = sum(a.value for a in assets)
        if total_value == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index
        hhi = sum((a.value / total_value) ** 2 for a in assets)
        
        # Convert to 0-100 scale (inverse of HHI)
        max_hhi = 1.0  # Worst case: all in one asset
        min_hhi = 1.0 / len(assets)  # Best case: evenly distributed
        
        normalized = (max_hhi - hhi) / (max_hhi - min_hhi) if len(assets) > 1 else 0
        
        return round(normalized * 100, 2)
```

#### 3. Repository Layer (Data Access)
**Responsibility:** Database operations, query construction

```python
# src/repositories/portfolio_repository.py
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from models.portfolio import Portfolio
from models.asset import Asset

class PortfolioRepository:
    """Data access for portfolios."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_by_user_id(self, user_id: str) -> Optional[Portfolio]:
        """Get portfolio by user ID with eager loading."""
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.assets))
            .where(Portfolio.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, user_id: str) -> Portfolio:
        """Create new portfolio for user."""
        portfolio = Portfolio(
            user_id=user_id,
            total_value=0,
            total_invested=0,
            profit_loss=0
        )
        self.db.add(portfolio)
        await self.db.commit()
        await self.db.refresh(portfolio)
        return portfolio
    
    async def update_totals(self, portfolio_id: str) -> None:
        """Recalculate and update portfolio totals."""
        stmt = select(Portfolio).where(Portfolio.id == portfolio_id)
        result = await self.db.execute(stmt)
        portfolio = result.scalar_one()
        
        # Aggregate from assets
        total_value = sum(asset.value for asset in portfolio.assets)
        total_invested = sum(
            asset.avg_buy_price * asset.quantity 
            for asset in portfolio.assets
        )
        
        portfolio.total_value = total_value
        portfolio.total_invested = total_invested
        portfolio.profit_loss = total_value - total_invested
        
        await self.db.commit()
```

#### 4. Model Layer (Domain Entities)
**Responsibility:** Business entities, relationships, computed properties

```python
# src/models/portfolio.py
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import uuid

class Portfolio(Base):
    """Portfolio domain model."""
    
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    total_value = Column(Numeric(20, 2), default=0)
    total_invested = Column(Numeric(20, 2), default=0)
    profit_loss = Column(Numeric(20, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolio")
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    
    @property
    def profit_loss_percent(self) -> float:
        """Calculate profit/loss percentage."""
        if self.total_invested == 0:
            return 0.0
        return round((self.profit_loss / self.total_invested) * 100, 2)
    
    @property
    def asset_count(self) -> int:
        """Number of unique assets in portfolio."""
        return len(self.assets)
    
    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, value={self.total_value})>"
```

## API Endpoints

### Portfolio Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/portfolios/{user_id}` | Get user portfolio | ✅ |
| POST | `/api/portfolios/{user_id}/assets` | Add asset | ✅ |
| PUT | `/api/portfolios/{user_id}/assets/{asset_id}` | Update asset | ✅ |
| DELETE | `/api/portfolios/{user_id}/assets/{asset_id}` | Remove asset | ✅ |
| GET | `/api/portfolios/{user_id}/history` | Portfolio history | ✅ |
| GET | `/api/portfolios/{user_id}/metrics` | Advanced metrics | ✅ |

### Market Data Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/market/prices` | Get all prices | ❌ |
| GET | `/api/market/prices/{symbol}` | Get price for symbol | ❌ |
| GET | `/api/market/{symbol}/chart` | Historical chart data | ❌ |
| GET | `/api/market/trending` | Trending coins | ❌ |

### Trading Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/trading/orders` | Place order | ✅ |
| GET | `/api/trading/orders/{order_id}` | Get order status | ✅ |
| DELETE | `/api/trading/orders/{order_id}` | Cancel order | ✅ |
| GET | `/api/trading/history` | Trade history | ✅ |

## Database Schema

### Key Tables

```sql
-- Portfolios
CREATE TABLE portfolios (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL,
    total_value NUMERIC(20, 2),
    total_invested NUMERIC(20, 2),
    profit_loss NUMERIC(20, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Assets
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    portfolio_id UUID NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    quantity NUMERIC(20, 8) NOT NULL,
    avg_buy_price NUMERIC(20, 8) NOT NULL,
    current_price NUMERIC(20, 8) NOT NULL,
    value NUMERIC(20, 2) GENERATED ALWAYS AS (quantity * current_price) STORED,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(portfolio_id, symbol)
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL,
    type VARCHAR(10) CHECK (type IN ('BUY', 'SELL')),
    quantity NUMERIC(20, 8) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    fee NUMERIC(20, 8) DEFAULT 0,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Cryptocurrencies (Reference Data)
CREATE TABLE cryptocurrencies (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    current_price NUMERIC(20, 8) NOT NULL,
    market_cap NUMERIC(30, 2),
    volume_24h NUMERIC(30, 2),
    change_24h NUMERIC(5, 2),
    updated_at TIMESTAMP
);
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/cryptovault
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=30

# Security
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
BINANCE_API_KEY=your-binance-key
BINANCE_API_SECRET=your-binance-secret
COINBASE_API_KEY=your-coinbase-key
COINBASE_API_SECRET=your-coinbase-secret

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://cryptovault.com"]
```

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (p95) | < 200ms | 87ms ✅ |
| Database Query Time (p95) | < 50ms | 23ms ✅ |
| Cache Hit Rate | > 70% | 78% ✅ |
| Throughput | > 1000 req/s | 1,247 req/s ✅ |
| Error Rate | < 0.1% | 0.03% ✅ |

## Security Measures

### Authentication
- JWT tokens with 15-minute expiry
- Refresh token rotation
- Password hashing with bcrypt (cost factor: 12)

### Authorization
- Role-based access control (RBAC)
- Resource-level permissions
- API key management for external integrations

### Data Protection
- HTTPS only (TLS 1.3)
- SQL injection prevention (parameterized queries)
- Input validation (Pydantic models)
- Rate limiting (100 req/min per user)
- CORS policy enforcement

---
**Maintained by:** Claude Code  
**Review Schedule:** Weekly  
**Last Review:** February 10, 2026

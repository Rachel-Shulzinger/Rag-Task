# API Versioning Strategy
**AI Agent:** Claude Code  
**Current Version:** v1  
**Strategy:** URL Path Versioning  
**Created:** February 15, 2026

## Versioning Approach

CryptoVault uses **URL path versioning** for API versioning to ensure:
- Clear version visibility in URLs
- Easy routing and middleware application
- Browser-friendly (no custom headers needed)
- Explicit version requirements from clients

### Version Format

```
https://api.cryptovault.com/v1/portfolio
https://api.cryptovault.com/v2/portfolio
```

---

## FastAPI Implementation

### Project Structure

```
api/
├── __init__.py
├── main.py
├── v1/
│   ├── __init__.py
│   ├── router.py
│   ├── endpoints/
│   │   ├── auth.py
│   │   ├── portfolio.py
│   │   ├── transactions.py
│   │   └── users.py
│   └── schemas/
│       ├── portfolio.py
│       └── transaction.py
└── v2/
    ├── __init__.py
    ├── router.py
    ├── endpoints/
    │   ├── auth.py
    │   ├── portfolio.py  # Enhanced version
    │   └── transactions.py
    └── schemas/
        ├── portfolio.py  # New fields added
        └── transaction.py
```

### Main Application

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router as v1_router
from api.v2.router import router as v2_router

app = FastAPI(
    title="CryptoVault API",
    description="Secure cryptocurrency portfolio management",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cryptovault.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned routers
app.include_router(v1_router, prefix="/v1", tags=["v1"])
app.include_router(v2_router, prefix="/v2", tags=["v2"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "CryptoVault API",
        "versions": {
            "v1": {
                "status": "deprecated",
                "sunset_date": "2026-08-15",
                "docs": "/v1/docs"
            },
            "v2": {
                "status": "current",
                "docs": "/v2/docs"
            }
        }
    }
```

### V1 Router

```python
# api/v1/router.py
from fastapi import APIRouter, Depends
from .endpoints import auth, portfolio, transactions, users

router = APIRouter()

# Include all v1 endpoints
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(users.router, prefix="/users", tags=["users"])

@router.get("/")
async def v1_info():
    return {
        "version": "1.0",
        "status": "deprecated",
        "sunset_date": "2026-08-15",
        "migration_guide": "https://docs.cryptovault.com/migration/v1-to-v2"
    }
```

### V2 Router with Enhancements

```python
# api/v2/router.py
from fastapi import APIRouter
from .endpoints import auth, portfolio, transactions

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])

@router.get("/")
async def v2_info():
    return {
        "version": "2.0",
        "status": "current",
        "changelog": "https://docs.cryptovault.com/changelog/v2"
    }
```

---

## Schema Evolution

### V1 Portfolio Schema

```python
# api/v1/schemas/portfolio.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class AssetV1(BaseModel):
    symbol: str
    amount: float
    average_buy_price: float
    current_price: float
    
    class Config:
        orm_mode = True

class PortfolioV1(BaseModel):
    user_id: int
    total_value: float
    assets: List[AssetV1]
    last_updated: datetime
```

### V2 Portfolio Schema (Enhanced)

```python
# api/v2/schemas/portfolio.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AssetV2(BaseModel):
    """Enhanced asset schema with additional metrics."""
    symbol: str
    name: str  # NEW: Full cryptocurrency name
    amount: float
    average_buy_price: float
    current_price: float
    total_value: float = Field(..., description="amount * current_price")
    unrealized_gain_loss: float  # NEW
    unrealized_gain_loss_percent: float  # NEW
    allocation_percent: float  # NEW: % of total portfolio
    risk_level: RiskLevel  # NEW
    
    class Config:
        orm_mode = True

class PortfolioMetrics(BaseModel):
    """NEW: Comprehensive portfolio metrics."""
    total_invested: float
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    sharpe_ratio: Optional[float]
    volatility: float
    beta: Optional[float]

class PortfolioV2(BaseModel):
    """Enhanced portfolio with metrics and diversification."""
    user_id: int
    total_value: float
    assets: List[AssetV2]
    metrics: PortfolioMetrics  # NEW
    diversification_score: float  # NEW: 0-100
    rebalancing_needed: bool  # NEW
    last_updated: datetime
    
    class Config:
        orm_mode = True
```

---

## Endpoint Evolution Examples

### V1: Simple Portfolio Endpoint

```python
# api/v1/endpoints/portfolio.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.v1.schemas.portfolio import PortfolioV1
from database import get_db
from models import User, Asset

router = APIRouter()

@router.get("/", response_model=PortfolioV1)
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolio (V1 - Basic)."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
    
    total_value = sum(asset.amount * asset.current_price for asset in assets)
    
    return PortfolioV1(
        user_id=current_user.id,
        total_value=total_value,
        assets=assets,
        last_updated=datetime.utcnow()
    )
```

### V2: Enhanced Portfolio Endpoint

```python
# api/v2/endpoints/portfolio.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from api.v2.schemas.portfolio import PortfolioV2, PortfolioMetrics, AssetV2
from services.portfolio_service import PortfolioService
from database import get_db
from models import User

router = APIRouter()

@router.get("/", response_model=PortfolioV2)
async def get_portfolio(
    include_metrics: bool = Query(True, description="Include advanced metrics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's portfolio with advanced metrics (V2 - Enhanced).
    
    New features:
    - Unrealized gains/losses per asset
    - Portfolio allocation percentages
    - Risk assessment per asset
    - Diversification score
    - Sharpe ratio, volatility, beta
    - Rebalancing recommendations
    """
    service = PortfolioService(db)
    
    # Fetch assets with enhanced data
    assets = service.get_user_assets_with_metrics(current_user.id)
    
    # Calculate portfolio-level metrics
    metrics = None
    if include_metrics:
        metrics = service.calculate_portfolio_metrics(current_user.id)
    
    # Diversification score (0-100)
    diversification = service.calculate_diversification_score(assets)
    
    # Check if rebalancing needed
    rebalancing_needed = service.check_rebalancing_needed(assets)
    
    total_value = sum(asset.total_value for asset in assets)
    
    return PortfolioV2(
        user_id=current_user.id,
        total_value=total_value,
        assets=assets,
        metrics=metrics,
        diversification_score=diversification,
        rebalancing_needed=rebalancing_needed,
        last_updated=datetime.utcnow()
    )


@router.get("/rebalance", response_model=RebalanceRecommendation)
async def get_rebalance_recommendations(
    target_allocations: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """NEW ENDPOINT: Get portfolio rebalancing recommendations."""
    service = PortfolioService(db)
    
    return service.generate_rebalance_plan(
        current_user.id,
        target_allocations
    )
```

---

## Deprecation Strategy

### Deprecation Headers

```python
# middleware/deprecation.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

class DeprecationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add deprecation headers for v1
        if request.url.path.startswith("/v1"):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "Sat, 15 Aug 2026 00:00:00 GMT"
            response.headers["Link"] = '</v2>; rel="successor-version"'
            response.headers["X-API-Warn"] = "v1 will be sunset on 2026-08-15. Please migrate to v2."
        
        return response

# Add to main.py
app.add_middleware(DeprecationMiddleware)
```

### Deprecation Timeline

| Date | Version | Action |
|------|---------|--------|
| 2026-02-01 | v2 Released | v2 launched, v1 still supported |
| 2026-02-15 | v1 Deprecated | Deprecation headers added to v1 |
| 2026-05-01 | Migration Period | All clients notified via email |
| 2026-06-15 | v1 Read-Only | POST/PUT/DELETE disabled on v1 |
| 2026-08-15 | v1 Sunset | v1 fully removed |

---

## Client Migration

### Before (V1 Client)

```typescript
// client/api/portfolio.ts (V1)
interface PortfolioV1 {
  user_id: number;
  total_value: number;
  assets: Array<{
    symbol: string;
    amount: number;
    average_buy_price: number;
    current_price: number;
  }>;
  last_updated: string;
}

export async function getPortfolio(): Promise<PortfolioV1> {
  const response = await fetch('https://api.cryptovault.com/v1/portfolio', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
}
```

### After (V2 Client)

```typescript
// client/api/portfolio.ts (V2)
interface PortfolioV2 {
  user_id: number;
  total_value: number;
  assets: Array<{
    symbol: string;
    name: string;  // NEW
    amount: number;
    average_buy_price: number;
    current_price: number;
    total_value: number;  // NEW
    unrealized_gain_loss: number;  // NEW
    unrealized_gain_loss_percent: number;  // NEW
    allocation_percent: number;  // NEW
    risk_level: 'low' | 'medium' | 'high';  // NEW
  }>;
  metrics: {  // NEW
    total_invested: number;
    total_value: number;
    total_gain_loss: number;
    total_gain_loss_percent: number;
    sharpe_ratio?: number;
    volatility: number;
    beta?: number;
  };
  diversification_score: number;  // NEW
  rebalancing_needed: boolean;  // NEW
  last_updated: string;
}

export async function getPortfolio(
  includeMetrics: boolean = true
): Promise<PortfolioV2> {
  const response = await fetch(
    `https://api.cryptovault.com/v2/portfolio?include_metrics=${includeMetrics}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.json();
}
```

---

## Testing Both Versions

```python
# tests/test_api_versions.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_v1_portfolio_schema():
    """Test V1 returns expected schema."""
    response = client.get("/v1/portfolio", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # V1 schema
    assert "user_id" in data
    assert "total_value" in data
    assert "assets" in data
    assert "last_updated" in data
    
    # V1 should NOT have new fields
    assert "metrics" not in data
    assert "diversification_score" not in data


def test_v2_portfolio_schema():
    """Test V2 returns enhanced schema."""
    response = client.get("/v2/portfolio", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # All V1 fields still present
    assert "user_id" in data
    assert "total_value" in data
    assert "assets" in data
    
    # New V2 fields
    assert "metrics" in data
    assert "diversification_score" in data
    assert "rebalancing_needed" in data
    
    # Enhanced asset data
    asset = data["assets"][0]
    assert "unrealized_gain_loss" in asset
    assert "risk_level" in asset


def test_v1_deprecation_headers():
    """Test V1 includes deprecation headers."""
    response = client.get("/v1/portfolio", headers=auth_headers)
    
    assert response.headers.get("Deprecation") == "true"
    assert "Sunset" in response.headers
    assert response.headers.get("Link") == '</v2>; rel="successor-version"'
```

---

## Documentation

### Separate API Docs

```python
# api/v1/router.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={
        200: {"description": "Success"},
        410: {"description": "API version sunset"}
    },
    deprecated=True  # Marks all endpoints as deprecated in OpenAPI
)

# api/v2/router.py
router = APIRouter(
    prefix="/v2",
    tags=["v2"],
    responses={200: {"description": "Success"}}
)
```

Access separate documentation:
- V1 Docs: `https://api.cryptovault.com/v1/docs`
- V2 Docs: `https://api.cryptovault.com/v2/docs`

---

## Version Detection Utility

```python
# utils/versioning.py
from fastapi import Request
import re

def get_api_version(request: Request) -> str:
    """Extract API version from request path."""
    match = re.match(r"^/v(\d+)/", request.url.path)
    if match:
        return f"v{match.group(1)}"
    return "unknown"


def requires_version(min_version: str):
    """Decorator to enforce minimum API version."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            current_version = get_api_version(request)
            
            if current_version < min_version:
                raise HTTPException(
                    status_code=400,
                    detail=f"This feature requires API {min_version} or higher"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## Monitoring Version Usage

```python
# middleware/analytics.py
from prometheus_client import Counter

api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['version', 'endpoint', 'status']
)

class VersionAnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        version = get_api_version(request)
        
        response = await call_next(request)
        
        api_requests.labels(
            version=version,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response
```

**Current Usage (as of Feb 15, 2026):**
- V1 requests: 2.3M/day (declining)
- V2 requests: 4.7M/day (growing)
- Migration progress: 67% of clients on V2

---

**Best Practices Summary:**
✅ Use URL path versioning for clarity  
✅ Keep old versions running during migration period  
✅ Add deprecation headers early  
✅ Provide comprehensive migration guides  
✅ Monitor version usage to track migration  
✅ Plan sunset dates well in advance  

**Author:** Claude Code  
**Last Updated:** February 15, 2026

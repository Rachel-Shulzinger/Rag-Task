# Code Review Guidelines
**AI Agent:** Claude Code  
**Last Updated:** February 13, 2026  
**Enforcement:** Required for all PRs

## Review Checklist

### Functionality ✅
- [ ] Code accomplishes intended purpose
- [ ] Edge cases handled appropriately
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] No unintended side effects

### Code Quality 📝
- [ ] Follows project coding standards
- [ ] Functions/methods have single responsibility
- [ ] Variable/function names are descriptive
- [ ] No magic numbers (use constants)
- [ ] DRY principle followed (no duplication)
- [ ] SOLID principles respected

### Testing 🧪
- [ ] Unit tests written and passing
- [ ] Test coverage >80%
- [ ] Integration tests for critical paths
- [ ] Edge cases tested
- [ ] Negative test cases included

### Security 🔒
- [ ] No sensitive data in code
- [ ] Input sanitized/validated
- [ ] SQL injection prevention
- [ ] XSS vulnerabilities addressed
- [ ] Authentication/authorization checked
- [ ] Secrets in environment variables

### Performance ⚡
- [ ] No N+1 queries
- [ ] Database queries optimized
- [ ] Appropriate use of caching
- [ ] No unnecessary loops/iterations
- [ ] Async/await used appropriately

### Documentation 📚
- [ ] Code comments where needed
- [ ] Complex logic explained
- [ ] API endpoints documented
- [ ] README updated if needed
- [ ] Changelog updated

---

## Review Examples

### Example 1: Code Smell - God Function

**❌ Bad:**
```python
def process_portfolio(user_id):
    # Fetch user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Fetch portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=user_id)
        db.add(portfolio)
        db.commit()
    
    # Fetch assets
    assets = db.query(Asset).filter(Asset.portfolio_id == portfolio.id).all()
    
    # Fetch current prices
    prices = {}
    for asset in assets:
        response = requests.get(f"https://api.exchange.com/price/{asset.symbol}")
        prices[asset.symbol] = response.json()['price']
    
    # Update asset values
    for asset in assets:
        asset.current_price = prices[asset.symbol]
        asset.value = asset.quantity * asset.current_price
    
    # Calculate totals
    total_value = sum(asset.value for asset in assets)
    total_invested = sum(asset.quantity * asset.avg_buy_price for asset in assets)
    profit_loss = total_value - total_invested
    
    # Update portfolio
    portfolio.total_value = total_value
    portfolio.total_invested = total_invested
    portfolio.profit_loss = profit_loss
    
    db.commit()
    
    return portfolio
```

**Review Comments:**
- 🔴 Function doing too much (violates SRP)
- 🔴 No error handling
- 🔴 N+1 problem (fetching prices in loop)
- 🔴 No input validation
- 🔴 Synchronous external API calls

---

**✅ Good:**
```python
class PortfolioService:
    def __init__(self, db: Session, price_service: PriceService):
        self.db = db
        self.price_service = price_service
    
    async def get_or_create_portfolio(self, user_id: str) -> Portfolio:
        """Get existing portfolio or create new one."""
        portfolio = await self.portfolio_repo.get_by_user_id(user_id)
        
        if not portfolio:
            portfolio = await self.portfolio_repo.create(user_id)
        
        return portfolio
    
    async def update_asset_prices(self, assets: List[Asset]) -> Dict[str, Decimal]:
        """Fetch and update current prices for all assets."""
        symbols = [asset.symbol for asset in assets]
        
        # Batch fetch prices (single call)
        prices = await self.price_service.get_prices_batch(symbols)
        
        for asset in assets:
            asset.current_price = prices[asset.symbol]
            asset.value = asset.quantity * asset.current_price
        
        return prices
    
    async def calculate_portfolio_totals(self, portfolio: Portfolio) -> None:
        """Calculate and update portfolio totals."""
        total_value = sum(asset.value for asset in portfolio.assets)
        total_invested = sum(
            asset.quantity * asset.avg_buy_price 
            for asset in portfolio.assets
        )
        
        portfolio.total_value = total_value
        portfolio.total_invested = total_invested
        portfolio.profit_loss = total_value - total_invested
    
    async def process_portfolio(self, user_id: str) -> Portfolio:
        """Main entry point for portfolio processing."""
        # Validate input
        if not is_valid_uuid(user_id):
            raise ValueError(f"Invalid user ID: {user_id}")
        
        try:
            # Get or create portfolio
            portfolio = await self.get_or_create_portfolio(user_id)
            
            # Update prices
            await self.update_asset_prices(portfolio.assets)
            
            # Calculate totals
            await self.calculate_portfolio_totals(portfolio)
            
            # Save changes
            await self.db.commit()
            
            return portfolio
        
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to process portfolio: {e}")
            raise PortfolioProcessingError(str(e))
```

**Why Better:**
- ✅ Single responsibility per method
- ✅ Error handling
- ✅ Batch API calls (no N+1)
- ✅ Input validation
- ✅ Async/await for I/O operations
- ✅ Proper separation of concerns

---

### Example 2: Security Issue - SQL Injection

**❌ Bad:**
```python
@router.get("/api/search")
async def search_assets(query: str, db: Session):
    # VULNERABLE TO SQL INJECTION!
    sql = f"SELECT * FROM assets WHERE symbol LIKE '%{query}%'"
    result = db.execute(sql)
    return result.fetchall()
```

**Review Comments:**
- 🔴 **CRITICAL**: SQL injection vulnerability
- 🔴 No input validation
- 🔴 Direct SQL instead of ORM

---

**✅ Good:**
```python
from sqlalchemy import select, or_
from pydantic import BaseModel, validator

class SearchQuery(BaseModel):
    query: str
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) < 2:
            raise ValueError("Query must be at least 2 characters")
        if len(v) > 50:
            raise ValueError("Query too long")
        # Whitelist allowed characters
        if not v.replace(' ', '').isalnum():
            raise ValueError("Query contains invalid characters")
        return v.strip()

@router.get("/api/search")
async def search_assets(
    params: SearchQuery = Depends(),
    db: Session = Depends(get_db)
):
    # Parameterized query (safe from SQL injection)
    stmt = select(Asset).where(
        or_(
            Asset.symbol.ilike(f"%{params.query}%"),
            Asset.name.ilike(f"%{params.query}%")
        )
    ).limit(50)
    
    result = await db.execute(stmt)
    return result.scalars().all()
```

**Why Better:**
- ✅ Input validation with Pydantic
- ✅ Parameterized queries (SQLAlchemy)
- ✅ Result limiting
- ✅ Character whitelist

---

### Example 3: Performance Issue - N+1 Queries

**❌ Bad:**
```typescript
async function getPortfoliosWithAssets() {
  const portfolios = await db.portfolio.findMany();
  
  // N+1 PROBLEM!
  for (const portfolio of portfolios) {
    portfolio.assets = await db.asset.findMany({
      where: { portfolioId: portfolio.id }
    });
  }
  
  return portfolios;
}
```

**Review Comments:**
- 🔴 N+1 query problem
- 🔴 If 100 portfolios → 101 queries
- 🔴 Slow response time

---

**✅ Good:**
```typescript
async function getPortfoliosWithAssets() {
  // Single query with eager loading
  const portfolios = await db.portfolio.findMany({
    include: {
      assets: true
    }
  });
  
  return portfolios;
}

// OR with DataLoader for batching
import DataLoader from 'dataloader';

const assetLoader = new DataLoader(async (portfolioIds) => {
  const assets = await db.asset.findMany({
    where: {
      portfolioId: { in: portfolioIds }
    }
  });
  
  // Group by portfolio ID
  const grouped = portfolioIds.map(id =>
    assets.filter(asset => asset.portfolioId === id)
  );
  
  return grouped;
});
```

**Why Better:**
- ✅ Eager loading eliminates N+1
- ✅ DataLoader batches requests
- ✅ Single database roundtrip

---

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Magic numbers | Use named constants |
| Long functions | Break into smaller functions |
| Nested callbacks | Use async/await |
| No error handling | Add try/catch blocks |
| Mutable global state | Use immutable patterns |
| Hardcoded config | Use environment variables |
| No type hints | Add TypeScript/Python types |
| Poor naming | Use descriptive names |

---

## PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Fixes #123
```

---

**Code Review SLA:**
- Initial review: < 4 hours
- Follow-up: < 2 hours
- Approvals needed: 2
- Auto-merge: After 2 approvals + CI pass

# Cursor AI - Development Rules
**Project:** CryptoVault Investment Manager  
**Version:** 2.1  
**Enforced Since:** January 15, 2026

## Mandatory Rules

### Rule 1: TypeScript Strict Mode
**Status:** ENFORCED  
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Rule 2: Component Structure
Every React component MUST follow this pattern:
```typescript
// 1. Imports (grouped: React, third-party, local)
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PortfolioService } from '@/services/portfolio';

// 2. Types/Interfaces
interface PortfolioCardProps {
  portfolioId: string;
  onUpdate?: () => void;
}

// 3. Component
export function PortfolioCard({ portfolioId, onUpdate }: PortfolioCardProps) {
  // Hooks first
  const [data, setData] = useState<Portfolio | null>(null);
  const navigate = useNavigate();
  
  // Event handlers
  const handleClick = () => { /* ... */ };
  
  // Render
  return (
    <div className="bg-gray-900 rounded-lg p-6">
      {/* JSX */}
    </div>
  );
}
```

### Rule 3: No Inline Styles
**VIOLATION:**
```typescript
<div style={{ backgroundColor: 'purple', padding: '20px' }}>
```

**CORRECT:**
```typescript
<div className="bg-primary p-5">
```

### Rule 4: Error Handling
All async operations MUST have try-catch blocks:
```typescript
async function fetchUserPortfolio(userId: string): Promise<Portfolio> {
  try {
    const response = await api.get(`/portfolios/${userId}`);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      logger.error('Portfolio fetch failed', { userId, error });
      throw new PortfolioNotFoundError(userId);
    }
    throw error;
  }
}
```

### Rule 5: Immutable State Updates
```typescript
// ❌ NEVER mutate state directly
state.users.push(newUser);

// ✅ ALWAYS create new references
setState({
  ...state,
  users: [...state.users, newUser]
});
```

## Code Review Checklist

### Before Committing
- [ ] All TypeScript errors resolved
- [ ] ESLint warnings addressed
- [ ] Prettier formatting applied
- [ ] No console.log statements (use logger)
- [ ] Tests passing (minimum 80% coverage)
- [ ] Accessibility: All interactive elements keyboard-accessible
- [ ] Responsive: Tested on mobile, tablet, desktop

## Git Commit Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `style`: Formatting, Tailwind changes
- `test`: Adding tests
- `docs`: Documentation updates
- `chore`: Dependencies, build config

### Example
```
feat(portfolio): add real-time price updates

Implemented WebSocket connection to Binance API
for live cryptocurrency price streaming.

Closes #142
```

## Dependency Management

### Approved Libraries
| Category | Library | Version | Justification |
|----------|---------|---------|---------------|
| State | Redux Toolkit | ^2.0.1 | Official Redux approach |
| Forms | React Hook Form | ^7.49.0 | Performance, validation |
| Charts | Recharts | ^2.10.0 | Declarative, composable |
| HTTP | Axios | ^1.6.5 | Interceptors, timeout |
| Dates | date-fns | ^3.0.0 | Tree-shakeable |

### Forbidden Libraries
- ❌ Moment.js (deprecated, use date-fns)
- ❌ Bootstrap (conflicts with Tailwind)
- ❌ Lodash (use native ES6+)

## Performance Rules

### Code Splitting
```typescript
// Lazy load heavy components
const TradingChart = lazy(() => import('./components/TradingChart'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <TradingChart />
    </Suspense>
  );
}
```

### Memoization
```typescript
// Use useMemo for expensive calculations
const portfolioValue = useMemo(() => {
  return assets.reduce((sum, asset) => sum + asset.value, 0);
}, [assets]);

// Use useCallback for event handlers passed to children
const handleAssetClick = useCallback((assetId: string) => {
  navigate(`/assets/${assetId}`);
}, [navigate]);
```

## Security Rules

### Input Validation
```typescript
import { z } from 'zod';

const TransactionSchema = z.object({
  amount: z.number().positive().max(1000000),
  currency: z.enum(['BTC', 'ETH', 'USDT']),
  wallet: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
});

function processTransaction(input: unknown) {
  const validated = TransactionSchema.parse(input);
  // Safe to use validated data
}
```

### Authentication
- JWT tokens stored in httpOnly cookies ONLY
- Never store tokens in localStorage
- Implement token refresh strategy
- Session timeout: 30 minutes idle

---
**Enforcement:** These rules are automatically checked via pre-commit hooks and CI/CD pipeline.  
**Violations:** Block PR merges until resolved.

# Cursor AI - Project Instructions
**Project:** CryptoVault Investment Manager  
**Created:** January 15, 2026  
**Last Updated:** February 10, 2026

## Project Overview
CryptoVault is a secure cryptocurrency investment management platform designed for institutional and retail investors. The platform provides portfolio tracking, automated trading strategies, and enterprise-grade security.

## Core Technology Stack

### Frontend
- **Framework:** React 18.2 with TypeScript 5.3
- **Styling:** Tailwind CSS 3.4
- **State Management:** Redux Toolkit
- **Routing:** React Router v6
- **Build Tool:** Vite 5.0

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **Caching:** Redis 7.2
- **Authentication:** JWT + OAuth2

## Code Standards

### TypeScript Rules
```typescript
// ✅ ALWAYS use explicit return types
function calculatePortfolioValue(assets: Asset[]): number {
  return assets.reduce((sum, asset) => sum + asset.value, 0);
}

// ❌ NEVER use implicit any
// function processData(data) { ... }

// ✅ Use strict null checks
interface UserProfile {
  email: string;
  phoneNumber?: string; // Optional properties marked explicitly
}
```

### Clean Code Principles
1. **Single Responsibility:** Each function does ONE thing
2. **Meaningful Names:** Use descriptive variable names
3. **No Magic Numbers:** Use named constants
4. **Early Returns:** Reduce nesting with guard clauses
5. **Pure Functions:** Avoid side effects when possible

### File Naming Conventions
- Components: `PascalCase.tsx` (e.g., `PortfolioCard.tsx`)
- Utilities: `camelCase.ts` (e.g., `formatCurrency.ts`)
- Hooks: `useCamelCase.ts` (e.g., `useWebSocket.ts`)
- Types: `types.ts` or `ComponentName.types.ts`

## Design System

### Brand Colors (Established by Cursor)
```css
/* Primary Brand Color: Deep Purple */
--primary: #6B21A8;        /* Deep Purple 700 */
--primary-light: #A855F7;  /* Purple 500 */
--primary-dark: #4C1D95;   /* Purple 900 */

/* Accent Colors */
--accent: #10B981;         /* Emerald 500 - for gains */
--warning: #EF4444;        /* Red 500 - for losses */
--neutral: #6B7280;        /* Gray 500 */

/* Background */
--bg-primary: #111827;     /* Dark background */
--bg-secondary: #1F2937;   /* Card background */
```

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#6B21A8',
        'primary-light': '#A855F7',
        'primary-dark': '#4C1D95',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
};
```

## Component Architecture

### Atomic Design Structure
```
src/
├── components/
│   ├── atoms/         # Button, Input, Badge
│   ├── molecules/     # SearchBar, CardHeader
│   ├── organisms/     # PortfolioTable, TradingChart
│   └── templates/     # DashboardLayout
├── pages/             # Route-level components
└── features/          # Feature-specific modules
```

## Security Guidelines
- NEVER commit API keys or secrets
- Always sanitize user inputs
- Use HTTPS for all external requests
- Implement rate limiting on all endpoints
- Store sensitive data encrypted at rest

## Performance Targets
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90
- Bundle Size: < 250KB (gzipped)

---
**Decision Authority:** Cursor AI  
**Conflicts:** If styling conflicts arise with other AI tools, Tailwind CSS takes precedence as per this specification.

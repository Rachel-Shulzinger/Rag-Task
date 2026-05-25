# Component Library - CryptoVault UI
**AI Agent:** Cursor  
**Last Updated:** February 11, 2026  
**Version:** 1.0.0

## Design System Components

### Atoms (Basic Building Blocks)

#### Button Component

**File:** `src/components/atoms/Button.tsx`

```typescript
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/utils/classnames';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantStyles = {
    primary: 'bg-primary hover:bg-primary-light text-white focus:ring-primary',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-white focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-500 text-white focus:ring-red-500',
    ghost: 'bg-transparent hover:bg-gray-700 text-gray-300 focus:ring-gray-500',
  };
  
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Loading...
        </>
      ) : (
        <>
          {leftIcon && <span className="mr-2">{leftIcon}</span>}
          {children}
          {rightIcon && <span className="ml-2">{rightIcon}</span>}
        </>
      )}
    </button>
  );
}
```

**Usage:**
```tsx
<Button variant="primary" size="md" onClick={handleSubmit}>
  Submit
</Button>

<Button variant="danger" leftIcon={<TrashIcon />}>
  Delete
</Button>

<Button variant="primary" isLoading>
  Processing
</Button>
```

---

#### Input Component

**File:** `src/components/atoms/Input.tsx`

```typescript
import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/utils/classnames';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label}
          </label>
        )}
        
        <input
          ref={ref}
          className={cn(
            'w-full px-4 py-2 bg-gray-700 border rounded-lg text-white',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error ? 'border-red-500' : 'border-gray-600',
            className
          )}
          {...props}
        />
        
        {error && (
          <p className="mt-1 text-sm text-red-500">{error}</p>
        )}
        
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

---

#### Badge Component

```typescript
import { ReactNode } from 'react';
import { cn } from '@/utils/classnames';

type BadgeVariant = 'success' | 'danger' | 'warning' | 'info' | 'neutral';

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  className?: string;
}

export function Badge({ variant, children, className }: BadgeProps) {
  const variantStyles = {
    success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500',
    danger: 'bg-red-500/20 text-red-400 border-red-500',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500',
    neutral: 'bg-gray-500/20 text-gray-400 border-gray-500',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
```

---

### Molecules (Simple Combinations)

#### Card Component

```typescript
import { ReactNode } from 'react';
import { cn } from '@/utils/classnames';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({
  title,
  subtitle,
  children,
  footer,
  className,
  onClick,
}: CardProps) {
  return (
    <div
      className={cn(
        'bg-gray-800 rounded-lg border border-gray-700 shadow-xl overflow-hidden',
        onClick && 'cursor-pointer hover:bg-gray-700/50 transition-colors',
        className
      )}
      onClick={onClick}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-700">
          {title && (
            <h3 className="text-xl font-semibold text-white">{title}</h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-gray-400">{subtitle}</p>
          )}
        </div>
      )}
      
      <div className="px-6 py-4">
        {children}
      </div>
      
      {footer && (
        <div className="px-6 py-3 bg-gray-900 border-t border-gray-700">
          {footer}
        </div>
      )}
    </div>
  );
}
```

---

#### StatCard Component

```typescript
import { ReactNode } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  change?: number;
  icon?: ReactNode;
}

export function StatCard({ label, value, change, icon }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-400">{label}</h3>
        {icon && (
          <div className="bg-primary/20 p-2 rounded-lg">
            {icon}
          </div>
        )}
      </div>
      
      <div className="text-3xl font-bold text-white mb-2">
        {value}
      </div>
      
      {change !== undefined && (
        <div className="flex items-center text-sm">
          {isPositive ? (
            <TrendingUp className="w-4 h-4 text-emerald-400 mr-1" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
          )}
          <span className={isPositive ? 'text-emerald-400' : 'text-red-400'}>
            {Math.abs(change).toFixed(2)}%
          </span>
        </div>
      )}
    </div>
  );
}
```

---

### Organisms (Complex Components)

#### DataTable Component

```typescript
import { ReactNode } from 'react';

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  isLoading?: boolean;
}

export function DataTable<T extends { id: string }>({
  data,
  columns,
  onRowClick,
  isLoading,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        <p className="mt-4 text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-900">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {data.map((item) => (
              <tr
                key={item.id}
                onClick={() => onRowClick?.(item)}
                className={onRowClick ? 'hover:bg-gray-700/50 cursor-pointer transition-colors' : ''}
              >
                {columns.map((column) => (
                  <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {column.render ? column.render(item) : (item as any)[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400">No data available</p>
        </div>
      )}
    </div>
  );
}
```

---

## Utility Functions

### Currency Formatting

**File:** `src/utils/format.ts`

```typescript
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  decimals: number = 2
): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(amount);
}

export function formatCrypto(amount: number, symbol: string): string {
  // Format with appropriate decimal places based on value
  const decimals = amount < 0.01 ? 8 : amount < 1 ? 6 : amount < 100 ? 4 : 2;
  
  return `${amount.toFixed(decimals)} ${symbol}`;
}

export function formatPercent(value: number, decimals: number = 2): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}
```

---

### Date Formatting

```typescript
import { formatDistanceToNow, format } from 'date-fns';

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return format(d, 'MMM dd, yyyy');
}

export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return format(d, 'MMM dd, yyyy HH:mm:ss');
}

export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}
```

---

## Component Usage Examples

### Portfolio Card Example

```tsx
import { StatCard } from '@/components/molecules/StatCard';
import { Wallet } from 'lucide-react';
import { formatCurrency, formatPercent } from '@/utils/format';

function PortfolioSummary({ portfolio }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <StatCard
        label="Total Value"
        value={formatCurrency(portfolio.totalValue)}
        icon={<Wallet className="w-5 h-5 text-primary-light" />}
      />
      
      <StatCard
        label="Profit/Loss"
        value={formatCurrency(portfolio.profitLoss)}
        change={portfolio.profitLossPercent}
      />
      
      <StatCard
        label="Asset Count"
        value={portfolio.assetCount}
      />
    </div>
  );
}
```

---

**Component Library Maintained by:** Cursor AI  
**Storybook:** https://storybook.cryptovault.com  
**Design Tokens:** `src/styles/tokens.ts`

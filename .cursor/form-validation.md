# Form Validation & Error Handling
**AI Agent:** Cursor  
**Last Updated:** February 20, 2026  
**Validation Library:** React Hook Form + Zod  
**UX Pattern:** Inline validation with helpful messages

## Overview

CryptoVault uses **React Hook Form** for form state management and **Zod** for schema validation. This combination provides:
- Type-safe validation
- Excellent performance (minimal re-renders)
- Clear error messages
- Accessibility-first approach

---

## Setup

### Installation

```bash
npm install react-hook-form zod @hookform/resolvers
```

### Basic Configuration

```tsx
// lib/validation.ts
import { z } from 'zod';

// Reusable validation schemas
export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Invalid email address');

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

export const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters')
  .max(20, 'Username must be at most 20 characters')
  .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores');
```

---

## Registration Form Example

### Complete Form with Validation

```tsx
// components/auth/RegisterForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { emailSchema, passwordSchema, usernameSchema } from '@/lib/validation';

// Define schema
const registerSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
  agreeToTerms: z.boolean().refine(val => val === true, {
    message: 'You must agree to the terms and conditions',
  }),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'], // Error will be attached to confirmPassword field
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
    setError,
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: 'onBlur', // Validate on blur
    reValidateMode: 'onChange', // Re-validate on change after first blur
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    try {
      const response = await fetch('/api/v2/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        
        // Server-side validation errors
        if (error.field === 'email' && error.code === 'EMAIL_EXISTS') {
          setError('email', {
            type: 'manual',
            message: 'This email is already registered',
          });
          return;
        }
        
        throw new Error(error.message);
      }

      // Success - redirect to dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Registration error:', error);
      // Show generic error toast
      toast.error('Registration failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Username Field */}
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-gray-200">
          Username
        </label>
        <input
          id="username"
          type="text"
          {...register('username')}
          aria-invalid={errors.username ? 'true' : 'false'}
          aria-describedby={errors.username ? 'username-error' : undefined}
          className={`
            mt-1 block w-full px-4 py-3 rounded-lg
            bg-gray-800 border
            ${errors.username ? 'border-red-500' : 'border-gray-700'}
            focus:outline-none focus:ring-2 focus:ring-purple-500
            transition-colors
          `}
        />
        {errors.username && (
          <p id="username-error" role="alert" className="mt-1 text-sm text-red-500">
            {errors.username.message}
          </p>
        )}
      </div>

      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-200">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
          className={`
            mt-1 block w-full px-4 py-3 rounded-lg
            bg-gray-800 border
            ${errors.email ? 'border-red-500' : 'border-gray-700'}
            focus:outline-none focus:ring-2 focus:ring-purple-500
          `}
        />
        {errors.email && (
          <p id="email-error" role="alert" className="mt-1 text-sm text-red-500">
            {errors.email.message}
          </p>
        )}
      </div>

      {/* Password Field with Strength Indicator */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-200">
          Password
        </label>
        <input
          id="password"
          type="password"
          {...register('password')}
          aria-invalid={errors.password ? 'true' : 'false'}
          aria-describedby="password-error password-requirements"
          className={`
            mt-1 block w-full px-4 py-3 rounded-lg
            bg-gray-800 border
            ${errors.password ? 'border-red-500' : 'border-gray-700'}
            focus:outline-none focus:ring-2 focus:ring-purple-500
          `}
        />
        
        {/* Password Requirements */}
        <div id="password-requirements" className="mt-2 space-y-1 text-xs text-gray-400">
          <PasswordRequirement 
            met={password?.length >= 8} 
            text="At least 8 characters" 
          />
          <PasswordRequirement 
            met={/[A-Z]/.test(password || '')} 
            text="One uppercase letter" 
          />
          <PasswordRequirement 
            met={/[a-z]/.test(password || '')} 
            text="One lowercase letter" 
          />
          <PasswordRequirement 
            met={/[0-9]/.test(password || '')} 
            text="One number" 
          />
          <PasswordRequirement 
            met={/[^A-Za-z0-9]/.test(password || '')} 
            text="One special character" 
          />
        </div>
        
        {errors.password && (
          <p id="password-error" role="alert" className="mt-1 text-sm text-red-500">
            {errors.password.message}
          </p>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-200">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          {...register('confirmPassword')}
          aria-invalid={errors.confirmPassword ? 'true' : 'false'}
          aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
          className={`
            mt-1 block w-full px-4 py-3 rounded-lg
            bg-gray-800 border
            ${errors.confirmPassword ? 'border-red-500' : 'border-gray-700'}
            focus:outline-none focus:ring-2 focus:ring-purple-500
          `}
        />
        {errors.confirmPassword && (
          <p id="confirm-password-error" role="alert" className="mt-1 text-sm text-red-500">
            {errors.confirmPassword.message}
          </p>
        )}
      </div>

      {/* Terms Checkbox */}
      <div className="flex items-start">
        <input
          id="agreeToTerms"
          type="checkbox"
          {...register('agreeToTerms')}
          aria-invalid={errors.agreeToTerms ? 'true' : 'false'}
          aria-describedby={errors.agreeToTerms ? 'terms-error' : undefined}
          className="mt-1 h-4 w-4 rounded border-gray-700 bg-gray-800 text-purple-600 focus:ring-2 focus:ring-purple-500"
        />
        <label htmlFor="agreeToTerms" className="ml-2 block text-sm text-gray-300">
          I agree to the{' '}
          <a href="/terms" className="text-purple-400 hover:text-purple-300">
            Terms and Conditions
          </a>
        </label>
      </div>
      {errors.agreeToTerms && (
        <p id="terms-error" role="alert" className="text-sm text-red-500">
          {errors.agreeToTerms.message}
        </p>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting || !isValid}
        className={`
          w-full px-6 py-3 rounded-lg font-semibold
          transition-all duration-200
          ${
            isSubmitting || !isValid
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-purple-600 text-white hover:bg-purple-700 active:bg-purple-800'
          }
        `}
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center">
            <LoadingSpinner className="mr-2" />
            Creating account...
          </span>
        ) : (
          'Create Account'
        )}
      </button>
    </form>
  );
}

// Password requirement indicator component
function PasswordRequirement({ met, text }: { met: boolean; text: string }) {
  return (
    <div className="flex items-center">
      {met ? (
        <CheckIcon className="w-4 h-4 text-green-500 mr-2" />
      ) : (
        <XIcon className="w-4 h-4 text-gray-500 mr-2" />
      )}
      <span className={met ? 'text-green-500' : 'text-gray-500'}>{text}</span>
    </div>
  );
}
```

---

## Transaction Form Example

### Dynamic Amount Validation

```tsx
// components/portfolio/AddTransactionForm.tsx
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const transactionSchema = z.object({
  symbol: z.string().min(1, 'Please select a cryptocurrency'),
  type: z.enum(['buy', 'sell'], {
    required_error: 'Please select transaction type',
  }),
  amount: z
    .number({ invalid_type_error: 'Amount must be a number' })
    .positive('Amount must be greater than 0')
    .max(1000000, 'Amount too large'),
  price: z
    .number({ invalid_type_error: 'Price must be a number' })
    .positive('Price must be greater than 0'),
  date: z.date({
    required_error: 'Please select a date',
    invalid_type_error: 'Invalid date',
  }),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
});

type TransactionFormData = z.infer<typeof transactionSchema>;

export function AddTransactionForm() {
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  
  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      type: 'buy',
      date: new Date(),
    },
  });

  const selectedSymbol = watch('symbol');
  const amount = watch('amount');
  const price = watch('price');

  // Fetch current price when symbol changes
  useEffect(() => {
    if (selectedSymbol) {
      fetch(`/api/v2/prices/${selectedSymbol}`)
        .then(res => res.json())
        .then(data => {
          setCurrentPrice(data.price);
          setValue('price', data.price); // Auto-fill with current price
        });
    }
  }, [selectedSymbol, setValue]);

  const totalValue = amount && price ? amount * price : 0;

  const onSubmit = async (data: TransactionFormData) => {
    try {
      await fetch('/api/v2/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      toast.success('Transaction added successfully!');
      // Reset form or close modal
    } catch (error) {
      toast.error('Failed to add transaction');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Transaction Type Toggle */}
      <div>
        <label className="block text-sm font-medium text-gray-200 mb-2">
          Transaction Type
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setValue('type', 'buy')}
            className={`
              flex-1 px-4 py-2 rounded-lg font-medium transition-colors
              ${
                watch('type') === 'buy'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }
            `}
          >
            Buy
          </button>
          <button
            type="button"
            onClick={() => setValue('type', 'sell')}
            className={`
              flex-1 px-4 py-2 rounded-lg font-medium transition-colors
              ${
                watch('type') === 'sell'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }
            `}
          >
            Sell
          </button>
        </div>
      </div>

      {/* Cryptocurrency Select */}
      <div>
        <label htmlFor="symbol" className="block text-sm font-medium text-gray-200">
          Cryptocurrency
        </label>
        <select
          id="symbol"
          {...register('symbol')}
          className="mt-1 block w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Select cryptocurrency</option>
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
          <option value="ADA">Cardano (ADA)</option>
          <option value="SOL">Solana (SOL)</option>
        </select>
        {errors.symbol && (
          <p role="alert" className="mt-1 text-sm text-red-500">
            {errors.symbol.message}
          </p>
        )}
      </div>

      {/* Amount Input */}
      <div>
        <label htmlFor="amount" className="block text-sm font-medium text-gray-200">
          Amount
        </label>
        <Controller
          name="amount"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              id="amount"
              type="number"
              step="0.00000001"
              onChange={e => field.onChange(parseFloat(e.target.value))}
              className={`
                mt-1 block w-full px-4 py-3 rounded-lg
                bg-gray-800 border
                ${errors.amount ? 'border-red-500' : 'border-gray-700'}
                focus:outline-none focus:ring-2 focus:ring-purple-500
              `}
            />
          )}
        />
        {errors.amount && (
          <p role="alert" className="mt-1 text-sm text-red-500">
            {errors.amount.message}
          </p>
        )}
      </div>

      {/* Price Input */}
      <div>
        <label htmlFor="price" className="block text-sm font-medium text-gray-200">
          Price (USD)
        </label>
        <div className="relative">
          <Controller
            name="price"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                id="price"
                type="number"
                step="0.01"
                onChange={e => field.onChange(parseFloat(e.target.value))}
                className={`
                  mt-1 block w-full px-4 py-3 rounded-lg
                  bg-gray-800 border
                  ${errors.price ? 'border-red-500' : 'border-gray-700'}
                  focus:outline-none focus:ring-2 focus:ring-purple-500
                `}
              />
            )}
          />
          {currentPrice > 0 && (
            <div className="absolute right-3 top-4 text-sm text-gray-400">
              Current: ${currentPrice.toLocaleString()}
            </div>
          )}
        </div>
        {errors.price && (
          <p role="alert" className="mt-1 text-sm text-red-500">
            {errors.price.message}
          </p>
        )}
      </div>

      {/* Total Value Display */}
      {totalValue > 0 && (
        <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Total Value:</span>
            <span className="text-2xl font-bold text-white">
              ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>
      )}

      {/* Date Picker */}
      <div>
        <label htmlFor="date" className="block text-sm font-medium text-gray-200">
          Date
        </label>
        <Controller
          name="date"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              id="date"
              type="datetime-local"
              value={field.value ? new Date(field.value).toISOString().slice(0, 16) : ''}
              onChange={e => field.onChange(new Date(e.target.value))}
              className="mt-1 block w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          )}
        />
        {errors.date && (
          <p role="alert" className="mt-1 text-sm text-red-500">
            {errors.date.message}
          </p>
        )}
      </div>

      {/* Notes (Optional) */}
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-200">
          Notes (Optional)
        </label>
        <textarea
          id="notes"
          {...register('notes')}
          rows={3}
          className="mt-1 block w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="Add any notes about this transaction..."
        />
        {errors.notes && (
          <p role="alert" className="mt-1 text-sm text-red-500">
            {errors.notes.message}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? 'Adding Transaction...' : 'Add Transaction'}
      </button>
    </form>
  );
}
```

---

## Custom Validation Rules

### Async Email Availability Check

```tsx
const checkEmailAvailability = async (email: string): Promise<boolean> => {
  const response = await fetch(`/api/v2/auth/check-email?email=${encodeURIComponent(email)}`);
  const data = await response.json();
  return data.available;
};

const registerSchema = z.object({
  email: z
    .string()
    .email('Invalid email')
    .refine(
      async (email) => await checkEmailAvailability(email),
      { message: 'This email is already registered' }
    ),
  // ... other fields
});
```

---

## Error Patterns

### Field-Level Errors

```tsx
// Inline error below field
{errors.fieldName && (
  <p role="alert" className="mt-1 text-sm text-red-500">
    {errors.fieldName.message}
  </p>
)}
```

### Form-Level Errors

```tsx
// Top of form
{errors.root && (
  <div role="alert" className="p-4 bg-red-900/20 border border-red-500 rounded-lg">
    <p className="text-red-500">{errors.root.message}</p>
  </div>
)}
```

### Toast Notifications

```tsx
import { toast } from 'react-hot-toast';

// Success
toast.success('Transaction added successfully!');

// Error
toast.error('Failed to save changes. Please try again.');

// Custom
toast.custom((t) => (
  <div className="bg-gray-800 px-6 py-4 rounded-lg shadow-lg">
    <p className="text-white">Custom message</p>
  </div>
));
```

---

## Testing

```tsx
// __tests__/RegisterForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RegisterForm } from '@/components/auth/RegisterForm';

describe('RegisterForm', () => {
  it('shows validation errors for invalid inputs', async () => {
    render(<RegisterForm />);
    
    const submitButton = screen.getByRole('button', { name: /create account/i });
    
    // Try to submit empty form
    await userEvent.click(submitButton);
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });
  
  it('validates password requirements', async () => {
    render(<RegisterForm />);
    
    const passwordInput = screen.getByLabelText(/^password$/i);
    
    await userEvent.type(passwordInput, 'weak');
    await userEvent.tab(); // Blur
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });
});
```

---

**Best Practices:**
✅ Validate on blur, re-validate on change  
✅ Show inline errors immediately  
✅ Provide helpful, specific error messages  
✅ Use ARIA attributes for accessibility  
✅ Disable submit until form is valid  
✅ Show loading state during submission  

**Created by:** Cursor AI  
**Last Updated:** February 20, 2026

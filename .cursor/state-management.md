# State Management Architecture
**AI Agent:** Cursor  
**Last Updated:** February 9, 2026  
**Library:** Redux Toolkit + RTK Query

## Redux Store Structure

```typescript
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import authReducer from './slices/authSlice';
import portfolioReducer from './slices/portfolioSlice';
import uiReducer from './slices/uiSlice';
import { api } from './api';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    portfolio: portfolioReducer,
    ui: uiReducer,
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

---

## Slices

### Auth Slice

**File:** `src/store/slices/authSlice.ts`

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; accessToken: string }>
    ) => {
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      state.isAuthenticated = true;
      state.isLoading = false;
    },
    
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.isAuthenticated = false;
    },
    
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { setCredentials, logout, setLoading } = authSlice.actions;
export default authSlice.reducer;

// Selectors
export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAuthToken = (state: RootState) => state.auth.accessToken;
```

---

### Portfolio Slice

```typescript
import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { PortfolioService } from '@/services/portfolio';

interface Asset {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  value: number;
  currentPrice: number;
}

interface PortfolioState {
  assets: Asset[];
  totalValue: number;
  profitLoss: number;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: PortfolioState = {
  assets: [],
  totalValue: 0,
  profitLoss: 0,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

// Async thunks
export const fetchPortfolio = createAsyncThunk(
  'portfolio/fetch',
  async (userId: string) => {
    const response = await PortfolioService.getPortfolio(userId);
    return response;
  }
);

export const addAsset = createAsyncThunk(
  'portfolio/addAsset',
  async ({ userId, asset }: { userId: string; asset: any }) => {
    const response = await PortfolioService.addAsset(userId, asset);
    return response;
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    updateAssetPrice: (
      state,
      action: PayloadAction<{ symbol: string; price: number }>
    ) => {
      const asset = state.assets.find((a) => a.symbol === action.payload.symbol);
      if (asset) {
        asset.currentPrice = action.payload.price;
        asset.value = asset.quantity * action.payload.price;
      }
      
      // Recalculate total
      state.totalValue = state.assets.reduce((sum, a) => sum + a.value, 0);
      state.lastUpdated = new Date().toISOString();
    },
    
    clearPortfolio: (state) => {
      return initialState;
    },
  },
  
  extraReducers: (builder) => {
    builder
      // Fetch portfolio
      .addCase(fetchPortfolio.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.assets = action.payload.assets;
        state.totalValue = action.payload.totalValue;
        state.profitLoss = action.payload.profitLoss;
        state.isLoading = false;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch portfolio';
      })
      
      // Add asset
      .addCase(addAsset.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(addAsset.fulfilled, (state, action) => {
        state.assets.push(action.payload);
        state.isLoading = false;
      })
      .addCase(addAsset.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to add asset';
      });
  },
});

export const { updateAssetPrice, clearPortfolio } = portfolioSlice.actions;
export default portfolioSlice.reducer;

// Selectors
export const selectAssets = (state: RootState) => state.portfolio.assets;
export const selectTotalValue = (state: RootState) => state.portfolio.totalValue;
export const selectProfitLoss = (state: RootState) => state.portfolio.profitLoss;
export const selectPortfolioLoading = (state: RootState) => state.portfolio.isLoading;
```

---

### UI Slice (Toast notifications, modals, etc.)

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

interface UIState {
  toasts: Toast[];
  sidebarOpen: boolean;
  theme: 'dark' | 'light';
  modal: {
    isOpen: boolean;
    type: string | null;
    data: any;
  };
}

const initialState: UIState = {
  toasts: [],
  sidebarOpen: true,
  theme: 'dark',
  modal: {
    isOpen: false,
    type: null,
    data: null,
  },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    addToast: (state, action: PayloadAction<Omit<Toast, 'id'>>) => {
      state.toasts.push({
        id: Date.now().toString(),
        ...action.payload,
      });
    },
    
    removeToast: (state, action: PayloadAction<string>) => {
      state.toasts = state.toasts.filter((t) => t.id !== action.payload);
    },
    
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setTheme: (state, action: PayloadAction<'dark' | 'light'>) => {
      state.theme = action.payload;
    },
    
    openModal: (state, action: PayloadAction<{ type: string; data?: any }>) => {
      state.modal = {
        isOpen: true,
        type: action.payload.type,
        data: action.payload.data || null,
      };
    },
    
    closeModal: (state) => {
      state.modal = {
        isOpen: false,
        type: null,
        data: null,
      };
    },
  },
});

export const {
  addToast,
  removeToast,
  toggleSidebar,
  setTheme,
  openModal,
  closeModal,
} = uiSlice.actions;

export default uiSlice.reducer;
```

---

## RTK Query API

**File:** `src/store/api/index.ts`

```typescript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../index';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Portfolio', 'Assets', 'Transactions'],
  endpoints: (builder) => ({
    // Portfolio
    getPortfolio: builder.query({
      query: (userId) => `/portfolios/${userId}`,
      providesTags: ['Portfolio'],
    }),
    
    // Assets
    addAsset: builder.mutation({
      query: ({ userId, asset }) => ({
        url: `/portfolios/${userId}/assets`,
        method: 'POST',
        body: asset,
      }),
      invalidatesTags: ['Portfolio', 'Assets'],
    }),
    
    updateAsset: builder.mutation({
      query: ({ userId, assetId, updates }) => ({
        url: `/portfolios/${userId}/assets/${assetId}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: ['Portfolio', 'Assets'],
    }),
    
    deleteAsset: builder.mutation({
      query: ({ userId, assetId }) => ({
        url: `/portfolios/${userId}/assets/${assetId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Portfolio', 'Assets'],
    }),
    
    // Market data
    getMarketPrices: builder.query({
      query: () => '/market/prices',
      // Poll every 10 seconds
      pollingInterval: 10000,
    }),
    
    // Trading
    placeOrder: builder.mutation({
      query: (order) => ({
        url: '/trading/orders',
        method: 'POST',
        body: order,
      }),
      invalidatesTags: ['Portfolio', 'Transactions'],
    }),
  }),
});

export const {
  useGetPortfolioQuery,
  useAddAssetMutation,
  useUpdateAssetMutation,
  useDeleteAssetMutation,
  useGetMarketPricesQuery,
  usePlaceOrderMutation,
} = api;
```

---

## Custom Hooks

### Typed Redux Hooks

**File:** `src/hooks/redux.ts`

```typescript
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '@/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

---

### Toast Hook

```typescript
import { useCallback } from 'react';
import { useAppDispatch } from './redux';
import { addToast, removeToast } from '@/store/slices/uiSlice';

export function useToast() {
  const dispatch = useAppDispatch();

  const success = useCallback(
    (message: string) => {
      dispatch(addToast({ message, type: 'success' }));
    },
    [dispatch]
  );

  const error = useCallback(
    (message: string) => {
      dispatch(addToast({ message, type: 'error' }));
    },
    [dispatch]
  );

  const info = useCallback(
    (message: string) => {
      dispatch(addToast({ message, type: 'info' }));
    },
    [dispatch]
  );

  const remove = useCallback(
    (id: string) => {
      dispatch(removeToast(id));
    },
    [dispatch]
  );

  return { success, error, info, remove };
}
```

---

## Usage Examples

### In Components

```typescript
import { useAppSelector, useAppDispatch } from '@/hooks/redux';
import { useGetPortfolioQuery, useAddAssetMutation } from '@/store/api';
import { updateAssetPrice } from '@/store/slices/portfolioSlice';
import { useToast } from '@/hooks/useToast';

function PortfolioPage() {
  const user = useAppSelector(selectCurrentUser);
  const dispatch = useAppDispatch();
  const toast = useToast();
  
  // RTK Query - automatic loading, caching, refetching
  const { data: portfolio, isLoading, error } = useGetPortfolioQuery(user.id);
  
  // Mutations
  const [addAsset, { isLoading: isAdding }] = useAddAssetMutation();
  
  const handleAddAsset = async (asset: any) => {
    try {
      await addAsset({ userId: user.id, asset }).unwrap();
      toast.success('Asset added successfully');
    } catch (err) {
      toast.error('Failed to add asset');
    }
  };
  
  // WebSocket price updates
  useEffect(() => {
    const ws = new WebSocket('wss://api.cryptovault.com/ws/prices');
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      dispatch(updateAssetPrice({
        symbol: update.symbol,
        price: update.price,
      }));
    };
    
    return () => ws.close();
  }, [dispatch]);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>Portfolio Value: ${portfolio.totalValue}</h1>
      {/* ... */}
    </div>
  );
}
```

---

## Persistence

**File:** `src/store/middleware/persistence.ts`

```typescript
import { Middleware } from '@reduxjs/toolkit';

// Persist certain slices to localStorage
export const persistenceMiddleware: Middleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Save auth state
  if (action.type.startsWith('auth/')) {
    const { auth } = store.getState();
    localStorage.setItem('auth', JSON.stringify({
      user: auth.user,
      accessToken: auth.accessToken,
    }));
  }
  
  // Save UI preferences
  if (action.type.startsWith('ui/')) {
    const { ui } = store.getState();
    localStorage.setItem('ui-prefs', JSON.stringify({
      theme: ui.theme,
      sidebarOpen: ui.sidebarOpen,
    }));
  }
  
  return result;
};

// Rehydrate on app start
export function rehydrateStore() {
  const authData = localStorage.getItem('auth');
  const uiPrefs = localStorage.getItem('ui-prefs');
  
  return {
    auth: authData ? JSON.parse(authData) : undefined,
    ui: uiPrefs ? JSON.parse(uiPrefs) : undefined,
  };
}
```

---

**State Management by:** Cursor AI  
**Redux DevTools:** Enabled in development  
**Documentation:** https://redux-toolkit.js.org

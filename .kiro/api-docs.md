# API Documentation - CryptoVault REST API
**AI Agent:** Kiro  
**API Version:** 1.2.0  
**Base URL:** `https://api.cryptovault.com`  
**Protocol:** HTTPS only (TLS 1.3)  
**Documentation Updated:** February 15, 2026

## Overview

The CryptoVault API provides programmatic access to cryptocurrency portfolio management, trading, and market data. All endpoints follow RESTful principles and return JSON responses.

### Key Features
- 🔐 Secure JWT-based authentication
- 📊 Real-time portfolio tracking
- 💹 Multi-exchange trading
- 📈 Historical market data
- 🔔 WebSocket streaming for live updates
- ⚡ Average response time: <100ms

## Authentication

### Bearer Token (JWT)

All authenticated endpoints require a JWT token in the Authorization header.

**Login to obtain token:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Usage:**
```http
GET /api/portfolios/user-123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh

Access tokens expire after 15 minutes. Use refresh token to obtain new access token.

```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newuser@example.com",
  "email_verified": false,
  "created_at": "2026-02-15T10:30:00Z"
}
```

**Errors:**
- `400` - Validation error (weak password, invalid email)
- `409` - Email already registered

---

#### POST /api/auth/login
Authenticate and receive access token.

**Rate Limit:** 5 requests per minute

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "user"
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `429` - Too many login attempts (rate limited)

---

### Portfolio Endpoints

#### GET /api/portfolios/{user_id}
Retrieve user's complete portfolio with current valuations.

**Authentication:** Required  
**Rate Limit:** 100 requests per minute

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string (UUID) | Yes | User identifier |
| `include_history` | boolean | No | Include historical data (default: false) |

**Response (200 OK):**
```json
{
  "id": "portfolio-abc-123",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_value": 45678.92,
  "total_invested": 35000.00,
  "profit_loss": 10678.92,
  "profit_loss_percent": 30.51,
  "asset_count": 8,
  "diversification_score": 72.5,
  "assets": [
    {
      "id": "asset-001",
      "symbol": "BTC",
      "name": "Bitcoin",
      "quantity": 0.75,
      "avg_buy_price": 42000.00,
      "current_price": 48500.00,
      "value": 36375.00,
      "profit_loss": 4875.00,
      "profit_loss_percent": 15.48,
      "allocation_percent": 79.62,
      "logo_url": "https://cdn.cryptovault.com/logos/btc.png"
    },
    {
      "id": "asset-002",
      "symbol": "ETH",
      "name": "Ethereum",
      "quantity": 3.5,
      "avg_buy_price": 2200.00,
      "current_price": 2650.00,
      "value": 9275.00,
      "profit_loss": 1575.00,
      "profit_loss_percent": 20.45,
      "allocation_percent": 20.31,
      "logo_url": "https://cdn.cryptovault.com/logos/eth.png"
    }
  ],
  "updated_at": "2026-02-15T14:23:45Z"
}
```

**Errors:**
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (not your portfolio)
- `404` - Portfolio not found

---

#### POST /api/portfolios/{user_id}/assets
Add a cryptocurrency asset to portfolio.

**Authentication:** Required  
**Rate Limit:** 50 requests per minute

**Request:**
```json
{
  "symbol": "SOL",
  "quantity": 10.5,
  "avg_buy_price": 98.50,
  "purchase_date": "2026-02-10T00:00:00Z",
  "notes": "Purchased during dip"
}
```

**Response (201 Created):**
```json
{
  "id": "asset-003",
  "symbol": "SOL",
  "name": "Solana",
  "quantity": 10.5,
  "avg_buy_price": 98.50,
  "current_price": 105.30,
  "value": 1105.65,
  "profit_loss": 71.40,
  "profit_loss_percent": 6.90,
  "created_at": "2026-02-15T14:30:00Z"
}
```

**Validation Rules:**
- `symbol`: Valid cryptocurrency symbol (uppercase, 2-10 chars)
- `quantity`: Positive number, max 8 decimal places
- `avg_buy_price`: Positive number, max 8 decimal places

**Errors:**
- `400` - Validation error
- `409` - Asset already exists in portfolio

---

#### PUT /api/portfolios/{user_id}/assets/{asset_id}
Update asset quantity or average buy price.

**Request:**
```json
{
  "quantity": 12.0,
  "avg_buy_price": 100.00
}
```

**Response (200 OK):**
```json
{
  "id": "asset-003",
  "symbol": "SOL",
  "quantity": 12.0,
  "avg_buy_price": 100.00,
  "current_price": 105.30,
  "value": 1263.60,
  "updated_at": "2026-02-15T14:35:00Z"
}
```

---

#### DELETE /api/portfolios/{user_id}/assets/{asset_id}
Remove asset from portfolio.

**Response (204 No Content)**

**Errors:**
- `404` - Asset not found

---

### Market Data Endpoints

#### GET /api/market/prices
Get current prices for all supported cryptocurrencies.

**Authentication:** Not required  
**Rate Limit:** 1000 requests per minute  
**Cache:** 10 seconds

**Response (200 OK):**
```json
{
  "timestamp": "2026-02-15T14:40:00Z",
  "prices": {
    "BTC": {
      "price": 48500.00,
      "change_24h": 2.35,
      "change_24h_percent": 5.10,
      "volume_24h": 28500000000,
      "market_cap": 950000000000
    },
    "ETH": {
      "price": 2650.00,
      "change_24h": -45.00,
      "change_24h_percent": -1.67,
      "volume_24h": 15200000000,
      "market_cap": 318000000000
    }
  }
}
```

---

#### GET /api/market/prices/{symbol}
Get current price for specific cryptocurrency.

**Parameters:**
- `symbol`: Cryptocurrency symbol (e.g., BTC, ETH, SOL)

**Response (200 OK):**
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price": 48500.00,
  "change_1h": 0.45,
  "change_24h": 5.10,
  "change_7d": 8.75,
  "volume_24h": 28500000000,
  "market_cap": 950000000000,
  "circulating_supply": 19500000,
  "total_supply": 21000000,
  "max_supply": 21000000,
  "all_time_high": 69000.00,
  "all_time_high_date": "2021-11-10",
  "timestamp": "2026-02-15T14:42:00Z"
}
```

---

#### GET /api/market/{symbol}/chart
Get historical price data for charting.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `symbol` | string | Yes | Cryptocurrency symbol |
| `interval` | string | No | Time interval: 1m, 5m, 1h, 1d (default: 1h) |
| `start` | ISO 8601 | No | Start date (default: 7 days ago) |
| `end` | ISO 8601 | No | End date (default: now) |

**Response (200 OK):**
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2026-02-15T10:00:00Z",
      "open": 47800.00,
      "high": 48200.00,
      "low": 47650.00,
      "close": 48100.00,
      "volume": 450000000
    },
    {
      "timestamp": "2026-02-15T11:00:00Z",
      "open": 48100.00,
      "high": 48600.00,
      "low": 48000.00,
      "close": 48500.00,
      "volume": 520000000
    }
  ]
}
```

---

### Trading Endpoints

#### POST /api/trading/orders
Place a new trading order.

**Authentication:** Required  
**Rate Limit:** 10 requests per minute

**Request (Market Order):**
```json
{
  "exchange": "binance",
  "symbol": "BTC",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.05
}
```

**Request (Limit Order):**
```json
{
  "exchange": "binance",
  "symbol": "ETH",
  "side": "SELL",
  "type": "LIMIT",
  "quantity": 1.5,
  "price": 2700.00,
  "time_in_force": "GTC"
}
```

**Response (201 Created):**
```json
{
  "id": "order-xyz-789",
  "exchange": "binance",
  "symbol": "BTC",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.05,
  "status": "FILLED",
  "filled_quantity": 0.05,
  "avg_fill_price": 48520.00,
  "total_cost": 2426.00,
  "fee": 2.43,
  "fee_currency": "USDT",
  "created_at": "2026-02-15T14:50:00Z",
  "updated_at": "2026-02-15T14:50:01Z"
}
```

**Order Status Values:**
- `PENDING` - Order submitted, awaiting execution
- `FILLED` - Order completely filled
- `PARTIALLY_FILLED` - Order partially filled
- `CANCELLED` - Order cancelled by user
- `REJECTED` - Order rejected by exchange
- `EXPIRED` - Order expired (time-in-force)

**Errors:**
- `400` - Invalid order parameters
- `402` - Insufficient funds
- `503` - Exchange unavailable

---

#### GET /api/trading/orders/{order_id}
Get order details and status.

**Response (200 OK):**
```json
{
  "id": "order-xyz-789",
  "exchange": "binance",
  "symbol": "BTC",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.05,
  "status": "FILLED",
  "filled_quantity": 0.05,
  "avg_fill_price": 48520.00,
  "executions": [
    {
      "id": "exec-001",
      "price": 48520.00,
      "quantity": 0.05,
      "fee": 2.43,
      "timestamp": "2026-02-15T14:50:01Z"
    }
  ],
  "created_at": "2026-02-15T14:50:00Z",
  "updated_at": "2026-02-15T14:50:01Z"
}
```

---

#### DELETE /api/trading/orders/{order_id}
Cancel an open order.

**Response (200 OK):**
```json
{
  "id": "order-xyz-789",
  "status": "CANCELLED",
  "cancelled_at": "2026-02-15T14:55:00Z"
}
```

**Errors:**
- `400` - Order already filled or cancelled
- `404` - Order not found

---

#### GET /api/trading/history
Get trade execution history.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `start_date` | ISO 8601 | No | Start date (default: 30 days ago) |
| `end_date` | ISO 8601 | No | End date (default: now) |
| `symbol` | string | No | Filter by cryptocurrency |
| `limit` | integer | No | Max results (default: 50, max: 500) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Response (200 OK):**
```json
{
  "total": 127,
  "limit": 50,
  "offset": 0,
  "trades": [
    {
      "id": "trade-001",
      "order_id": "order-xyz-789",
      "exchange": "binance",
      "symbol": "BTC",
      "side": "BUY",
      "quantity": 0.05,
      "price": 48520.00,
      "total": 2426.00,
      "fee": 2.43,
      "fee_currency": "USDT",
      "timestamp": "2026-02-15T14:50:01Z"
    }
  ]
}
```

---

## WebSocket API

### Real-Time Price Updates

Connect to WebSocket for live price streaming.

**Endpoint:** `wss://api.cryptovault.com/ws/prices`

**Authentication:** Include JWT token as query parameter

```javascript
const ws = new WebSocket('wss://api.cryptovault.com/ws/prices?token=YOUR_JWT_TOKEN');

// Subscribe to symbols
ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['BTC', 'ETH', 'SOL']
  }));
};

// Receive price updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(update);
  /*
  {
    "symbol": "BTC",
    "price": 48520.00,
    "change": 125.50,
    "change_percent": 0.26,
    "timestamp": "2026-02-15T14:50:01Z"
  }
  */
};
```

---

## Error Handling

All errors follow RFC 7807 Problem Details format.

**Error Response Structure:**
```json
{
  "type": "https://api.cryptovault.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid cryptocurrency symbol",
  "instance": "/api/portfolios/user-123/assets",
  "errors": [
    {
      "field": "symbol",
      "message": "Symbol must be uppercase, 2-10 characters"
    }
  ]
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content returned |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

Rate limits are enforced per user per endpoint. Limits reset every minute.

**Headers Returned:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1708005600
```

**Rate Limit Exceeded Response (429):**
```json
{
  "type": "https://api.cryptovault.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per minute",
  "retry_after": 42
}
```

---

## Pagination

List endpoints support pagination using `limit` and `offset` parameters.

**Request:**
```
GET /api/trading/history?limit=50&offset=100
```

**Response includes pagination metadata:**
```json
{
  "total": 347,
  "limit": 50,
  "offset": 100,
  "has_more": true,
  "data": [...]
}
```

---

## SDKs and Libraries

Official SDKs available:

- **Python:** `pip install cryptovault-sdk`
- **JavaScript/TypeScript:** `npm install @cryptovault/sdk`
- **Go:** `go get github.com/cryptovault/go-sdk`

**Example (Python):**
```python
from cryptovault import CryptoVault

client = CryptoVault(api_key='your_api_key')
portfolio = client.portfolios.get(user_id='user-123')
print(f"Total value: ${portfolio.total_value}")
```

---

**API Support:** api-support@cryptovault.com  
**Status Page:** https://status.cryptovault.com  
**Changelog:** https://api.cryptovault.com/changelog

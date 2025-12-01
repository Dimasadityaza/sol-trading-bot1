export interface Wallet {
  id: number
  label: string
  public_key: string
  balance: number
  is_primary: boolean
}

export interface CreateWalletRequest {
  password: string
  label: string
}

export interface ImportWalletRequest {
  private_key?: string
  mnemonic?: string
  password: string
  label: string
}

export interface Trade {
  id: number
  wallet_id: number
  token_address: string
  trade_type: 'buy' | 'sell'
  amount: number
  price: number
  cost?: number
  revenue?: number
  pnl?: number
  signature?: string
  timestamp: string
  strategy?: 'manual' | 'snipe' | 'copy'
}

export interface TokenInfo {
  address: string
  symbol: string
  name: string
  decimals: number
  price: number
  market_cap: number
  liquidity: number
  volume_24h: number
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface SniperConfig {
  id?: number
  wallet_id: number
  buy_amount: number
  slippage: number
  min_liquidity: number
  min_safety_score?: number
  require_mint_renounced: boolean
  require_freeze_renounced: boolean
  max_buy_tax: number
  max_sell_tax: number
  is_active?: boolean
}

export interface SniperConfigRequest {
  wallet_id: number
  buy_amount: number
  slippage: number
  min_liquidity: number
  min_safety_score?: number
  require_mint_renounced: boolean
  require_freeze_renounced: boolean
  max_buy_tax: number
  max_sell_tax: number
}

export interface SniperStartRequest {
  wallet_id: number
  password: string
  platforms?: string[]
}

export interface SniperStatus {
  is_running: boolean
  pools_detected?: number
  tokens_bought?: number
  tokens_skipped?: number
  success_rate?: number
}

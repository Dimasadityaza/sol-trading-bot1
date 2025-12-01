import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useWalletStore } from '@/store/walletStore'
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Percent, Activity } from 'lucide-react'
import axios from 'axios'

interface TradeStats {
  total_trades: number
  total_buys: number
  total_sells: number
  total_volume: number
  total_pnl: number
  win_rate: number
}

interface PnLData {
  total_pnl: number
  realized_pnl: number
  unrealized_pnl: number
  total_invested: number
  total_returned: number
  roi_percentage: number
}

export function Analytics() {
  const { selectedWallet } = useWalletStore()

  const [stats, setStats] = useState<TradeStats | null>(null)
  const [pnl, setPnl] = useState<PnLData | null>(null)
  const [winRate, setWinRate] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (selectedWallet) {
      loadAnalytics()
    }
  }, [selectedWallet])

  const loadAnalytics = async () => {
    if (!selectedWallet) return

    setIsLoading(true)
    try {
      // Load stats
      const statsResponse = await axios.get(
        `http://localhost:8000/analytics/stats?wallet_id=${selectedWallet.id}`
      )
      setStats(statsResponse.data)

      // Load PnL
      const pnlResponse = await axios.get(
        `http://localhost:8000/analytics/pnl?wallet_id=${selectedWallet.id}`
      )
      setPnl(pnlResponse.data)

      // Load win rate
      const winRateResponse = await axios.get(
        `http://localhost:8000/analytics/win-rate?wallet_id=${selectedWallet.id}`
      )
      setWinRate(winRateResponse.data.win_rate)
    } catch (error: any) {
      console.error('Failed to load analytics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  if (!selectedWallet) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Track your trading performance and profits
          </p>
        </div>

        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="py-4">
            <p className="text-yellow-500">
              ⚠️ Please select a wallet from the Wallets page to view analytics
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Trading performance for {selectedWallet.label}
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Activity className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {/* PnL Overview */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total PnL</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  (pnl?.total_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {formatCurrency(pnl?.total_pnl || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatPercent(pnl?.roi_percentage || 0)} ROI
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <Percent className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{winRate.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  Success rate of trades
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_trades || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.total_buys || 0} buys, {stats?.total_sells || 0} sells
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(stats?.total_volume || 0).toFixed(2)} SOL
                </div>
                <p className="text-xs text-muted-foreground">
                  Trading volume
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Stats */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Profit & Loss</CardTitle>
                <CardDescription>Detailed PnL breakdown</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Realized PnL</span>
                  <span className={`text-sm font-semibold ${
                    (pnl?.realized_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatCurrency(pnl?.realized_pnl || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Unrealized PnL</span>
                  <span className={`text-sm font-semibold ${
                    (pnl?.unrealized_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatCurrency(pnl?.unrealized_pnl || 0)}
                  </span>
                </div>
                <div className="h-px bg-border" />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Invested</span>
                  <span className="text-sm font-semibold">
                    {formatCurrency(pnl?.total_invested || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Returned</span>
                  <span className="text-sm font-semibold">
                    {formatCurrency(pnl?.total_returned || 0)}
                  </span>
                </div>
                <div className="h-px bg-border" />
                <div className="flex items-center justify-between">
                  <span className="font-medium">ROI</span>
                  <span className={`font-bold ${
                    (pnl?.roi_percentage || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatPercent(pnl?.roi_percentage || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Trade Statistics</CardTitle>
                <CardDescription>Overview of your trading activity</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-muted-foreground">Buy Trades</span>
                  </div>
                  <span className="text-sm font-semibold">{stats?.total_buys || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingDown className="h-4 w-4 text-red-500" />
                    <span className="text-sm text-muted-foreground">Sell Trades</span>
                  </div>
                  <span className="text-sm font-semibold">{stats?.total_sells || 0}</span>
                </div>
                <div className="h-px bg-border" />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Win Rate</span>
                  <span className={`text-sm font-semibold ${
                    winRate >= 50 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {winRate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Volume</span>
                  <span className="text-sm font-semibold">
                    {(stats?.total_volume || 0).toFixed(2)} SOL
                  </span>
                </div>
                <div className="h-px bg-border" />
                <div className="flex items-center justify-between">
                  <span className="font-medium">Total PnL</span>
                  <span className={`font-bold ${
                    (stats?.total_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatCurrency(stats?.total_pnl || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Card */}
          <Card className="border-blue-500/20 bg-blue-500/5">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <BarChart3 className="h-5 w-5 text-blue-500 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-blue-500">Analytics Overview</p>
                  <p className="text-sm text-muted-foreground">
                    Track your trading performance, profit & loss, and win rates. Analytics are calculated based on your trade history and current holdings.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

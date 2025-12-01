import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useWalletStore } from '@/store/walletStore'
import { formatNumber, formatCurrency } from '@/lib/utils'
import { TrendingUp, TrendingDown, Wallet, Activity } from 'lucide-react'

export function Dashboard() {
  const { wallets, selectedWallet } = useWalletStore()

  const totalBalance = wallets.reduce((sum, w) => sum + w.balance, 0)
  const totalWallets = wallets.length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your portfolio and trading activity
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Portfolio
            </CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(totalBalance, 4)} SOL
            </div>
            <p className="text-xs text-muted-foreground">
              ≈ {formatCurrency(totalBalance * 100)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Wallets
            </CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalWallets}</div>
            <p className="text-xs text-muted-foreground">
              {selectedWallet ? 'Using ' + selectedWallet.label : 'No wallet selected'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total PnL
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              +0.00 SOL
            </div>
            <p className="text-xs text-muted-foreground">
              +0.00% today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Win Rate
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0%</div>
            <p className="text-xs text-muted-foreground">
              0 trades executed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Active Positions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Positions</CardTitle>
          <CardDescription>Your current token holdings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <Activity className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No active positions</p>
            <p className="text-sm mt-1">Start trading to see your positions here</p>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest transactions and trades</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <Activity className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No recent activity</p>
            <p className="text-sm mt-1">Your trades will appear here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

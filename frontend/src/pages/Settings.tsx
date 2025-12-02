import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Network } from 'lucide-react'

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your bot settings
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Network className="h-5 w-5 text-green-500" />
            <CardTitle>Network Configuration</CardTitle>
          </div>
          <CardDescription>
            Trading bot is configured for Solana Mainnet
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg border bg-green-500/10 border-green-500/30">
              <div>
                <p className="text-sm font-medium">Current Network</p>
                <p className="text-2xl font-bold text-green-500 mt-1">Mainnet</p>
              </div>
              <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
            </div>

            <div className="rounded-lg bg-blue-500/10 border border-blue-500/20 p-4">
              <p className="text-sm text-blue-600 dark:text-blue-400">
                <strong>Info:</strong> This bot is configured for Solana Mainnet only.
                All transactions use real SOL.
              </p>
            </div>

            <div className="text-xs text-muted-foreground space-y-1">
              <p>• RPC Endpoint: https://api.mainnet-beta.solana.com</p>
              <p>• All wallet operations use mainnet</p>
              <p>• Real SOL transactions</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

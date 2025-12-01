import { useWalletStore } from '@/store/walletStore'
import { Button } from '@/components/ui/button'
import { truncateAddress, formatNumber } from '@/lib/utils'
import { Wallet, RefreshCw } from 'lucide-react'

export function TopBar() {
  const { selectedWallet, wallets } = useWalletStore()

  return (
    <div className="flex h-16 items-center justify-between border-b bg-card px-6">
      <div className="text-sm text-muted-foreground">
        {/* Breadcrumb or page title can go here */}
      </div>

      <div className="flex items-center gap-4">
        {/* Wallet Selector */}
        {selectedWallet ? (
          <div className="flex items-center gap-3 rounded-lg border bg-secondary/50 px-4 py-2">
            <Wallet className="h-4 w-4 text-primary" />
            <div>
              <div className="text-sm font-medium">{selectedWallet.label}</div>
              <div className="text-xs text-muted-foreground">
                {truncateAddress(selectedWallet.public_key)}
              </div>
            </div>
            <div className="ml-4 border-l pl-4">
              <div className="text-sm font-semibold">
                {formatNumber(selectedWallet.balance, 4)} SOL
              </div>
              <div className="text-xs text-muted-foreground">Balance</div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            No wallet selected
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2 rounded-lg border bg-secondary/30 px-3 py-2">
          <div className="h-2 w-2 rounded-full bg-green-500"></div>
          <span className="text-xs font-medium">Connected</span>
        </div>

        {/* Refresh Button */}
        <Button size="icon" variant="ghost">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

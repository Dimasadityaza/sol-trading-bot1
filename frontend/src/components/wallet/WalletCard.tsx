import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Wallet as WalletType } from '@/types'
import { truncateAddress, formatNumber } from '@/lib/utils'
import { Wallet, Copy, Star, Trash2 } from 'lucide-react'
import { useWalletStore } from '@/store/walletStore'

interface WalletCardProps {
  wallet: WalletType
  onDelete?: (id: number) => void
}

export function WalletCard({ wallet, onDelete }: WalletCardProps) {
  const { selectedWallet, selectWallet } = useWalletStore()
  const isSelected = selectedWallet?.id === wallet.id

  const copyAddress = () => {
    navigator.clipboard.writeText(wallet.public_key)
  }

  return (
    <Card 
      className={`hover:border-primary/50 transition-colors cursor-pointer ${
        isSelected ? 'border-primary' : ''
      }`}
      onClick={() => selectWallet(wallet)}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <Wallet className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{wallet.label}</h3>
                {wallet.is_primary && (
                  <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                )}
              </div>
              <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                <span>{truncateAddress(wallet.public_key, 8)}</span>
                <Button 
                  size="icon" 
                  variant="ghost" 
                  className="h-6 w-6"
                  onClick={(e) => {
                    e.stopPropagation()
                    copyAddress()
                  }}
                >
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>

          {onDelete && (
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 text-destructive hover:bg-destructive/10"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(wallet.id)
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>

        <div className="mt-4 flex items-end justify-between border-t pt-4">
          <div>
            <div className="text-2xl font-bold">
              {formatNumber(wallet.balance, 4)} SOL
            </div>
            <div className="text-sm text-muted-foreground">
              ≈ ${formatNumber(wallet.balance * 100, 2)} USD
            </div>
          </div>

          {isSelected && (
            <div className="rounded-full bg-primary/20 px-3 py-1 text-xs font-medium text-primary">
              Active
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

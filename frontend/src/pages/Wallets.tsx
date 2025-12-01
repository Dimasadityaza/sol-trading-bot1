import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { WalletCard } from '@/components/wallet/WalletCard'
import { CreateWalletModal } from '@/components/wallet/CreateWalletModal'
import { useWalletStore } from '@/store/walletStore'
import { walletApi } from '@/services/api'
import { Plus, RefreshCw } from 'lucide-react'

export function Wallets() {
  const { wallets, setWallets, removeWallet, setLoading, isLoading } = useWalletStore()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  useEffect(() => {
    loadWallets()
  }, [])

  const loadWallets = async () => {
    setLoading(true)
    try {
      const data = await walletApi.list()
      setWallets(data)
    } catch (error) {
      console.error('Failed to load wallets:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this wallet?')) return

    try {
      await walletApi.delete(id)
      removeWallet(id)
    } catch (error) {
      console.error('Failed to delete wallet:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Wallets</h1>
          <p className="text-muted-foreground">
            Manage your Solana wallets
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={loadWallets}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Wallet
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <RefreshCw className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-muted-foreground">Loading wallets...</p>
        </div>
      ) : wallets.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <Plus className="h-12 w-12 text-primary" />
          </div>
          <h3 className="text-lg font-semibold">No wallets yet</h3>
          <p className="text-muted-foreground mt-1">
            Create your first wallet to get started
          </p>
          <Button 
            className="mt-4"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Wallet
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {wallets.map((wallet) => (
            <WalletCard
              key={wallet.id}
              wallet={wallet}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      <CreateWalletModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  )
}

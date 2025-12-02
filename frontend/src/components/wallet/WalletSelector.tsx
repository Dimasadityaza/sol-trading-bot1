import { useState, useEffect } from 'react'
import { Search, Wallet, RefreshCw } from 'lucide-react'
import { Input } from '@/components/ui/input'
import api from '@/services/api'

interface WalletOption {
  id: number
  label: string
  public_key: string
  balance: number
}

interface WalletSelectorProps {
  value: number | null
  onChange: (walletId: number) => void
  placeholder?: string
}

export function WalletSelector({ value, onChange, placeholder = 'Select a wallet' }: WalletSelectorProps) {
  const [wallets, setWallets] = useState<WalletOption[]>([])
  const [search, setSearch] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadWallets()
  }, [])

  const loadWallets = async () => {
    try {
      setLoading(true)
      const response = await api.get('/wallet/list')
      setWallets(response.data || [])
    } catch (error) {
      console.error('Failed to load wallets:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredWallets = wallets.filter(wallet =>
    wallet.label.toLowerCase().includes(search.toLowerCase()) ||
    wallet.public_key.toLowerCase().includes(search.toLowerCase()) ||
    wallet.id.toString().includes(search)
  )

  const selectedWallet = wallets.find(w => w.id === value)

  return (
    <div className="relative">
      {/* Selected Wallet Display */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 rounded-md border border-input bg-background text-left flex items-center justify-between hover:bg-accent hover:text-accent-foreground transition-colors"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Wallet className="h-4 w-4 flex-shrink-0" />
          {selectedWallet ? (
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{selectedWallet.label}</div>
              <div className="text-xs text-muted-foreground">
                ID: {selectedWallet.id} • {selectedWallet.balance.toFixed(4)} SOL
              </div>
            </div>
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
        </div>
        <div className="flex items-center gap-2 ml-2">
          {loading && <RefreshCw className="h-4 w-4 animate-spin" />}
          <svg
            className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-popover border border-border rounded-md shadow-lg">
          <div className="p-2 border-b border-border">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, address, or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8"
                autoFocus
              />
            </div>
            <button
              type="button"
              onClick={loadWallets}
              className="mt-2 w-full text-xs text-muted-foreground hover:text-foreground flex items-center justify-center gap-1"
            >
              <RefreshCw className="h-3 w-3" />
              Refresh wallets
            </button>
          </div>

          <div className="max-h-60 overflow-y-auto">
            {filteredWallets.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                {search ? 'No wallets found' : 'No wallets available'}
              </div>
            ) : (
              filteredWallets.map(wallet => (
                <button
                  key={wallet.id}
                  type="button"
                  onClick={() => {
                    onChange(wallet.id)
                    setIsOpen(false)
                    setSearch('')
                  }}
                  className={`w-full px-3 py-2 text-left hover:bg-accent transition-colors ${
                    value === wallet.id ? 'bg-accent' : ''
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{wallet.label}</div>
                      <div className="text-xs text-muted-foreground font-mono truncate">
                        {wallet.public_key.slice(0, 8)}...{wallet.public_key.slice(-6)}
                      </div>
                    </div>
                    <div className="flex flex-col items-end flex-shrink-0">
                      <div className="text-xs text-muted-foreground">ID: {wallet.id}</div>
                      <div className="text-sm font-semibold text-green-400">
                        {wallet.balance.toFixed(4)} SOL
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsOpen(false)
            setSearch('')
          }}
        />
      )}
    </div>
  )
}

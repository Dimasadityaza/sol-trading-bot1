import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { walletApi } from '@/services/api'
import { useWalletStore } from '@/store/walletStore'
import { Plus, X, Download } from 'lucide-react'

interface CreateWalletModalProps {
  isOpen: boolean
  onClose: () => void
}

type TabType = 'create' | 'import'

export function CreateWalletModal({ isOpen, onClose }: CreateWalletModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>('create')
  const [label, setLabel] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [privateKey, setPrivateKey] = useState('')
  const [mnemonic, setMnemonic] = useState('')
  const [importType, setImportType] = useState<'private_key' | 'mnemonic'>('private_key')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const { addWallet } = useWalletStore()

  if (!isOpen) return null

  const resetForm = () => {
    setLabel('')
    setPassword('')
    setConfirmPassword('')
    setPrivateKey('')
    setMnemonic('')
    setError('')
  }

  const handleClose = () => {
    resetForm()
    setActiveTab('create')
    onClose()
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)

    try {
      const wallet = await walletApi.create({ password, label })
      addWallet(wallet)
      resetForm()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create wallet')
    } finally {
      setIsLoading(false)
    }
  }

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    if (importType === 'private_key' && !privateKey) {
      setError('Please enter a private key')
      return
    }

    if (importType === 'mnemonic' && !mnemonic) {
      setError('Please enter a mnemonic phrase')
      return
    }

    setIsLoading(true)

    try {
      const wallet = await walletApi.import({
        password,
        label,
        private_key: importType === 'private_key' ? privateKey : undefined,
        mnemonic: importType === 'mnemonic' ? mnemonic : undefined,
      })
      addWallet(wallet)
      resetForm()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import wallet')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {activeTab === 'create' ? 'Create New Wallet' : 'Import Wallet'}
            </CardTitle>
            <Button size="icon" variant="ghost" onClick={handleClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            {activeTab === 'create'
              ? 'Create a new Solana wallet with BIP39 mnemonic'
              : 'Import an existing wallet using private key or mnemonic'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Tabs */}
          <div className="flex mb-6 border-b">
            <button
              type="button"
              onClick={() => {
                setActiveTab('create')
                setError('')
              }}
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                activeTab === 'create'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Plus className="inline-block mr-1 h-4 w-4" />
              Create
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveTab('import')
                setError('')
              }}
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                activeTab === 'import'
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Download className="inline-block mr-1 h-4 w-4" />
              Import
            </button>
          </div>

          {/* Create Form */}
          {activeTab === 'create' && (
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Wallet Label</label>
                <Input
                  type="text"
                  placeholder="My Trading Wallet"
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Password</label>
                <Input
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Minimum 8 characters
                </p>
              </div>

              <div>
                <label className="text-sm font-medium">Confirm Password</label>
                <Input
                  type="password"
                  placeholder="Confirm password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              {error && (
                <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1"
                >
                  {isLoading ? 'Creating...' : 'Create Wallet'}
                </Button>
              </div>
            </form>
          )}

          {/* Import Form */}
          {activeTab === 'import' && (
            <form onSubmit={handleImport} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Wallet Label</label>
                <Input
                  type="text"
                  placeholder="Imported Wallet"
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Import Method</label>
                <div className="flex gap-2 mt-2">
                  <Button
                    type="button"
                    variant={importType === 'private_key' ? 'default' : 'outline'}
                    onClick={() => setImportType('private_key')}
                    className="flex-1"
                    size="sm"
                  >
                    Private Key
                  </Button>
                  <Button
                    type="button"
                    variant={importType === 'mnemonic' ? 'default' : 'outline'}
                    onClick={() => setImportType('mnemonic')}
                    className="flex-1"
                    size="sm"
                  >
                    Mnemonic
                  </Button>
                </div>
              </div>

              {importType === 'private_key' ? (
                <div>
                  <label className="text-sm font-medium">Private Key</label>
                  <Input
                    type="text"
                    placeholder="Enter your private key (base58 or hex)"
                    value={privateKey}
                    onChange={(e) => setPrivateKey(e.target.value)}
                    required
                    className="mt-1"
                  />
                </div>
              ) : (
                <div>
                  <label className="text-sm font-medium">Mnemonic Phrase</label>
                  <textarea
                    placeholder="Enter your 12 or 24 word mnemonic phrase"
                    value={mnemonic}
                    onChange={(e) => setMnemonic(e.target.value)}
                    required
                    className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    rows={3}
                  />
                </div>
              )}

              <div>
                <label className="text-sm font-medium">Password</label>
                <Input
                  type="password"
                  placeholder="Enter password to encrypt wallet"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Minimum 8 characters
                </p>
              </div>

              {error && (
                <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1"
                >
                  {isLoading ? 'Importing...' : 'Import Wallet'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

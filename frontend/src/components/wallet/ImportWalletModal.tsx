import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { walletApi } from '@/services/api'
import { useWalletStore } from '@/store/walletStore'
import { storage } from '@/utils/storage'
import { Download, X, Key, FileText } from 'lucide-react'

interface ImportWalletModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ImportWalletModal({ isOpen, onClose }: ImportWalletModalProps) {
  const [importType, setImportType] = useState<'private_key' | 'mnemonic'>('mnemonic')
  const [label, setLabel] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [privateKey, setPrivateKey] = useState('')
  const [mnemonic, setMnemonic] = useState('')
  const [rememberPassword, setRememberPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const { addWallet } = useWalletStore()

  if (!isOpen) return null

  const handleImport = async (e: React.FormEvent) => {
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

    if (importType === 'private_key' && !privateKey.trim()) {
      setError('Please enter a private key')
      return
    }

    if (importType === 'mnemonic' && !mnemonic.trim()) {
      setError('Please enter a mnemonic phrase')
      return
    }

    setIsLoading(true)

    try {
      const wallet = await walletApi.import({
        password,
        label,
        private_key: importType === 'private_key' ? privateKey.trim() : undefined,
        mnemonic: importType === 'mnemonic' ? mnemonic.trim() : undefined,
      })

      addWallet(wallet)

      // Handle remember password
      if (rememberPassword) {
        storage.savePassword(password)
      }

      // Reset form
      setLabel('')
      setPassword('')
      setConfirmPassword('')
      setPrivateKey('')
      setMnemonic('')
      setRememberPassword(false)
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import wallet')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Import Wallet
            </CardTitle>
            <Button size="icon" variant="ghost" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>
            Import an existing wallet using private key or mnemonic
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleImport} className="space-y-4">
            {/* Import Type Tabs */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setImportType('mnemonic')}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                  importType === 'mnemonic'
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <FileText className="h-4 w-4 mx-auto mb-1" />
                <div className="text-sm font-medium">Mnemonic</div>
                <div className="text-xs text-muted-foreground">12/24 words</div>
              </button>
              <button
                type="button"
                onClick={() => setImportType('private_key')}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                  importType === 'private_key'
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <Key className="h-4 w-4 mx-auto mb-1" />
                <div className="text-sm font-medium">Private Key</div>
                <div className="text-xs text-muted-foreground">Base58</div>
              </button>
            </div>

            {/* Import Input */}
            {importType === 'mnemonic' ? (
              <div>
                <label className="text-sm font-medium">Mnemonic Phrase</label>
                <textarea
                  placeholder="word1 word2 word3 ... (12 or 24 words)"
                  value={mnemonic}
                  onChange={(e) => setMnemonic(e.target.value)}
                  required
                  rows={3}
                  className="mt-1 w-full px-3 py-2 rounded-md border border-border bg-background font-mono text-sm"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Enter your 12 or 24 word mnemonic phrase separated by spaces
                </p>
              </div>
            ) : (
              <div>
                <label className="text-sm font-medium">Private Key</label>
                <Input
                  type="text"
                  placeholder="Base58 encoded private key"
                  value={privateKey}
                  onChange={(e) => setPrivateKey(e.target.value)}
                  required
                  className="mt-1 font-mono text-sm"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  Your private key in Base58 format
                </p>
              </div>
            )}

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

            {/* Remember Password */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="remember-import"
                checked={rememberPassword}
                onChange={(e) => setRememberPassword(e.target.checked)}
                className="h-4 w-4"
              />
              <label htmlFor="remember-import" className="text-sm text-muted-foreground cursor-pointer">
                Remember password (browser only)
              </label>
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
                onClick={onClose}
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

            <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/50 p-3">
              <p className="text-xs text-yellow-500">
                ⚠️ Never share your private key or mnemonic with anyone. Make sure you're on the correct website.
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

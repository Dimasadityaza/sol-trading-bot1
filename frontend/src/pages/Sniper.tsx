import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useWalletStore } from '@/store/walletStore'
import { Target, Play, Square, Settings as SettingsIcon, Shield } from 'lucide-react'
import axios from 'axios'

interface SniperConfig {
  id?: number
  wallet_id: number
  buy_amount: number
  slippage: number
  min_liquidity: number
  min_safety_score: number
  require_mint_renounced: boolean
  require_freeze_renounced: boolean
  max_buy_tax: number
  max_sell_tax: number
  is_active?: boolean
}

interface SniperStatus {
  is_running: boolean
  pools_detected?: number
  tokens_bought?: number
  tokens_skipped?: number
  success_rate?: number
}

export function Sniper() {
  const { selectedWallet } = useWalletStore()

  // Configuration
  const [config, setConfig] = useState<SniperConfig>({
    wallet_id: 0,
    buy_amount: 0.1,
    slippage: 5.0,
    min_liquidity: 5.0,
    min_safety_score: 70,
    require_mint_renounced: true,
    require_freeze_renounced: true,
    max_buy_tax: 10.0,
    max_sell_tax: 10.0
  })

  const [password, setPassword] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [isStopping, setIsStopping] = useState(false)
  const [status, setStatus] = useState<SniperStatus>({ is_running: false })

  // Load config when wallet is selected
  useEffect(() => {
    if (selectedWallet) {
      loadConfig()
    }
  }, [selectedWallet])

  // Poll status
  useEffect(() => {
    const interval = setInterval(() => {
      loadStatus()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const loadConfig = async () => {
    if (!selectedWallet) return

    try {
      const response = await axios.get(`http://localhost:8000/sniper/config/${selectedWallet.id}`)
      setConfig(response.data)
    } catch (error: any) {
      if (error.response?.status === 404) {
        // No config yet, use defaults
        setConfig({
          ...config,
          wallet_id: selectedWallet.id
        })
      }
    }
  }

  const loadStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/sniper/status')
      setStatus(response.data)
    } catch (error) {
      // Ignore errors
    }
  }

  const saveConfig = async () => {
    if (!selectedWallet) {
      alert('Please select a wallet first')
      return
    }

    setIsSaving(true)
    try {
      await axios.post('http://localhost:8000/sniper/config', {
        ...config,
        wallet_id: selectedWallet.id
      })
      alert('Configuration saved successfully!')
      await loadConfig()
    } catch (error: any) {
      alert('Failed to save config: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsSaving(false)
    }
  }

  const startSniper = async () => {
    if (!selectedWallet) {
      alert('Please select a wallet first')
      return
    }

    if (!password) {
      alert('Please enter your wallet password')
      return
    }

    setIsStarting(true)
    try {
      await axios.post('http://localhost:8000/sniper/start', {
        wallet_id: selectedWallet.id,
        password: password,
        platforms: ['raydium', 'pumpfun']
      })
      setPassword('')
      alert('Sniper bot started successfully!')
      await loadStatus()
    } catch (error: any) {
      alert('Failed to start sniper: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsStarting(false)
    }
  }

  const stopSniper = async () => {
    setIsStopping(true)
    try {
      const response = await axios.post('http://localhost:8000/sniper/stop')
      alert('Sniper bot stopped successfully!')
      console.log('Stats:', response.data.stats)
      await loadStatus()
    } catch (error: any) {
      alert('Failed to stop sniper: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsStopping(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Sniper Configuration</h1>
        <p className="text-muted-foreground">
          Configure and manage your automated token sniper bot
        </p>
      </div>

      {!selectedWallet && (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="py-4">
            <p className="text-yellow-500">
              ⚠️ Please select a wallet from the Wallets page to configure the sniper
            </p>
          </CardContent>
        </Card>
      )}

      {/* Status Card */}
      <Card className={status.is_running ? 'border-green-500/50' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Sniper Status
          </CardTitle>
          <CardDescription>Current bot status and statistics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status:</span>
              <div className={`flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
                status.is_running
                  ? 'bg-green-500/20 text-green-500'
                  : 'bg-gray-500/20 text-gray-500'
              }`}>
                {status.is_running ? (
                  <>
                    <div className="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
                    Running
                  </>
                ) : (
                  <>
                    <div className="h-2 w-2 rounded-full bg-gray-500"></div>
                    Stopped
                  </>
                )}
              </div>
            </div>

            {status.is_running && (
              <div className="grid grid-cols-2 gap-4 rounded-lg bg-secondary/30 p-4">
                <div>
                  <p className="text-sm text-muted-foreground">Pools Detected</p>
                  <p className="text-2xl font-bold">{status.pools_detected || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Tokens Bought</p>
                  <p className="text-2xl font-bold text-green-500">{status.tokens_bought || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Tokens Skipped</p>
                  <p className="text-2xl font-bold text-red-500">{status.tokens_skipped || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold">{status.success_rate?.toFixed(1) || 0}%</p>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              {!status.is_running ? (
                <>
                  <Input
                    type="password"
                    placeholder="Wallet password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={!selectedWallet}
                    className="flex-1"
                  />
                  <Button
                    onClick={startSniper}
                    disabled={isStarting || !selectedWallet || !password}
                    className="bg-green-500 hover:bg-green-600"
                  >
                    <Play className="mr-2 h-4 w-4" />
                    {isStarting ? 'Starting...' : 'Start Sniper'}
                  </Button>
                </>
              ) : (
                <Button
                  onClick={stopSniper}
                  disabled={isStopping}
                  className="w-full bg-red-500 hover:bg-red-600"
                >
                  <Square className="mr-2 h-4 w-4" />
                  {isStopping ? 'Stopping...' : 'Stop Sniper'}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configuration Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            Trading Configuration
          </CardTitle>
          <CardDescription>Configure buy amount and trading parameters</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium">Buy Amount (SOL)</label>
              <Input
                type="number"
                step="0.01"
                value={config.buy_amount}
                onChange={(e) => setConfig({ ...config, buy_amount: parseFloat(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Amount of SOL to spend per token
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Slippage (%)</label>
              <Input
                type="number"
                step="0.1"
                value={config.slippage}
                onChange={(e) => setConfig({ ...config, slippage: parseFloat(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Maximum allowed slippage
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Min Liquidity (SOL)</label>
              <Input
                type="number"
                step="0.1"
                value={config.min_liquidity}
                onChange={(e) => setConfig({ ...config, min_liquidity: parseFloat(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Minimum pool liquidity required
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Min Safety Score</label>
              <Input
                type="number"
                min="0"
                max="100"
                value={config.min_safety_score}
                onChange={(e) => setConfig({ ...config, min_safety_score: parseInt(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Minimum safety score (0-100)
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Max Buy Tax (%)</label>
              <Input
                type="number"
                step="0.1"
                value={config.max_buy_tax}
                onChange={(e) => setConfig({ ...config, max_buy_tax: parseFloat(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Maximum buy tax allowed
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Max Sell Tax (%)</label>
              <Input
                type="number"
                step="0.1"
                value={config.max_sell_tax}
                onChange={(e) => setConfig({ ...config, max_sell_tax: parseFloat(e.target.value) || 0 })}
                disabled={status.is_running}
                className="mt-1"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Maximum sell tax allowed
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Safety Filters Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Safety Filters
          </CardTitle>
          <CardDescription>Token safety requirements for auto-buying</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={config.require_mint_renounced}
                onChange={(e) => setConfig({ ...config, require_mint_renounced: e.target.checked })}
                disabled={status.is_running}
                className="h-4 w-4 rounded border-gray-300"
              />
              <div>
                <div className="text-sm font-medium">Require Mint Authority Renounced</div>
                <div className="text-xs text-muted-foreground">
                  Only buy tokens where mint authority is renounced
                </div>
              </div>
            </label>

            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={config.require_freeze_renounced}
                onChange={(e) => setConfig({ ...config, require_freeze_renounced: e.target.checked })}
                disabled={status.is_running}
                className="h-4 w-4 rounded border-gray-300"
              />
              <div>
                <div className="text-sm font-medium">Require Freeze Authority Renounced</div>
                <div className="text-xs text-muted-foreground">
                  Only buy tokens where freeze authority is renounced
                </div>
              </div>
            </label>
          </div>

          <div className="rounded-lg bg-blue-500/10 p-4 text-sm text-blue-500">
            ℹ️ Safety filters help protect against rug pulls and malicious tokens. Higher requirements mean safer but fewer trading opportunities.
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={saveConfig}
          disabled={isSaving || !selectedWallet || status.is_running}
          size="lg"
        >
          {isSaving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </div>
    </div>
  )
}

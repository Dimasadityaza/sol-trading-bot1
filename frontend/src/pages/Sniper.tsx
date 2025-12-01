import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useWalletStore } from '@/store/walletStore'
import { sniperApi, groupsApi } from '@/services/api'
import { Target, Play, Square, Activity, TrendingUp, AlertCircle, CheckCircle, Users, Wallet } from 'lucide-react'
import type { SniperConfig, SniperStatus } from '@/types'
import { storage } from '@/utils/storage'

export function Sniper() {
  const { selectedWallet } = useWalletStore()

  // Mode selection
  const [mode, setMode] = useState<'single' | 'group'>('single')
  const [groups, setGroups] = useState<any[]>([])
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null)
  const [tokenAddress, setTokenAddress] = useState('')
  const [network, setNetwork] = useState<string>('devnet')

  // Configuration state
  const [config, setConfig] = useState<SniperConfig>({
    wallet_id: 0,
    buy_amount: 0.1,
    slippage: 5.0,
    min_liquidity: 5.0,
    min_safety_score: 70,
    require_mint_renounced: true,
    require_freeze_renounced: true,
    max_buy_tax: 10.0,
    max_sell_tax: 10.0,
  })

  // Status state
  const [status, setStatus] = useState<SniperStatus>({
    is_running: false,
    pools_detected: 0,
    tokens_bought: 0,
    tokens_skipped: 0,
    success_rate: 0,
  })

  // UI state
  const [password, setPassword] = useState('')
  const [rememberPassword, setRememberPassword] = useState(false)
  const [platforms, setPlatforms] = useState<string[]>(['raydium', 'pumpfun'])
  const [isSaving, setIsSaving] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [isStopping, setIsStopping] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Load groups and saved password on mount
  useEffect(() => {
    loadGroups()
    fetchNetworkInfo()

    // Load saved password if exists
    const savedPassword = storage.getPassword()
    if (savedPassword) {
      setPassword(savedPassword)
      setRememberPassword(true)
    }
  }, [])

  // Load config when wallet selected
  useEffect(() => {
    if (selectedWallet && mode === 'single') {
      loadConfig()
    }
  }, [selectedWallet, mode])

  const loadGroups = async () => {
    try {
      const response = await groupsApi.listGroups()
      setGroups(response.groups || [])
    } catch (error) {
      console.error('Failed to load groups:', error)
    }
  }

  const fetchNetworkInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      const data = await response.json()
      setNetwork(data.network || 'devnet')
    } catch (error) {
      console.error('Failed to fetch network info:', error)
    }
  }

  // Poll status every 3 seconds when running
  useEffect(() => {
    let interval: number | null = null

    if (status.is_running) {
      interval = window.setInterval(() => {
        fetchStatus()
      }, 3000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [status.is_running])

  const loadConfig = async () => {
    if (!selectedWallet) return

    try {
      const data = await sniperApi.getConfig(selectedWallet.id)
      setConfig(data)
    } catch (error: any) {
      // Config not found, create default config
      const defaultConfig = {
        wallet_id: selectedWallet.id,
        buy_amount: 0.1,
        slippage: 5.0,
        min_liquidity: 5.0,
        min_safety_score: 70,
        require_mint_renounced: true,
        require_freeze_renounced: true,
        max_buy_tax: 10.0,
        max_sell_tax: 10.0,
      }

      setConfig(defaultConfig)

      // Auto-save default config to backend
      try {
        await sniperApi.saveConfig(defaultConfig)
        showMessage('success', 'Default sniper configuration created')
      } catch (saveError) {
        console.error('Failed to auto-save config:', saveError)
      }
    }
  }

  const fetchStatus = async () => {
    try {
      const data = await sniperApi.getStatus()
      setStatus(data)
    } catch (error) {
      console.error('Failed to fetch status:', error)
    }
  }

  const saveConfig = async () => {
    if (!selectedWallet) {
      showMessage('error', 'Please select a wallet first')
      return
    }

    setIsSaving(true)
    try {
      await sniperApi.saveConfig({
        wallet_id: selectedWallet.id,
        buy_amount: config.buy_amount,
        slippage: config.slippage,
        min_liquidity: config.min_liquidity,
        min_safety_score: config.min_safety_score,
        require_mint_renounced: config.require_mint_renounced,
        require_freeze_renounced: config.require_freeze_renounced,
        max_buy_tax: config.max_buy_tax,
        max_sell_tax: config.max_sell_tax,
      })
      showMessage('success', 'Configuration saved successfully')
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to save configuration')
    } finally {
      setIsSaving(false)
    }
  }

  const startSniper = async () => {
    // Validation
    if (mode === 'single' && !selectedWallet) {
      showMessage('error', 'Please select a wallet first')
      return
    }

    if (mode === 'group' && !selectedGroupId) {
      showMessage('error', 'Please select a group first')
      return
    }

    if (!password) {
      showMessage('error', 'Please enter your wallet password')
      return
    }

    setIsStarting(true)
    try {
      if (mode === 'group') {
        // Group sniper mode
        await sniperApi.setupGroupSniper({
          group_id: selectedGroupId!,
          buy_amount: config.buy_amount,
          slippage: config.slippage,
          min_liquidity: config.min_liquidity,
          min_safety_score: config.min_safety_score,
          require_mint_renounced: config.require_mint_renounced,
          require_freeze_renounced: config.require_freeze_renounced,
          max_buy_tax: config.max_buy_tax,
          max_sell_tax: config.max_sell_tax,
          password: password,
          platforms: platforms,
        })

        // If token address is provided, start manual snipe
        if (tokenAddress.trim()) {
          await sniperApi.startManualSnipe({
            group_id: selectedGroupId!,
            token_address: tokenAddress.trim(),
            password: password,
          })
          showMessage('success', `Group sniper started for token: ${tokenAddress.substring(0, 8)}...`)
        } else {
          showMessage('success', 'Group sniper configured successfully!')
        }
      } else {
        // Single wallet mode
        if (tokenAddress.trim()) {
          // Manual snipe with specific token
          await sniperApi.startManualSnipe({
            wallet_id: selectedWallet!.id,
            token_address: tokenAddress.trim(),
            password: password,
          })
          showMessage('success', `Manual snipe started for token: ${tokenAddress.substring(0, 8)}...`)
        } else {
          // Auto-detection mode
          await sniperApi.start({
            wallet_id: selectedWallet!.id,
            password: password,
            platforms: platforms,
          })
          showMessage('success', 'Sniper bot started successfully!')
        }
      }

      // Handle remember password
      if (rememberPassword) {
        storage.savePassword(password)
      } else {
        storage.clearPassword()
      }

      setPassword('')
      await fetchStatus()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to start sniper')
    } finally {
      setIsStarting(false)
    }
  }

  const handleForgetPassword = () => {
    storage.clearPassword()
    setPassword('')
    setRememberPassword(false)
    showMessage('success', 'Password cleared from browser storage')
  }

  const stopSniper = async () => {
    setIsStopping(true)
    try {
      const result = await sniperApi.stop()
      showMessage('success', 'Sniper bot stopped')
      setStatus(result.stats || { is_running: false })
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to stop sniper')
    } finally {
      setIsStopping(false)
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const togglePlatform = (platform: string) => {
    if (platforms.includes(platform)) {
      setPlatforms(platforms.filter(p => p !== platform))
    } else {
      setPlatforms([...platforms, platform])
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sniper Configuration</h1>
          <p className="text-muted-foreground">
            Auto-detect and snipe new liquidity pools with safety checks
          </p>
        </div>
        <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
          network === 'mainnet'
            ? 'bg-green-500/20 text-green-400 border border-green-500/50'
            : network === 'testnet'
            ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
            : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
        }`}>
          {network === 'mainnet' ? '🔴 MAINNET' : network === 'testnet' ? '🔵 TESTNET' : '🟡 DEVNET'}
        </div>
      </div>

      {/* Mode Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Sniper Mode</CardTitle>
          <CardDescription>Choose between single wallet or group wallet sniping</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <button
              onClick={() => setMode('single')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                mode === 'single'
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <Wallet className="h-6 w-6 mx-auto mb-2" />
              <div className="font-medium">Single Wallet</div>
              <div className="text-xs text-muted-foreground mt-1">
                Snipe using one wallet
              </div>
            </button>
            <button
              onClick={() => setMode('group')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                mode === 'group'
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <Users className="h-6 w-6 mx-auto mb-2" />
              <div className="font-medium">Group Wallet</div>
              <div className="text-xs text-muted-foreground mt-1">
                Snipe using multiple wallets
              </div>
            </button>
          </div>

          {mode === 'single' && !selectedWallet && (
            <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/50">
              <p className="text-sm text-yellow-500">
                ⚠️ Please select a wallet from the Wallets page
              </p>
            </div>
          )}

          {mode === 'group' && (
            <div className="mt-4">
              <label className="text-sm font-medium">Select Group</label>
              <select
                value={selectedGroupId || ''}
                onChange={(e) => setSelectedGroupId(Number(e.target.value))}
                className="mt-1 w-full px-3 py-2 rounded-md border border-border bg-background"
              >
                <option value="">Select a group...</option>
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name} ({group.wallet_count} wallets)
                  </option>
                ))}
              </select>
              {groups.length === 0 && (
                <p className="text-xs text-muted-foreground mt-1">
                  No groups found. Create a group in the Groups page first.
                </p>
              )}
            </div>
          )}

          <div className="mt-4">
            <label className="text-sm font-medium">Token Address (Optional)</label>
            <Input
              placeholder="Enter token address to snipe manually (leave empty for auto-detection)"
              value={tokenAddress}
              onChange={(e) => setTokenAddress(e.target.value)}
              className="mt-1 font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {tokenAddress.trim()
                ? '🎯 Manual snipe mode - will buy this specific token'
                : '🔍 Auto-detection mode - will monitor DEX platforms for new pools'
              }
            </p>
          </div>
        </CardContent>
      </Card>

      {mode === 'single' && !selectedWallet && (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="py-4">
            <p className="text-yellow-500">
              ⚠️ Please select a wallet from the Wallets page to configure sniper
            </p>
          </CardContent>
        </Card>
      )}

      {message && (
        <Card className={`border-${message.type === 'success' ? 'green' : 'red'}-500/50 bg-${message.type === 'success' ? 'green' : 'red'}-500/10`}>
          <CardContent className="py-4 flex items-center gap-2">
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
            <p className={`text-${message.type === 'success' ? 'green' : 'red'}-500`}>
              {message.text}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Status Card */}
      <Card className={status.is_running ? 'border-green-500/50' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className={`h-5 w-5 ${status.is_running ? 'text-green-500' : 'text-muted-foreground'}`} />
            Sniper Status
            {status.is_running && (
              <span className="ml-auto text-sm font-normal text-green-500 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                Running
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg bg-secondary/30 p-4">
              <div className="text-2xl font-bold">{status.pools_detected || 0}</div>
              <div className="text-xs text-muted-foreground">Pools Detected</div>
            </div>
            <div className="rounded-lg bg-green-500/10 p-4">
              <div className="text-2xl font-bold text-green-500">{status.tokens_bought || 0}</div>
              <div className="text-xs text-muted-foreground">Tokens Bought</div>
            </div>
            <div className="rounded-lg bg-red-500/10 p-4">
              <div className="text-2xl font-bold text-red-500">{status.tokens_skipped || 0}</div>
              <div className="text-xs text-muted-foreground">Tokens Skipped</div>
            </div>
            <div className="rounded-lg bg-blue-500/10 p-4">
              <div className="text-2xl font-bold text-blue-500">{status.success_rate?.toFixed(1) || 0}%</div>
              <div className="text-xs text-muted-foreground">Success Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Configuration Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Sniper Configuration
            </CardTitle>
            <CardDescription>Configure auto-sniper parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Buy Amount (SOL)</label>
              <Input
                type="number"
                step="0.01"
                value={config.buy_amount}
                onChange={(e) => setConfig({ ...config, buy_amount: parseFloat(e.target.value) })}
                className="mt-1"
                disabled={status.is_running}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Amount to spend per snipe
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Slippage (%)</label>
              <Input
                type="number"
                step="0.1"
                value={config.slippage}
                onChange={(e) => setConfig({ ...config, slippage: parseFloat(e.target.value) })}
                className="mt-1"
                disabled={status.is_running}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Min Liquidity (SOL)</label>
              <Input
                type="number"
                step="0.1"
                value={config.min_liquidity}
                onChange={(e) => setConfig({ ...config, min_liquidity: parseFloat(e.target.value) })}
                className="mt-1"
                disabled={status.is_running}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Only snipe pools with liquidity above this amount
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Min Safety Score</label>
              <Input
                type="number"
                min="0"
                max="100"
                value={config.min_safety_score}
                onChange={(e) => setConfig({ ...config, min_safety_score: parseInt(e.target.value) })}
                className="mt-1"
                disabled={status.is_running}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Minimum safety score (0-100)
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Max Buy Tax (%)</label>
              <Input
                type="number"
                step="0.1"
                value={config.max_buy_tax}
                onChange={(e) => setConfig({ ...config, max_buy_tax: parseFloat(e.target.value) })}
                className="mt-1"
                disabled={status.is_running}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Safety Requirements</label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.require_mint_renounced}
                    onChange={(e) => setConfig({ ...config, require_mint_renounced: e.target.checked })}
                    className="h-4 w-4"
                    disabled={status.is_running}
                  />
                  <span className="text-sm">Require Mint Authority Renounced</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.require_freeze_renounced}
                    onChange={(e) => setConfig({ ...config, require_freeze_renounced: e.target.checked })}
                    className="h-4 w-4"
                    disabled={status.is_running}
                  />
                  <span className="text-sm">Require Freeze Authority Renounced</span>
                </label>
              </div>
            </div>

            <Button
              onClick={saveConfig}
              disabled={isSaving || !selectedWallet || status.is_running}
              className="w-full"
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </CardContent>
        </Card>

        {/* Control Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Sniper Controls
            </CardTitle>
            <CardDescription>Start and stop the sniper bot</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">DEX Platforms</label>
              <div className="mt-2 space-y-2">
                {['raydium', 'pumpfun', 'orca'].map((platform) => (
                  <label key={platform} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={platforms.includes(platform)}
                      onChange={() => togglePlatform(platform)}
                      className="h-4 w-4"
                      disabled={status.is_running}
                    />
                    <span className="text-sm capitalize">{platform}</span>
                  </label>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Select which DEX platforms to monitor
              </p>
            </div>

            {!status.is_running ? (
              <>
                <div>
                  <label className="text-sm font-medium">Wallet Password</label>
                  <Input
                    type="password"
                    placeholder="Enter your wallet password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="mt-1"
                  />
                  <div className="flex items-center justify-between mt-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={rememberPassword}
                        onChange={(e) => setRememberPassword(e.target.checked)}
                        className="h-4 w-4"
                      />
                      <span className="text-xs text-muted-foreground">
                        Remember password (browser only)
                      </span>
                    </label>
                    {storage.hasPassword() && (
                      <button
                        onClick={handleForgetPassword}
                        className="text-xs text-red-400 hover:text-red-300 underline"
                      >
                        Forget Password
                      </button>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Required to decrypt private key for trading
                  </p>
                </div>

                <Button
                  onClick={startSniper}
                  disabled={isStarting || (mode === 'single' && !selectedWallet) || (mode === 'group' && !selectedGroupId) || platforms.length === 0}
                  className="w-full bg-green-500 hover:bg-green-600"
                >
                  <Play className="h-4 w-4 mr-2" />
                  {isStarting ? 'Starting...' : 'Start Sniper Bot'}
                </Button>
              </>
            ) : (
              <Button
                onClick={stopSniper}
                disabled={isStopping}
                className="w-full bg-red-500 hover:bg-red-600"
              >
                <Square className="h-4 w-4 mr-2" />
                {isStopping ? 'Stopping...' : 'Stop Sniper Bot'}
              </Button>
            )}

            <div className="rounded-lg bg-blue-500/10 border border-blue-500/20 p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-blue-500 mt-0.5" />
                <div className="space-y-1 text-sm">
                  <p className="font-medium text-blue-500">How it works:</p>
                  <ul className="text-muted-foreground space-y-1 ml-4 list-disc">
                    <li>Monitors selected DEX platforms in real-time</li>
                    <li>Detects new liquidity pools automatically</li>
                    <li>Analyzes token safety (mint/freeze authority)</li>
                    <li>Auto-buys tokens that pass all safety checks</li>
                    <li>Tracks success rate and statistics</li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

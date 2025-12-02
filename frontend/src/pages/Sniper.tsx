import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useWalletStore } from '@/store/walletStore'
import { sniperApi } from '@/services/api'
import { Target, Play, Square, Activity, TrendingUp, AlertCircle, CheckCircle, Zap } from 'lucide-react'
import type { SniperConfig, SniperStatus } from '@/types'
import axios from 'axios'

export function Sniper() {
  const { selectedWallet } = useWalletStore()

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
  const [platforms, setPlatforms] = useState<string[]>(['raydium', 'pumpfun'])
  const [isSaving, setIsSaving] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [isStopping, setIsStopping] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Manual snipe state
  const [manualTokenAddress, setManualTokenAddress] = useState('')
  const [manualPassword, setManualPassword] = useState('')
  const [isManualSniping, setIsManualSniping] = useState(false)

  // Bulk snipe state
  const [groups, setGroups] = useState<any[]>([])
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null)
  const [bulkTokenAddress, setBulkTokenAddress] = useState('')
  const [bulkBuyAmount, setBulkBuyAmount] = useState(0.1)
  const [bulkSlippage, setBulkSlippage] = useState(5.0)
  const [bulkPassword, setBulkPassword] = useState('')
  const [isBulkSniping, setIsBulkSniping] = useState(false)
  const [bulkResults, setBulkResults] = useState<any>(null)

  // Load config when wallet selected
  useEffect(() => {
    if (selectedWallet) {
      loadConfig()
    }
  }, [selectedWallet])

  // Load groups on mount
  useEffect(() => {
    loadGroups()
  }, [])

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

  const loadGroups = async () => {
    try {
      const response = await axios.get('http://localhost:8000/group/list')
      setGroups(response.data || [])
    } catch (error) {
      console.error('Failed to load groups:', error)
    }
  }

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
    if (!selectedWallet) {
      showMessage('error', 'Please select a wallet first')
      return
    }

    if (!password) {
      showMessage('error', 'Please enter your wallet password')
      return
    }

    setIsStarting(true)
    try {
      await sniperApi.start({
        wallet_id: selectedWallet.id,
        password: password,
        platforms: platforms,
      })

      showMessage('success', 'Sniper bot started successfully!')
      setPassword('')
      await fetchStatus()
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to start sniper')
    } finally {
      setIsStarting(false)
    }
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

  const executeManualSnipe = async () => {
    if (!selectedWallet) {
      showMessage('error', 'Please select a wallet first')
      return
    }

    if (!manualTokenAddress) {
      showMessage('error', 'Please enter token address to snipe')
      return
    }

    if (!manualPassword) {
      showMessage('error', 'Please enter your wallet password')
      return
    }

    setIsManualSniping(true)
    try {
      const response = await axios.post('http://localhost:8000/trade/buy', {
        wallet_id: selectedWallet.id,
        token_address: manualTokenAddress,
        sol_amount: config.buy_amount,
        slippage: config.slippage,
        password: manualPassword
      })

      showMessage('success', `Manual snipe successful! TX: ${response.data.signature?.slice(0, 10)}...`)
      setManualTokenAddress('')
      setManualPassword('')
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Manual snipe failed')
    } finally {
      setIsManualSniping(false)
    }
  }

  const executeBulkSnipe = async () => {
    if (!selectedGroupId) {
      showMessage('error', 'Please select a group first')
      return
    }

    if (!bulkTokenAddress) {
      showMessage('error', 'Please enter token address to snipe')
      return
    }

    if (!bulkPassword) {
      showMessage('error', 'Please enter password')
      return
    }

    setIsBulkSniping(true)
    setBulkResults(null)

    try {
      const response = await axios.post('http://localhost:8000/sniper/group/manual-snipe', {
        group_id: selectedGroupId,
        token_address: bulkTokenAddress,
        buy_amount: bulkBuyAmount,
        slippage: bulkSlippage,
        password: bulkPassword
      })

      setBulkResults(response.data)
      showMessage('success', response.data.message)
      setBulkPassword('')
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Bulk snipe failed')
    } finally {
      setIsBulkSniping(false)
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Sniper Configuration</h1>
        <p className="text-muted-foreground">
          Auto-detect and snipe new liquidity pools with safety checks
        </p>
      </div>

      {!selectedWallet && (
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

      {/* Manual Snipe Card */}
      <Card className="border-yellow-500/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Manual Snipe (Single Wallet)
          </CardTitle>
          <CardDescription>Snipe a specific token address with selected wallet</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Token Address to Snipe</label>
            <Input
              placeholder="Enter token address (e.g., EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)"
              value={manualTokenAddress}
              onChange={(e) => setManualTokenAddress(e.target.value)}
              className="mt-1 font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Will buy {config.buy_amount} SOL worth with {config.slippage}% slippage
            </p>
          </div>

          <div>
            <label className="text-sm font-medium">Wallet Password</label>
            <Input
              type="password"
              placeholder="Enter your wallet password"
              value={manualPassword}
              onChange={(e) => setManualPassword(e.target.value)}
              className="mt-1"
            />
          </div>

          <Button
            onClick={executeManualSnipe}
            disabled={isManualSniping || !selectedWallet || !manualTokenAddress || !manualPassword}
            className="w-full bg-yellow-500 hover:bg-yellow-600"
          >
            <Zap className="h-4 w-4 mr-2" />
            {isManualSniping ? 'Sniping...' : 'Snipe Now!'}
          </Button>

          <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-3 text-sm">
            <p className="text-yellow-500">
              ⚡ Quick snipe: Uses current sniper config (buy amount & slippage). Make sure to configure them first!
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Bulk Snipe Card */}
      <Card className="border-purple-500/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-purple-500" />
            Bulk Snipe (Multiple Wallets)
          </CardTitle>
          <CardDescription>Snipe a token with ALL wallets in a group simultaneously</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Select Group</label>
            <select
              value={selectedGroupId || ''}
              onChange={(e) => setSelectedGroupId(parseInt(e.target.value))}
              className="mt-1 w-full rounded-md border bg-background px-3 py-2"
            >
              <option value="">Select a wallet group...</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name} ({group.wallet_count} wallets)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">Token Address to Snipe</label>
            <Input
              placeholder="Enter token address"
              value={bulkTokenAddress}
              onChange={(e) => setBulkTokenAddress(e.target.value)}
              className="mt-1 font-mono text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-sm font-medium">Buy Amount (SOL)</label>
              <Input
                type="number"
                step="0.01"
                value={bulkBuyAmount}
                onChange={(e) => setBulkBuyAmount(parseFloat(e.target.value))}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Slippage (%)</label>
              <Input
                type="number"
                step="0.1"
                value={bulkSlippage}
                onChange={(e) => setBulkSlippage(parseFloat(e.target.value))}
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Password</label>
            <Input
              type="password"
              placeholder="Enter wallet password"
              value={bulkPassword}
              onChange={(e) => setBulkPassword(e.target.value)}
              className="mt-1"
            />
          </div>

          <Button
            onClick={executeBulkSnipe}
            disabled={isBulkSniping || !selectedGroupId || !bulkTokenAddress || !bulkPassword}
            className="w-full bg-purple-500 hover:bg-purple-600"
          >
            <Target className="h-4 w-4 mr-2" />
            {isBulkSniping ? 'Bulk Sniping...' : 'Bulk Snipe Now!'}
          </Button>

          {bulkResults && (
            <div className="rounded-lg bg-purple-500/10 border border-purple-500/20 p-3 space-y-2">
              <p className="font-semibold text-purple-500">
                ✅ {bulkResults.success_count} Success | ❌ {bulkResults.fail_count} Failed
              </p>
              <div className="max-h-40 overflow-y-auto space-y-1 text-sm">
                {bulkResults.results?.map((result: any, idx: number) => (
                  <div key={idx} className={result.success ? 'text-green-500' : 'text-red-500'}>
                    {result.success ? '✓' : '✗'} {result.wallet_label}
                    {result.error && `: ${result.error}`}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="rounded-lg bg-purple-500/10 border border-purple-500/20 p-3 text-sm">
            <p className="text-purple-500">
              🚀 Bulk snipe: All wallets in the group will snipe the token at the same time!
            </p>
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
                  <p className="text-xs text-muted-foreground mt-1">
                    Required to decrypt private key for trading
                  </p>
                </div>

                <Button
                  onClick={startSniper}
                  disabled={isStarting || !selectedWallet || platforms.length === 0}
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

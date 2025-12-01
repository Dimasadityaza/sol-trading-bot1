import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useWalletStore } from '@/store/walletStore'
import { formatNumber } from '@/lib/utils'
import { TrendingUp, TrendingDown, Search, Shield } from 'lucide-react'
import axios from 'axios'

export function Trading() {
  const { selectedWallet } = useWalletStore()
  
  // Token search
  const [tokenAddress, setTokenAddress] = useState('')
  const [tokenInfo, setTokenInfo] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  
  // Buy form
  const [buyAmount, setBuyAmount] = useState('')
  const [buySlippage, setBuySlippage] = useState('1')
  const [buyPassword, setBuyPassword] = useState('')
  const [isBuying, setIsBuying] = useState(false)
  const [buyResult, setBuyResult] = useState<any>(null)
  
  // Sell form
  const [sellPercentage, setSellPercentage] = useState('100')
  const [sellSlippage, setSellSlippage] = useState('1')
  const [sellPassword, setSellPassword] = useState('')
  const [isSelling, setIsSelling] = useState(false)
  const [sellResult, setSellResult] = useState<any>(null)

  const analyzeToken = async () => {
    if (!tokenAddress) return
    
    setIsAnalyzing(true)
    setTokenInfo(null)
    setBuyResult(null)
    setSellResult(null)
    
    try {
      const response = await axios.post('http://localhost:8000/trade/analyze', {
        token_address: tokenAddress
      })
      setTokenInfo(response.data)
    } catch (error: any) {
      alert('Failed to analyze token: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsAnalyzing(false)
    }
  }

  const executeBuy = async () => {
    if (!selectedWallet) {
      alert('Please select a wallet first')
      return
    }
    
    if (!tokenAddress || !buyAmount || !buyPassword) {
      alert('Please fill all fields')
      return
    }
    
    setIsBuying(true)
    setBuyResult(null)
    
    try {
      const response = await axios.post('http://localhost:8000/trade/buy', {
        wallet_id: selectedWallet.id,
        token_address: tokenAddress,
        sol_amount: parseFloat(buyAmount),
        slippage: parseFloat(buySlippage),
        password: buyPassword
      })
      
      setBuyResult(response.data)
      setBuyPassword('')
      alert('Buy order executed successfully!')
    } catch (error: any) {
      alert('Buy failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsBuying(false)
    }
  }

  const executeSell = async () => {
    if (!selectedWallet) {
      alert('Please select a wallet first')
      return
    }
    
    if (!tokenAddress || !sellPassword) {
      alert('Please fill all fields')
      return
    }
    
    setIsSelling(true)
    setSellResult(null)
    
    try {
      const response = await axios.post('http://localhost:8000/trade/sell', {
        wallet_id: selectedWallet.id,
        token_address: tokenAddress,
        percentage: parseFloat(sellPercentage),
        slippage: parseFloat(sellSlippage),
        password: sellPassword
      })
      
      setSellResult(response.data)
      setSellPassword('')
      alert('Sell order executed successfully!')
    } catch (error: any) {
      alert('Sell failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsSelling(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Manual Trading</h1>
        <p className="text-muted-foreground">
          Buy and sell tokens with Jupiter integration
        </p>
      </div>

      {!selectedWallet && (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="py-4">
            <p className="text-yellow-500">
              ⚠️ Please select a wallet from the Wallets page to start trading
            </p>
          </CardContent>
        </Card>
      )}

      {/* Token Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Token Search
          </CardTitle>
          <CardDescription>Enter token address to analyze and trade</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Token address (e.g., EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)"
              value={tokenAddress}
              onChange={(e) => setTokenAddress(e.target.value)}
              className="font-mono text-sm"
            />
            <Button 
              onClick={analyzeToken} 
              disabled={isAnalyzing || !tokenAddress}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>

          {tokenInfo && (
            <div className="rounded-lg border bg-secondary/30 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Safety Analysis</h3>
                <div className={`flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
                  tokenInfo.is_safe 
                    ? 'bg-green-500/20 text-green-500'
                    : 'bg-red-500/20 text-red-500'
                }`}>
                  <Shield className="h-4 w-4" />
                  Score: {tokenInfo.safety_score}/100
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center gap-2">
                  <div className={`h-2 w-2 rounded-full ${tokenInfo.mint_renounced ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span>Mint Authority: {tokenInfo.mint_renounced ? 'Renounced' : 'Not Renounced'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`h-2 w-2 rounded-full ${tokenInfo.freeze_renounced ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span>Freeze Authority: {tokenInfo.freeze_renounced ? 'Renounced' : 'Not Renounced'}</span>
                </div>
              </div>

              {!tokenInfo.is_safe && (
                <div className="text-sm text-yellow-500">
                  ⚠️ Warning: This token has safety concerns. Trade with caution.
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Buy Panel */}
        <Card className="border-green-500/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-500">
              <TrendingUp className="h-5 w-5" />
              Buy Token
            </CardTitle>
            <CardDescription>Purchase tokens with SOL</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Amount (SOL)</label>
              <div className="mt-1 flex gap-2">
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.1"
                  value={buyAmount}
                  onChange={(e) => setBuyAmount(e.target.value)}
                />
              </div>
              <div className="mt-2 flex gap-2">
                {[0.1, 0.5, 1, 5].map((amount) => (
                  <Button
                    key={amount}
                    size="sm"
                    variant="outline"
                    onClick={() => setBuyAmount(amount.toString())}
                  >
                    {amount} SOL
                  </Button>
                ))}
              </div>
              {selectedWallet && (
                <p className="mt-1 text-xs text-muted-foreground">
                  Available: {formatNumber(selectedWallet.balance, 4)} SOL
                </p>
              )}
            </div>

            <div>
              <label className="text-sm font-medium">Slippage (%)</label>
              <Input
                type="number"
                step="0.1"
                value={buySlippage}
                onChange={(e) => setBuySlippage(e.target.value)}
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Wallet Password</label>
              <Input
                type="password"
                placeholder="Enter your wallet password"
                value={buyPassword}
                onChange={(e) => setBuyPassword(e.target.value)}
                className="mt-1"
              />
            </div>

            <Button
              className="w-full bg-green-500 hover:bg-green-600"
              onClick={executeBuy}
              disabled={isBuying || !selectedWallet || !tokenAddress}
            >
              {isBuying ? 'Executing Buy...' : 'Buy Token'}
            </Button>

            {buyResult && (
              <div className="rounded-lg bg-green-500/10 p-3 text-sm">
                <p className="font-semibold text-green-500">Buy Successful!</p>
                <a
                  href={buyResult.explorer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline"
                >
                  View on Solscan →
                </a>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sell Panel */}
        <Card className="border-red-500/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-500">
              <TrendingDown className="h-5 w-5" />
              Sell Token
            </CardTitle>
            <CardDescription>Sell tokens for SOL</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Percentage to Sell</label>
              <Input
                type="number"
                min="1"
                max="100"
                value={sellPercentage}
                onChange={(e) => setSellPercentage(e.target.value)}
                className="mt-1"
              />
              <div className="mt-2 flex gap-2">
                {[25, 50, 75, 100].map((pct) => (
                  <Button
                    key={pct}
                    size="sm"
                    variant="outline"
                    onClick={() => setSellPercentage(pct.toString())}
                  >
                    {pct}%
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Slippage (%)</label>
              <Input
                type="number"
                step="0.1"
                value={sellSlippage}
                onChange={(e) => setSellSlippage(e.target.value)}
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Wallet Password</label>
              <Input
                type="password"
                placeholder="Enter your wallet password"
                value={sellPassword}
                onChange={(e) => setSellPassword(e.target.value)}
                className="mt-1"
              />
            </div>

            <Button
              className="w-full bg-red-500 hover:bg-red-600"
              onClick={executeSell}
              disabled={isSelling || !selectedWallet || !tokenAddress}
            >
              {isSelling ? 'Executing Sell...' : 'Sell Token'}
            </Button>

            {sellResult && (
              <div className="rounded-lg bg-red-500/10 p-3 text-sm">
                <p className="font-semibold text-red-500">Sell Successful!</p>
                <a
                  href={sellResult.explorer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline"
                >
                  View on Solscan →
                </a>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

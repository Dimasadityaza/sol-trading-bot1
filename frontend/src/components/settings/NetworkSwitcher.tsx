import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import axios from 'axios'
import { Network, RefreshCw } from 'lucide-react'

const API_URL = 'http://localhost:8000'

export function NetworkSwitcher() {
  const [network, setNetwork] = useState<'devnet' | 'mainnet'>('devnet')
  const [isLoading, setIsLoading] = useState(false)
  const [isSwitching, setIsSwitching] = useState(false)

  useEffect(() => {
    loadNetwork()
  }, [])

  const loadNetwork = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(`${API_URL}/settings/network`)
      setNetwork(response.data.network)
    } catch (error) {
      console.error('Failed to load network:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const switchNetwork = async (newNetwork: 'devnet' | 'mainnet') => {
    if (newNetwork === network) return

    setIsSwitching(true)
    try {
      const response = await axios.post(`${API_URL}/settings/network`, {
        network: newNetwork,
      })
      setNetwork(response.data.network)

      // Show success message
      alert(`Switched to ${newNetwork.toUpperCase()}`)
    } catch (error) {
      console.error('Failed to switch network:', error)
      alert('Failed to switch network')
    } finally {
      setIsSwitching(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5" />
              Network Configuration
            </CardTitle>
            <CardDescription>
              Switch between Solana Devnet and Mainnet
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={loadNetwork}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-lg border bg-muted/50">
            <div>
              <p className="text-sm font-medium">Current Network</p>
              <p className="text-2xl font-bold capitalize mt-1">
                {network}
              </p>
            </div>
            <div className={`h-3 w-3 rounded-full ${
              network === 'devnet' ? 'bg-yellow-500' : 'bg-green-500'
            } animate-pulse`} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Button
              variant={network === 'devnet' ? 'default' : 'outline'}
              onClick={() => switchNetwork('devnet')}
              disabled={isSwitching || network === 'devnet'}
              className="h-20 flex flex-col items-center justify-center gap-2"
            >
              <div className="h-2 w-2 rounded-full bg-yellow-500" />
              <div>
                <div className="font-semibold">Devnet</div>
                <div className="text-xs opacity-80">Test Network</div>
              </div>
            </Button>

            <Button
              variant={network === 'mainnet' ? 'default' : 'outline'}
              onClick={() => switchNetwork('mainnet')}
              disabled={isSwitching || network === 'mainnet'}
              className="h-20 flex flex-col items-center justify-center gap-2"
            >
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div>
                <div className="font-semibold">Mainnet</div>
                <div className="text-xs opacity-80">Production Network</div>
              </div>
            </Button>
          </div>

          <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-3">
            <p className="text-sm text-yellow-600 dark:text-yellow-500">
              <strong>Warning:</strong> Switching networks will affect all wallet operations.
              Make sure you're using the correct network for your needs.
            </p>
          </div>

          {network === 'mainnet' && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
              <p className="text-sm text-red-600 dark:text-red-500">
                <strong>Caution:</strong> You are on MAINNET. All transactions use real SOL.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

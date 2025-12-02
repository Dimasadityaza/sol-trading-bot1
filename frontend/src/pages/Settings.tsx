import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Network, AlertTriangle, Save } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import api from '../services/api';

export default function Settings() {
  const [network, setNetwork] = useState('devnet');
  const [rpcEndpoint, setRpcEndpoint] = useState('');
  const [wsEndpoint, setWsEndpoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [showMainnetWarning, setShowMainnetWarning] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings/network');
      setNetwork(response.data.network || 'devnet');
      setRpcEndpoint(response.data.rpc_endpoint || '');
      setWsEndpoint(response.data.ws_endpoint || '');
    } catch (error) {
      console.error('Failed to load settings:', error);
      // Set defaults if API fails
      setNetwork('devnet');
      setRpcEndpoint('https://api.devnet.solana.com');
      setWsEndpoint('wss://api.devnet.solana.com');
    }
  };

  const handleNetworkChange = (newNetwork: string) => {
    if (newNetwork === 'mainnet') {
      setShowMainnetWarning(true);
    } else {
      applyNetworkChange(newNetwork);
    }
  };

  const applyNetworkChange = (newNetwork: string) => {
    setNetwork(newNetwork);

    if (newNetwork === 'mainnet') {
      setRpcEndpoint('https://api.mainnet-beta.solana.com');
      setWsEndpoint('wss://api.mainnet-beta.solana.com');
    } else {
      setRpcEndpoint('https://api.devnet.solana.com');
      setWsEndpoint('wss://api.devnet.solana.com');
    }

    setShowMainnetWarning(false);
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await api.post('/settings/network', {
        network,
        rpc_endpoint: rpcEndpoint,
        ws_endpoint: wsEndpoint
      });

      alert(`✅ Network settings saved!\n\nNetwork: ${network}\nRPC: ${rpcEndpoint}\n\n⚠️ Please restart the backend server for changes to take effect.`);
    } catch (error: any) {
      alert('❌ Failed to save settings: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <SettingsIcon className="w-8 h-8" />
          Settings
        </h1>
        <p className="text-gray-400 mt-1">Configure network and application settings</p>
      </div>

      {/* Network Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="w-5 h-5" />
            Network Configuration
          </CardTitle>
          <CardDescription>
            Switch between Devnet (testnet) and Mainnet (real money)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Network Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Network</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleNetworkChange('devnet')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  network === 'devnet'
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <div className="text-left">
                  <div className="font-semibold">Devnet</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Test network - Free SOL, no real value
                  </div>
                  {network === 'devnet' && (
                    <div className="text-xs text-blue-400 mt-2">✓ Currently Active</div>
                  )}
                </div>
              </button>

              <button
                onClick={() => handleNetworkChange('mainnet')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  network === 'mainnet'
                    ? 'border-green-500 bg-green-500/10'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <div className="text-left">
                  <div className="font-semibold text-green-400">Mainnet Beta</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Production network - Real SOL, real value
                  </div>
                  {network === 'mainnet' && (
                    <div className="text-xs text-green-400 mt-2">✓ Currently Active</div>
                  )}
                </div>
              </button>
            </div>
          </div>

          {/* RPC Endpoint */}
          <div>
            <label className="text-sm font-medium mb-2 block">RPC Endpoint</label>
            <input
              type="text"
              value={rpcEndpoint}
              onChange={(e) => setRpcEndpoint(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              placeholder="https://api.mainnet-beta.solana.com"
            />
            <p className="text-xs text-gray-500 mt-1">
              Solana RPC endpoint for transaction submission
            </p>
          </div>

          {/* WebSocket Endpoint */}
          <div>
            <label className="text-sm font-medium mb-2 block">WebSocket Endpoint</label>
            <input
              type="text"
              value={wsEndpoint}
              onChange={(e) => setWsEndpoint(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              placeholder="wss://api.mainnet-beta.solana.com"
            />
            <p className="text-xs text-gray-500 mt-1">
              WebSocket endpoint for real-time pool monitoring
            </p>
          </div>

          {/* Current Network Info */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <div className="text-sm font-medium mb-2">Current Configuration:</div>
            <div className="space-y-1 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-gray-400">Network:</span>
                <span className={network === 'mainnet' ? 'text-green-400 font-semibold' : 'text-blue-400'}>
                  {network.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">RPC:</span>
                <span className="text-gray-300">{rpcEndpoint}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">WS:</span>
                <span className="text-gray-300">{wsEndpoint}</span>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex gap-2">
            <Button
              onClick={handleSave}
              disabled={loading}
              className="gap-2 flex-1"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Saving...' : 'Save Network Settings'}
            </Button>
            <Button
              onClick={loadSettings}
              variant="outline"
            >
              Reset
            </Button>
          </div>

          {/* Warning for Mainnet */}
          {network === 'mainnet' && (
            <div className="p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <div className="font-semibold text-red-400 mb-1">Mainnet Warning</div>
                  <div className="text-gray-300">
                    You are using <strong>MAINNET</strong>. All transactions will use <strong>REAL SOL</strong> and have <strong>REAL VALUE</strong>.
                    Make sure you understand the risks before proceeding.
                  </div>
                  <ul className="mt-2 space-y-1 text-xs text-gray-400">
                    <li>• Lost funds cannot be recovered</li>
                    <li>• Test thoroughly on devnet first</li>
                    <li>• Use small amounts initially</li>
                    <li>• Double-check all addresses and amounts</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Mainnet Confirmation Modal */}
      {showMainnetWarning && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md border-red-500">
            <CardHeader className="bg-red-500/10">
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="w-6 h-6" />
                Switch to Mainnet?
              </CardTitle>
              <CardDescription>
                This will enable REAL money transactions
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-3">
                    <strong className="text-red-400">⚠️ CRITICAL WARNING:</strong> Switching to Mainnet means:
                  </p>
                  <ul className="space-y-2 text-sm text-gray-400">
                    <li>✓ All SOL used will be <strong className="text-white">REAL MONEY</strong></li>
                    <li>✓ All transactions are <strong className="text-white">IRREVERSIBLE</strong></li>
                    <li>✓ Lost funds <strong className="text-white">CANNOT BE RECOVERED</strong></li>
                    <li>✓ Network fees will apply to all transactions</li>
                    <li>✓ Trading carries risk of total loss</li>
                  </ul>
                </div>

                <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <p className="text-xs text-yellow-300">
                    <strong>Recommendation:</strong> Test all features on Devnet first before using Mainnet.
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowMainnetWarning(false)}
                    variant="outline"
                    className="flex-1"
                  >
                    Cancel - Stay on Devnet
                  </Button>
                  <Button
                    onClick={() => applyNetworkChange('mainnet')}
                    className="flex-1 bg-red-600 hover:bg-red-700"
                  >
                    I Understand - Switch to Mainnet
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

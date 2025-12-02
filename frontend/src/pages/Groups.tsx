import { useState, useEffect } from 'react';
import { Plus, Users, Trash2, DollarSign, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import api from '../services/api';

interface WalletGroup {
  id: number;
  name: string;
  description: string;
  wallet_count: number;
  created_at: string;
}

interface GroupWallet {
  id: number;
  index: number;
  label: string;
  address: string;
  balance?: number;
}

export default function Groups() {
  const [groups, setGroups] = useState<WalletGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null);
  const [groupWallets, setGroupWallets] = useState<GroupWallet[]>([]);
  const [groupBalances, setGroupBalances] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [allWallets, setAllWallets] = useState<any[]>([]);

  // Create Group Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    count: 10,
    password: ''
  });

  // Bulk Operations State
  const [showDistributeModal, setShowDistributeModal] = useState(false);
  const [showCollectModal, setShowCollectModal] = useState(false);
  const [showBulkBuyModal, setShowBulkBuyModal] = useState(false);
  const [showBulkSellModal, setShowBulkSellModal] = useState(false);

  // Load groups and wallets on mount
  useEffect(() => {
    loadGroups();
    loadAllWallets();
  }, []);

  // Load group details when selected
  useEffect(() => {
    if (selectedGroup) {
      loadGroupDetails(selectedGroup);
    }
  }, [selectedGroup]);

  const loadGroups = async () => {
    try {
      const response = await api.get('/group/list');
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const loadAllWallets = async () => {
    try {
      const response = await api.get('/wallet/list');
      setAllWallets(response.data.wallets || []);
    } catch (error) {
      console.error('Failed to load wallets:', error);
    }
  };

  const loadGroupDetails = async (groupId: number) => {
    try {
      setLoading(true);
      const [walletsRes, balancesRes] = await Promise.all([
        api.get(`/group/${groupId}/wallets`),
        api.get(`/group/${groupId}/balances`)
      ]);

      setGroupWallets(walletsRes.data.wallets || []);
      setGroupBalances(balancesRes.data);
    } catch (error) {
      console.error('Failed to load group details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async () => {
    try {
      setLoading(true);
      const response = await api.post('/group/create', createForm);
      
      if (response.data.success) {
        alert(`✅ Created ${createForm.name} with ${createForm.count} wallets!\n\n⚠️ IMPORTANT: Save your mnemonic phrases!\n\nCheck browser console for details.`);
        console.log('🔐 WALLET MNEMONICS - SAVE THESE SECURELY:', response.data.wallets);
        
        setShowCreateModal(false);
        setCreateForm({ name: '', description: '', count: 10, password: '' });
        loadGroups();
      }
    } catch (error: any) {
      alert('❌ Failed to create group: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGroup = async (groupId: number, groupName: string) => {
    if (!confirm(`Delete group "${groupName}" and all its wallets?\n\nThis cannot be undone!`)) {
      return;
    }

    try {
      await api.delete(`/group/${groupId}`);
      alert('✅ Group deleted successfully');
      loadGroups();
      if (selectedGroup === groupId) {
        setSelectedGroup(null);
        setGroupWallets([]);
      }
    } catch (error: any) {
      alert('❌ Failed to delete group: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDistributeSOL = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      setLoading(true);
      const response = await api.post('/group/distribute-sol', {
        from_wallet_id: parseInt(formData.get('from_wallet_id') as string),
        to_group_id: selectedGroup,
        amount_per_wallet: parseFloat(formData.get('amount_per_wallet') as string),
        password: formData.get('password') as string
      });

      alert(`✅ Distributed SOL successfully!\n\n` +
            `Per Wallet: ${formData.get('amount_per_wallet')} SOL\n` +
            `Total Sent: ${response.data.total_sol_sent} SOL to ${response.data.successful} wallets\n` +
            `Failed: ${response.data.failed} wallets`);
      setShowDistributeModal(false);
      loadGroupDetails(selectedGroup!);
    } catch (error: any) {
      alert('❌ Failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCollectSOL = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      setLoading(true);
      const response = await api.post('/group/collect-sol', {
        from_group_id: selectedGroup,
        to_wallet_id: parseInt(formData.get('to_wallet_id') as string),
        password: formData.get('password') as string,
        leave_amount: parseFloat(formData.get('leave_amount') as string || '0.001')
      });

      alert(`✅ Collected SOL successfully!\n\n` +
            `Total Collected: ${response.data.total_collected.toFixed(4)} SOL\n` +
            `From: ${response.data.successful} wallets\n` +
            `To Wallet: ${response.data.target_wallet}\n` +
            `Failed: ${response.data.failed} wallets`);
      setShowCollectModal(false);
      loadGroupDetails(selectedGroup!);
    } catch (error: any) {
      alert('❌ Failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleBulkBuy = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    if (!confirm('Execute bulk buy from all wallets in this group?')) return;

    try {
      setLoading(true);
      const response = await api.post('/group/bulk-buy', {
        group_id: selectedGroup,
        token_address: formData.get('token_address') as string,
        sol_amount: parseFloat(formData.get('sol_amount') as string),
        slippage: parseFloat(formData.get('slippage') as string),
        password: formData.get('password') as string
      });

      alert(`✅ Bulk buy completed!\n\nSuccessful: ${response.data.successful}/${response.data.total_wallets} wallets`);
      setShowBulkBuyModal(false);
    } catch (error: any) {
      alert('❌ Failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleBulkSell = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    if (!confirm('Execute bulk sell from all wallets in this group?')) return;

    try {
      setLoading(true);
      const response = await api.post('/group/bulk-sell', {
        group_id: selectedGroup,
        token_address: formData.get('token_address') as string,
        percentage: parseInt(formData.get('percentage') as string),
        slippage: parseFloat(formData.get('slippage') as string),
        password: formData.get('password') as string
      });

      alert(`✅ Bulk sell completed!\n\nSuccessful: ${response.data.successful}/${response.data.total_wallets} wallets`);
      setShowBulkSellModal(false);
    } catch (error: any) {
      alert('❌ Failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Wallet Groups</h1>
          <p className="text-gray-400 mt-1">Manage multi-wallet groups for bulk operations</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Create Group
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Groups List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Groups ({groups.length})
            </CardTitle>
            <CardDescription>Select a group to view details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {groups.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No groups yet. Create one!</p>
            ) : (
              groups.map(group => (
                <div
                  key={group.id}
                  onClick={() => setSelectedGroup(group.id)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedGroup === group.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold">{group.name}</h3>
                      <p className="text-sm text-gray-400">{group.wallet_count} wallets</p>
                      {group.description && (
                        <p className="text-xs text-gray-500 mt-1">{group.description}</p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteGroup(group.id, group.name);
                      }}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Group Details */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>
                  {selectedGroup ? groups.find(g => g.id === selectedGroup)?.name : 'Select a Group'}
                </CardTitle>
                <CardDescription>
                  {groupBalances && (
                    <span className="text-green-400 font-semibold">
                      Total: {groupBalances.total_balance?.toFixed(4) || '0.0000'} SOL
                    </span>
                  )}
                </CardDescription>
              </div>
              {selectedGroup && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => loadGroupDetails(selectedGroup)}
                  className="gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {!selectedGroup ? (
              <p className="text-gray-500 text-center py-12">
                Select a group from the list to view wallets and perform operations
              </p>
            ) : (
              <div className="space-y-4">
                {/* Bulk Operations Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <Button
                    onClick={() => setShowDistributeModal(true)}
                    variant="outline"
                    className="gap-2"
                  >
                    <DollarSign className="w-4 h-4" />
                    Distribute
                  </Button>
                  <Button
                    onClick={() => setShowCollectModal(true)}
                    variant="outline"
                    className="gap-2"
                  >
                    <DollarSign className="w-4 h-4" />
                    Collect
                  </Button>
                  <Button
                    onClick={() => setShowBulkBuyModal(true)}
                    variant="outline"
                    className="gap-2 text-green-400"
                  >
                    <TrendingUp className="w-4 h-4" />
                    Bulk Buy
                  </Button>
                  <Button
                    onClick={() => setShowBulkSellModal(true)}
                    variant="outline"
                    className="gap-2 text-red-400"
                  >
                    <TrendingDown className="w-4 h-4" />
                    Bulk Sell
                  </Button>
                </div>

                {/* Wallets List */}
                <div className="border border-gray-700 rounded-lg overflow-hidden">
                  <div className="max-h-96 overflow-y-auto">
                    <table className="w-full">
                      <thead className="bg-gray-800 sticky top-0">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-semibold">#</th>
                          <th className="px-4 py-2 text-left text-xs font-semibold">Label</th>
                          <th className="px-4 py-2 text-left text-xs font-semibold">Address</th>
                          <th className="px-4 py-2 text-right text-xs font-semibold">Balance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {groupWallets.map((wallet) => {
                          const balance = groupBalances?.wallets?.find((w: any) => w.id === wallet.id);
                          return (
                            <tr key={wallet.id} className="border-t border-gray-800 hover:bg-gray-800/50">
                              <td className="px-4 py-2 text-sm">{wallet.index}</td>
                              <td className="px-4 py-2 text-sm">{wallet.label}</td>
                              <td className="px-4 py-2 text-sm font-mono text-xs">
                                {wallet.address.slice(0, 4)}...{wallet.address.slice(-4)}
                              </td>
                              <td className="px-4 py-2 text-sm text-right">
                                {balance?.balance?.toFixed(4) || '0.0000'} SOL
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Group Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Create Wallet Group</CardTitle>
              <CardDescription>Auto-generate multiple wallets at once</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Group Name</label>
                  <Input
                    placeholder="e.g., Sniper Group"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Description (optional)</label>
                  <Input
                    placeholder="e.g., For pump.fun sniping"
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Number of Wallets</label>
                  <Input
                    type="number"
                    min="1"
                    max="1000"
                    value={createForm.count}
                    onChange={(e) => setCreateForm({ ...createForm, count: parseInt(e.target.value) })}
                  />
                  <p className="text-xs text-gray-500 mt-1">Min: 1, Max: 1000</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    type="password"
                    placeholder="Encrypt all wallets with this password"
                    value={createForm.password}
                    onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  />
                  <p className="text-xs text-gray-500 mt-1">Same password for all wallets in group</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleCreateGroup}
                    disabled={loading || !createForm.name || !createForm.password}
                    className="flex-1"
                  >
                    {loading ? 'Creating...' : `Create ${createForm.count} Wallets`}
                  </Button>
                  <Button
                    onClick={() => setShowCreateModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
                <p className="text-xs text-yellow-500">
                  ⚠️ Save the mnemonic phrases shown in console after creation!
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Distribute SOL Modal */}
      {showDistributeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Distribute SOL</CardTitle>
              <CardDescription>Send SOL to all wallets in group</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleDistributeSOL} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">From Wallet (Source)</label>
                  <select
                    name="from_wallet_id"
                    required
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select source wallet...</option>
                    {allWallets.map((wallet) => (
                      <option key={wallet.id} value={wallet.id}>
                        ID: {wallet.id} | {wallet.label} | {wallet.address.slice(0, 8)}...{wallet.address.slice(-6)}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Wallet to send SOL from</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Amount per Wallet (SOL)</label>
                  <Input
                    name="amount_per_wallet"
                    type="number"
                    step="0.001"
                    placeholder="0.1"
                    required
                    onChange={(e) => {
                      const input = e.target.nextElementSibling;
                      if (input && e.target.value) {
                        const total = parseFloat(e.target.value) * groupWallets.length;
                        (input as HTMLElement).textContent = `Each wallet gets ${e.target.value} SOL (Total: ${total.toFixed(3)} SOL for ${groupWallets.length} wallets)`;
                      }
                    }}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Each wallet gets [amount] SOL (Total: {groupWallets.length} wallets × amount)
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    name="password"
                    type="password"
                    placeholder="Source wallet password"
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={loading} className="flex-1">
                    {loading ? 'Processing...' : 'Distribute'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowDistributeModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Collect SOL Modal */}
      {showCollectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Collect SOL</CardTitle>
              <CardDescription>Gather SOL from all wallets to one</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCollectSOL} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">To Wallet (Destination)</label>
                  <select
                    name="to_wallet_id"
                    required
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select destination wallet...</option>
                    {allWallets.map((wallet) => (
                      <option key={wallet.id} value={wallet.id}>
                        ID: {wallet.id} | {wallet.label} | {wallet.address.slice(0, 8)}...{wallet.address.slice(-6)}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Wallet to collect SOL into</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Leave Amount (SOL)</label>
                  <Input
                    name="leave_amount"
                    type="number"
                    step="0.001"
                    defaultValue="0.001"
                    placeholder="0.001"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Amount to leave in each wallet for rent
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    name="password"
                    type="password"
                    placeholder="Group wallets password"
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={loading} className="flex-1">
                    {loading ? 'Processing...' : 'Collect'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowCollectModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Bulk Buy Modal */}
      {showBulkBuyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-green-400">Bulk Buy</CardTitle>
              <CardDescription>Buy token from all wallets</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleBulkBuy} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Token Address</label>
                  <Input
                    name="token_address"
                    placeholder="Token mint address"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">SOL Amount per Wallet</label>
                  <Input
                    name="sol_amount"
                    type="number"
                    step="0.001"
                    placeholder="0.05"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Slippage (%)</label>
                  <Input
                    name="slippage"
                    type="number"
                    step="0.1"
                    defaultValue="5.0"
                    placeholder="5.0"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    name="password"
                    type="password"
                    placeholder="Group wallets password"
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={loading} className="flex-1 bg-green-600 hover:bg-green-700">
                    {loading ? 'Processing...' : 'Buy from All Wallets'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowBulkBuyModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Bulk Sell Modal */}
      {showBulkSellModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-red-400">Bulk Sell</CardTitle>
              <CardDescription>Sell token from all wallets</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleBulkSell} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Token Address</label>
                  <Input
                    name="token_address"
                    placeholder="Token mint address"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Percentage to Sell (%)</label>
                  <Input
                    name="percentage"
                    type="number"
                    min="1"
                    max="100"
                    defaultValue="100"
                    placeholder="100"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">100 = Sell all tokens</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Slippage (%)</label>
                  <Input
                    name="slippage"
                    type="number"
                    step="0.1"
                    defaultValue="5.0"
                    placeholder="5.0"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Password</label>
                  <Input
                    name="password"
                    type="password"
                    placeholder="Group wallets password"
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={loading} className="flex-1 bg-red-600 hover:bg-red-700">
                    {loading ? 'Processing...' : 'Sell from All Wallets'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowBulkSellModal(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

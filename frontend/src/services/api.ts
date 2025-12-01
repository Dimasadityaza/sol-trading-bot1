import axios from 'axios'
import type {
  Wallet,
  CreateWalletRequest,
  ImportWalletRequest,
  SniperConfig,
  SniperConfigRequest,
  SniperStartRequest,
  SniperStatus
} from '@/types'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Wallet API
export const walletApi = {
  create: async (data: CreateWalletRequest): Promise<Wallet> => {
    const response = await api.post('/wallet/create', data)
    return response.data
  },

  import: async (data: ImportWalletRequest): Promise<Wallet> => {
    const response = await api.post('/wallet/import', data)
    return response.data
  },

  list: async (): Promise<Wallet[]> => {
    const response = await api.get('/wallet/list')
    return response.data
  },

  get: async (id: number): Promise<Wallet> => {
    const response = await api.get(`/wallet/${id}`)
    return response.data
  },

  getBalance: async (id: number) => {
    const response = await api.get(`/wallet/${id}/balance`)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/wallet/${id}`)
    return response.data
  },
}

// Sniper API
export const sniperApi = {
  getConfig: async (walletId: number): Promise<SniperConfig> => {
    const response = await api.get(`/sniper/config/${walletId}`)
    return response.data
  },

  saveConfig: async (data: SniperConfigRequest): Promise<SniperConfig> => {
    const response = await api.post('/sniper/config', data)
    return response.data
  },

  start: async (data: SniperStartRequest) => {
    const response = await api.post('/sniper/start', data)
    return response.data
  },

  stop: async () => {
    const response = await api.post('/sniper/stop')
    return response.data
  },

  getStatus: async (): Promise<SniperStatus> => {
    const response = await api.get('/sniper/status')
    return response.data
  },

  setupGroupSniper: async (data: any) => {
    const response = await api.post('/sniper/group/setup', data)
    return response.data
  },

  startManualSnipe: async (data: any) => {
    const response = await api.post('/sniper/manual', data)
    return response.data
  },
}

// Groups API
export const groupsApi = {
  listGroups: async () => {
    const response = await api.get('/group/list')
    return response.data
  },

  getGroup: async (groupId: number) => {
    const response = await api.get(`/group/${groupId}`)
    return response.data
  },

  createGroup: async (data: any) => {
    const response = await api.post('/group/create', data)
    return response.data
  },

  deleteGroup: async (groupId: number) => {
    const response = await api.delete(`/group/${groupId}`)
    return response.data
  },

  getGroupWallets: async (groupId: number) => {
    const response = await api.get(`/group/${groupId}/wallets`)
    return response.data
  },

  getGroupBalances: async (groupId: number) => {
    const response = await api.get(`/group/${groupId}/balances`)
    return response.data
  },
}

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api

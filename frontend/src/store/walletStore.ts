import { create } from 'zustand'
import type { Wallet } from '@/types'

interface WalletStore {
  wallets: Wallet[]
  selectedWallet: Wallet | null
  isLoading: boolean
  error: string | null
  
  setWallets: (wallets: Wallet[]) => void
  addWallet: (wallet: Wallet) => void
  removeWallet: (id: number) => void
  selectWallet: (wallet: Wallet | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  updateWalletBalance: (id: number, balance: number) => void
}

export const useWalletStore = create<WalletStore>((set) => ({
  wallets: [],
  selectedWallet: null,
  isLoading: false,
  error: null,

  setWallets: (wallets) => set({ wallets }),
  
  addWallet: (wallet) => 
    set((state) => ({ 
      wallets: [...state.wallets, wallet],
      selectedWallet: state.selectedWallet || wallet 
    })),
  
  removeWallet: (id) => 
    set((state) => ({
      wallets: state.wallets.filter((w) => w.id !== id),
      selectedWallet: state.selectedWallet?.id === id ? null : state.selectedWallet
    })),
  
  selectWallet: (wallet) => set({ selectedWallet: wallet }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  updateWalletBalance: (id, balance) =>
    set((state) => ({
      wallets: state.wallets.map((w) => 
        w.id === id ? { ...w, balance } : w
      ),
      selectedWallet: state.selectedWallet?.id === id 
        ? { ...state.selectedWallet, balance }
        : state.selectedWallet
    })),
}))

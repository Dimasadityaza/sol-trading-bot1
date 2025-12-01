import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Wallets } from './pages/Wallets'
import { Trading } from './pages/Trading'
import { Settings } from './pages/Settings'
import Groups from './pages/Groups'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="wallets" element={<Wallets />} />
            <Route path="groups" element={<Groups />} />
            <Route path="trading" element={<Trading />} />
            <Route path="sniper" element={<div className="text-center py-12">Sniper Config - Coming Soon</div>} />
            <Route path="copy-trading" element={<div className="text-center py-12">Copy Trading - Coming Soon</div>} />
            <Route path="analytics" element={<div className="text-center py-12">Analytics - Coming Soon</div>} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

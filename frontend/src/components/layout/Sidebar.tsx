import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Wallet, 
  Target, 
  TrendingUp, 
  Users, 
  BarChart3, 
  Settings 
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Wallets', href: '/wallets', icon: Wallet },
  { name: 'Groups', href: '/groups', icon: Users },
  { name: 'Trading', href: '/trading', icon: TrendingUp },
  { name: 'Sniper Config', href: '/sniper', icon: Target },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <div className="flex h-screen w-64 flex-col fixed left-0 top-0 border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Target className="h-6 w-6 text-primary" />
        <span className="ml-2 text-lg font-semibold">Sniper Bot</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <div>Solana Sniper Bot v2.0</div>
          <div className="mt-1">Multi-Wallet Groups</div>
        </div>
      </div>
    </div>
  )
}

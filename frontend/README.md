# Solana Sniper Bot - Frontend

React + TypeScript + Tailwind CSS + Shadcn/ui

## ✅ Phase 2 Complete

### Features Implemented:
- ✅ React + TypeScript setup
- ✅ Tailwind CSS dark theme
- ✅ Responsive layout (Sidebar + TopBar)
- ✅ Wallet management UI
- ✅ Dashboard with stats
- ✅ Create wallet modal
- ✅ Zustand state management
- ✅ React Query data fetching
- ✅ API integration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Backend (Required)
```bash
# In backend directory
cd ../backend
python3 -m uvicorn src.api.main:app --reload
```

### 3. Start Frontend
```bash
npm run dev
```

Frontend will run on: `http://localhost:5173`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Shadcn components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── input.tsx
│   │   ├── layout/
│   │   │   ├── Layout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── TopBar.tsx
│   │   └── wallet/
│   │       ├── WalletCard.tsx
│   │       └── CreateWalletModal.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx    ✅ Complete
│   │   ├── Wallets.tsx      ✅ Complete
│   │   ├── Trading.tsx      ⏳ Placeholder
│   │   └── Settings.tsx     ⏳ Placeholder
│   ├── store/
│   │   └── walletStore.ts   ✅ Zustand store
│   ├── services/
│   │   └── api.ts           ✅ API client
│   ├── lib/
│   │   └── utils.ts         ✅ Utilities
│   ├── types/
│   │   └── index.ts         ✅ TypeScript types
│   ├── App.tsx              ✅ Routes
│   ├── main.tsx             ✅ Entry point
│   └── index.css            ✅ Tailwind styles
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 🎨 Features

### Dashboard
- Portfolio overview
- Total balance across all wallets
- Stats cards (PnL, Win Rate, etc.)
- Active positions display
- Recent activity feed

### Wallets Page
- List all wallets
- Create new wallet
- Import existing wallet
- View wallet details
- Check balance
- Copy address
- Delete wallet
- Select active wallet

### Layout
- Fixed sidebar navigation
- Top bar with wallet selector
- Real-time balance display
- Connection status indicator
- Dark theme

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Query** - Data fetching
- **React Router** - Routing
- **Axios** - HTTP client
- **Lucide React** - Icons

## 📝 Available Scripts

```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## 🎯 Usage

### Create Wallet
1. Go to Wallets page
2. Click "Create Wallet"
3. Enter label and password
4. Click "Create Wallet"
5. Wallet appears in list

### View Dashboard
1. Select a wallet from Wallets page
2. Go to Dashboard
3. See portfolio overview
4. View stats and activity

### Switch Wallets
- Click on any wallet card to select it
- Selected wallet appears in top bar
- Use selected wallet for trading

## 🔌 API Integration

Frontend connects to backend at `http://localhost:8000`

Endpoints used:
- `POST /wallet/create` - Create wallet
- `POST /wallet/import` - Import wallet
- `GET /wallet/list` - List wallets
- `GET /wallet/{id}` - Get wallet
- `GET /wallet/{id}/balance` - Get balance
- `DELETE /wallet/{id}` - Delete wallet

## 🎨 UI Components

All components follow Shadcn/ui patterns:
- Button - Multiple variants (default, destructive, outline, etc.)
- Card - Container with header, content, footer
- Input - Styled form inputs
- Modal - Overlay dialogs

Custom components:
- WalletCard - Display wallet info
- CreateWalletModal - Wallet creation form
- Sidebar - Navigation menu
- TopBar - Wallet selector + stats

## 🚧 TODO (Phase 3+)

- [ ] Trading interface
- [ ] Token search
- [ ] Buy/Sell forms
- [ ] Transaction history
- [ ] Sniper configuration
- [ ] Copy trading UI
- [ ] Analytics charts
- [ ] Settings page
- [ ] Toast notifications
- [ ] Loading states
- [ ] Error handling UI

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### API not connecting
- Make sure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in `src/services/api.ts`

### npm install fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📊 Status

**Phase 2: COMPLETE ✅**

Working features:
- ✅ Full UI framework
- ✅ Wallet management
- ✅ Dashboard
- ✅ Dark theme
- ✅ Responsive layout
- ✅ API integration
- ✅ State management

Next: Phase 3 - Trading Engine

---

**Built with React + TypeScript + Tailwind CSS**

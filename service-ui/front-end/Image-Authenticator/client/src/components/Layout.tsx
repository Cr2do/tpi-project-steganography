import React from 'react';
import { useLocation, Link } from 'wouter';
import { nanoid } from 'nanoid';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  FileImage, 
  Settings, 
  LogOut, 
  Activity,
  Cpu
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { mockUser } from '@/lib/mockData';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: FileImage, label: 'My Assets', href: '/assets' },
    { icon: ShieldCheck, label: 'Verify', href: '/verify' },
    { icon: Settings, label: 'Settings', href: '/settings' },
  ];

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card/50 backdrop-blur-md flex flex-col z-20">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2 text-primary">
            <ShieldCheck className="h-8 w-8" />
            <span className="text-xl font-bold tracking-tighter font-mono">ImmuSign</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground font-mono flex items-center gap-1">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            NET: STABLE
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-md transition-all duration-200 cursor-pointer group border border-transparent",
                  location === item.href 
                    ? "bg-primary/10 text-primary border-primary/20 shadow-[0_0_10px_rgba(var(--primary),0.2)]" 
                    : "hover:bg-accent/50 hover:text-accent-foreground text-muted-foreground"
                )}
              >
                <item.icon className={cn("h-5 w-5", location === item.href && "text-primary")} />
                <span className="font-medium">{item.label}</span>
                {location === item.href && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute left-0 w-1 h-6 bg-primary rounded-r-full"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  />
                )}
              </div>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-border bg-black/20">
          <div className="flex items-center gap-3 p-2 rounded-lg border border-border/50 bg-background/50">
            <div className="h-8 w-8 rounded bg-primary/20 flex items-center justify-center text-primary font-mono font-bold">
              {mockUser.username[0]}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{mockUser.username}</div>
              <div className="text-xs text-muted-foreground truncate font-mono" title={mockUser.publicKey}>
                {mockUser.publicKey.substring(0, 8)}...
              </div>
            </div>
            <LogOut className="h-4 w-4 text-muted-foreground hover:text-foreground cursor-pointer" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto relative">
        {/* Header */}
        <header className="h-16 border-b border-border bg-background/50 backdrop-blur-sm sticky top-0 z-10 flex items-center justify-between px-6">
          <div className="flex items-center gap-4 text-sm text-muted-foreground font-mono">
            <span className="flex items-center gap-2">
              <Cpu className="h-4 w-4" /> NODE_ID: {nanoid(6)}
            </span>
            <span className="w-px h-4 bg-border" />
            <span className="flex items-center gap-2">
              <Activity className="h-4 w-4" /> LATENCY: 24ms
            </span>
          </div>
          <div className="flex items-center gap-4">
             {/* Add header actions if needed */}
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto pb-20">
          {children}
        </div>
      </main>
    </div>
  );
}

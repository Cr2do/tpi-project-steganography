import React, { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { ShieldCheck, Fingerprint, ArrowRight, Lock, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import heroBg from '@/assets/hero-bg.png';

export default function Auth() {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState<'login' | 'generating'>('login');
  const [keys, setKeys] = useState<{ public: string, private: string } | null>(null);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setStep('generating');
    
    // Simulate key generation
    setTimeout(() => {
      setKeys({
        public: '0x7e2...3f9',
        private: '••••••••••••••••'
      });
      setTimeout(() => {
        setLocation('/dashboard');
      }, 2000);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex overflow-hidden">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex w-1/2 relative flex-col justify-between p-12 overflow-hidden bg-black">
        <div className="absolute inset-0 z-0">
          <img src={heroBg} className="w-full h-full object-cover opacity-60" />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
        </div>
        
        <div className="relative z-10">
           <div className="flex items-center gap-3 text-white mb-8">
              <ShieldCheck className="h-10 w-10 text-primary" />
              <span className="text-3xl font-bold font-mono tracking-tighter">ImmuSign</span>
           </div>
           
           <h1 className="text-5xl font-bold text-white leading-tight max-w-lg font-sans">
              Immutable Truth in a Digital World.
           </h1>
           <p className="mt-6 text-xl text-gray-400 max-w-md">
              Secure your visual assets with military-grade blockchain steganography.
           </p>
        </div>

        <div className="relative z-10 grid grid-cols-2 gap-6">
           <div className="p-4 rounded-lg bg-white/5 backdrop-blur border border-white/10">
              <Lock className="h-6 w-6 text-primary mb-2" />
              <h3 className="font-bold text-white">Cryptographic Proof</h3>
              <p className="text-sm text-gray-400">SHA-256 signatures embedded in every pixel.</p>
           </div>
           <div className="p-4 rounded-lg bg-white/5 backdrop-blur border border-white/10">
              <Eye className="h-6 w-6 text-primary mb-2" />
              <h3 className="font-bold text-white">Deepfake Detection</h3>
              <p className="text-sm text-gray-400">AI-powered analysis of synthesis artifacts.</p>
           </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background relative">
        <div className="absolute inset-0 pointer-events-none opacity-20"
             style={{
               backgroundImage: 'radial-gradient(#4f46e5 1px, transparent 1px)',
               backgroundSize: '24px 24px'
             }}
        />

        <Card className="w-full max-w-md border-border bg-card/80 backdrop-blur-xl shadow-2xl relative z-10 overflow-hidden">
           {/* Top line decoration */}
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-accent to-primary" />

           <CardContent className="p-8">
             {step === 'login' ? (
               <motion.form 
                 initial={{ opacity: 0, x: 20 }}
                 animate={{ opacity: 1, x: 0 }}
                 className="space-y-6"
                 onSubmit={handleLogin}
               >
                 <div className="space-y-2 text-center">
                    <h2 className="text-2xl font-bold tracking-tight">Access Secure Vault</h2>
                    <p className="text-sm text-muted-foreground">Enter your credentials to decrypt your dashboard.</p>
                 </div>

                 <div className="space-y-4">
                    <div className="space-y-2">
                       <label className="text-xs font-mono uppercase font-bold text-muted-foreground">Identity Handle</label>
                       <Input placeholder="usr_8x92..." className="font-mono bg-secondary/50" defaultValue="usr_demo_access" />
                    </div>
                    <div className="space-y-2">
                       <label className="text-xs font-mono uppercase font-bold text-muted-foreground">Private Key / Password</label>
                       <Input type="password" placeholder="••••••••" className="font-mono bg-secondary/50" defaultValue="password" />
                    </div>
                 </div>

                 <Button type="submit" className="w-full h-12 text-lg font-bold shadow-[0_0_20px_rgba(var(--primary),0.3)] hover:shadow-[0_0_30px_rgba(var(--primary),0.5)] transition-all">
                    Connect Node <ArrowRight className="ml-2 h-5 w-5" />
                 </Button>
               </motion.form>
             ) : (
               <motion.div 
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 className="py-12 flex flex-col items-center justify-center text-center space-y-6"
               >
                 <div className="relative h-24 w-24">
                    <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                    <div className="absolute inset-0 rounded-full border-4 border-t-primary animate-spin" />
                    <Fingerprint className="h-12 w-12 text-primary absolute inset-0 m-auto animate-pulse" />
                 </div>
                 
                 <div className="space-y-2">
                    <h3 className="text-xl font-bold font-mono">Handshaking...</h3>
                    <p className="text-sm text-muted-foreground font-mono">
                      Verifying cryptographic keys
                    </p>
                 </div>

                 <div className="w-full bg-black/10 rounded p-4 font-mono text-xs text-left space-y-1 opacity-70">
                    <div className="text-emerald-500">{'>'} Establishing secure tunnel... OK</div>
                    <div className="text-emerald-500">{'>'} Validating signature... OK</div>
                    <div className="animate-pulse">{'>'} Decrypting user assets...</div>
                 </div>
               </motion.div>
             )}
           </CardContent>
        </Card>
      </div>
    </div>
  );
}

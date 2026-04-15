import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, ShieldCheck, AlertOctagon, Search, FileX, CheckCircle, Fingerprint, ScanLine } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

export default function Verify() {
  const [status, setStatus] = useState<'idle' | 'scanning' | 'verified' | 'tampered'>('idle');
  const [progress, setProgress] = useState(0);
  const [file, setFile] = useState<File | null>(null);

  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0];
    if (!f) return;
    
    setFile(f);
    setStatus('scanning');
    setProgress(0);

    // Simulate scanning process
    let p = 0;
    const interval = setInterval(() => {
      p += Math.random() * 10;
      if (p >= 100) {
        clearInterval(interval);
        setProgress(100);
        // Randomly decide result for demo
        setStatus(Math.random() > 0.3 ? 'verified' : 'tampered');
      } else {
        setProgress(p);
      }
    }, 200);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    maxFiles: 1,
    disabled: status === 'scanning'
  });

  const reset = () => {
    setStatus('idle');
    setFile(null);
    setProgress(0);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold font-sans">Verification Terminal</h1>
        <p className="text-muted-foreground font-mono">
          Upload any asset to validate its cryptographic signature against the ledger.
        </p>
      </div>

      <div className="relative min-h-[400px]">
        <AnimatePresence mode="wait">
          {status === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="absolute inset-0"
            >
              <div 
                {...getRootProps()} 
                className={cn(
                  "h-full rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-12 text-center transition-all cursor-pointer bg-card/30 backdrop-blur hover:bg-card/50",
                  isDragActive ? "border-primary bg-primary/5 shadow-[0_0_30px_rgba(var(--primary),0.2)]" : "border-border hover:border-primary/50"
                )}
              >
                <input {...getInputProps()} />
                <div className="h-20 w-20 rounded-full bg-secondary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                   <Search className="h-10 w-10 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-medium mb-2">Drop asset to verify</h3>
                <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                  Supports forensic analysis for JPEG, PNG, WEBP, and TIFF formats.
                </p>
              </div>
            </motion.div>
          )}

          {status === 'scanning' && (
            <motion.div
              key="scanning"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center bg-black/5 rounded-xl border border-border p-12 backdrop-blur-sm"
            >
               <div className="relative h-32 w-32 mb-8">
                  <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
                  <div 
                    className="absolute inset-0 rounded-full border-4 border-t-primary border-r-transparent border-b-transparent border-l-transparent animate-spin" 
                  />
                  <ScanLine className="h-12 w-12 text-primary absolute inset-0 m-auto animate-pulse" />
               </div>
               <h3 className="text-2xl font-bold font-mono animate-pulse">ANALYZING INTEGRITY...</h3>
               <div className="w-full max-w-md mt-8 space-y-2">
                  <Progress value={progress} className="h-2" />
                  <div className="flex justify-between text-xs font-mono text-muted-foreground">
                     <span>HASHING_CONTENT</span>
                     <span>{Math.round(progress)}%</span>
                  </div>
               </div>
            </motion.div>
          )}

          {status === 'verified' && (
            <motion.div
              key="verified"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center bg-emerald-950/10 rounded-xl border-2 border-emerald-500/50 p-12 backdrop-blur-md"
            >
               <div className="h-24 w-24 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                  <CheckCircle className="h-12 w-12 text-emerald-500" />
               </div>
               <h2 className="text-3xl font-bold text-emerald-500 mb-2 tracking-tight">AUTHENTICITY CONFIRMED</h2>
               <p className="text-emerald-500/70 font-mono mb-8">Signature matches blockchain record #8X92-A</p>
               
               <div className="grid grid-cols-2 gap-4 w-full max-w-lg mb-8">
                  <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded">
                     <div className="text-xs uppercase text-emerald-500/50 mb-1">Owner</div>
                     <div className="font-mono text-emerald-500">@DemoUser</div>
                  </div>
                  <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded">
                     <div className="text-xs uppercase text-emerald-500/50 mb-1">Integrity</div>
                     <div className="font-mono text-emerald-500">100% UNMODIFIED</div>
                  </div>
               </div>

               <Button onClick={reset} variant="outline" className="border-emerald-500/30 text-emerald-500 hover:bg-emerald-500/10">
                  Verify Another Asset
               </Button>
            </motion.div>
          )}

          {status === 'tampered' && (
            <motion.div
              key="tampered"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center bg-red-950/10 rounded-xl border-2 border-red-500/50 p-12 backdrop-blur-md"
            >
               <div className="h-24 w-24 rounded-full bg-red-500/20 flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(239,68,68,0.3)]">
                  <AlertOctagon className="h-12 w-12 text-red-500" />
               </div>
               <h2 className="text-3xl font-bold text-red-500 mb-2 tracking-tight">TAMPERING DETECTED</h2>
               <p className="text-red-500/70 font-mono mb-8">Hash mismatch. File has been modified.</p>
               
               <div className="w-full max-w-lg space-y-3 mb-8">
                  <div className="p-3 bg-red-950/20 border border-red-500/20 rounded flex justify-between items-center">
                     <span className="text-sm text-red-200">Compression Artifacts</span>
                     <span className="text-xs font-bold bg-red-500/20 text-red-400 px-2 py-1 rounded">DETECTED</span>
                  </div>
                  <div className="p-3 bg-red-950/20 border border-red-500/20 rounded flex justify-between items-center">
                     <span className="text-sm text-red-200">Metadata Stripped</span>
                     <span className="text-xs font-bold bg-red-500/20 text-red-400 px-2 py-1 rounded">YES</span>
                  </div>
               </div>

               <Button onClick={reset} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                  Verify Another Asset
               </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

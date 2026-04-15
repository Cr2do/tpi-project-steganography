import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Upload, FileUp, CheckCircle, AlertTriangle, Fingerprint, Activity, Clock, Share2, Download, AlertOctagon, RefreshCw, Zap } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { cn } from '@/lib/utils';
import { generateMockAsset, ImageAsset } from '@/lib/mockData';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

export default function Dashboard() {
  const [assets, setAssets] = useState<ImageAsset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<ImageAsset | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isCorrupted, setIsCorrupted] = useState(false);

  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    setIsUploading(true);
    // Simulate processing delay
    setTimeout(() => {
      const newAssets = acceptedFiles.map(generateMockAsset);
      setAssets(prev => [...newAssets, ...prev]);
      setSelectedAsset(newAssets[0]);
      setIsUploading(false);
      setIsCorrupted(false);
    }, 2000);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const toggleCorruption = () => {
    setIsCorrupted(!isCorrupted);
  };

  const currentScore = isCorrupted ? 0 : (selectedAsset?.authenticityScore || 0);

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 border-primary/20 bg-card/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Recent Activity
            </CardTitle>
            <CardDescription>Live feed of your secured assets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] flex items-center justify-center border border-dashed border-border rounded-lg bg-black/5">
              {assets.length === 0 ? (
                <div className="text-center space-y-4 p-8">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-4">
                    <Upload className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-medium">No assets secured yet</h3>
                  <p className="text-muted-foreground text-sm max-w-sm mx-auto">
                    Upload images to generate cryptographic signatures and timestamp them on the blockchain.
                  </p>
                </div>
              ) : (
                <div className="w-full h-full overflow-hidden relative">
                   {/* Simplified Visualization of "Chain" */}
                   <div className="absolute inset-0 flex items-center gap-4 px-4 overflow-x-auto">
                      {assets.map((asset, i) => (
                        <motion.div 
                          key={asset.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="flex-shrink-0 w-32 h-32 rounded-lg border border-border bg-background overflow-hidden relative cursor-pointer group"
                          onClick={() => {
                            setSelectedAsset(asset);
                            setIsCorrupted(false);
                          }}
                        >
                          <img src={asset.url} className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity" />
                          <div className="absolute bottom-0 left-0 right-0 p-1 bg-black/80 text-[10px] font-mono text-white truncate">
                            {asset.hash.substring(0, 8)}
                          </div>
                          {asset.id === selectedAsset?.id && (
                             <div className="absolute inset-0 ring-2 ring-primary z-10 pointer-events-none" />
                          )}
                        </motion.div>
                      ))}
                   </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Upload Area */}
        <Card className="border-primary/20 bg-card/50 backdrop-blur flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileUp className="h-5 w-5 text-primary" />
              Secure New Asset
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1">
            <div 
              {...getRootProps()} 
              className={cn(
                "h-full min-h-[200px] rounded-lg border-2 border-dashed flex flex-col items-center justify-center p-6 text-center transition-all cursor-pointer relative overflow-hidden",
                isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-accent/50",
                isUploading && "pointer-events-none"
              )}
            >
              <input {...getInputProps()} />
              
              {isUploading ? (
                <div className="space-y-4 z-10 relative">
                  <div className="relative h-16 w-16 mx-auto">
                    <div className="absolute inset-0 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
                    <Fingerprint className="h-8 w-8 text-primary absolute inset-0 m-auto animate-pulse" />
                  </div>
                  <div>
                    <p className="text-sm font-medium animate-pulse">Hashing & Signing...</p>
                    <p className="text-xs text-muted-foreground font-mono mt-1">Generating SHA-256...</p>
                  </div>
                </div>
              ) : (
                <>
                  <div className="h-12 w-12 rounded-full bg-secondary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <p className="text-sm font-medium">Drag & drop or click to upload</p>
                  <p className="text-xs text-muted-foreground mt-2">Supports JPG, PNG, WEBP, TIFF</p>
                </>
              )}
              
              {/* Scanline Effect */}
              {isUploading && <div className="scan-line" />}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Asset Detail View */}
      <AnimatePresence mode="wait">
        {selectedAsset && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
          >
            {/* Left Column: Image & Authenticity */}
            <div className="lg:col-span-2 space-y-6">
              <Card className={cn(
                "overflow-hidden border-primary/20 transition-colors duration-500",
                isCorrupted ? "border-red-500/50 bg-red-950/10" : "bg-black/20"
              )}>
                 <div className="relative aspect-video flex items-center justify-center bg-black/40">
                    <img src={selectedAsset.url} className="max-h-full max-w-full object-contain shadow-2xl" />
                    
                    {/* Overlay Badges */}
                    <div className="absolute top-4 left-4 flex gap-2">
                       <Badge variant={isCorrupted ? "destructive" : (currentScore > 80 ? "default" : "destructive")} className="font-mono uppercase tracking-wider transition-colors duration-300">
                          {isCorrupted ? "COMPROMISED" : (currentScore > 80 ? "VERIFIED" : "FLAGGED")}
                       </Badge>
                       <Badge variant="outline" className="bg-black/50 backdrop-blur text-white border-white/20 font-mono">
                          {selectedAsset.metadata.format}
                       </Badge>
                    </div>

                    {isCorrupted && (
                      <div className="absolute inset-0 bg-red-500/10 flex items-center justify-center backdrop-blur-[2px]">
                        <div className="bg-red-950/90 border border-red-500 p-4 rounded text-red-500 font-bold font-mono text-xl animate-pulse">
                          CRYPTOGRAPHIC FAILURE
                        </div>
                      </div>
                    )}
                 </div>
                 
                 <div className="p-6 border-t border-border bg-card">
                    <div className="flex items-center justify-between mb-6">
                       <div>
                          <h2 className="text-2xl font-bold font-sans flex items-center gap-2">
                            {selectedAsset.name}
                            {isCorrupted && <AlertOctagon className="h-6 w-6 text-red-500 animate-bounce" />}
                          </h2>
                          <div className="text-xs font-mono text-muted-foreground mt-1 flex gap-4">
                             <span>SIZE: {selectedAsset.metadata.size}</span>
                             <span>DIM: {selectedAsset.metadata.dimensions}</span>
                          </div>
                       </div>
                       <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={toggleCorruption}
                            className={cn("border-dashed", isCorrupted ? "bg-red-50 border-red-200 text-red-600" : "text-muted-foreground")}
                          >
                            <Zap className="h-4 w-4 mr-2" /> 
                            {isCorrupted ? "Restore Hash" : "Simulate Attack"}
                          </Button>
                          <Button variant="outline" size="sm"><Share2 className="h-4 w-4 mr-2" /> Share</Button>
                          <Button variant="outline" size="sm"><Download className="h-4 w-4 mr-2" /> Export</Button>
                       </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                       <div className={cn(
                         "p-4 rounded-lg border transition-colors duration-500",
                         isCorrupted ? "bg-red-50 border-red-200" : "bg-secondary/50 border-border"
                       )}>
                          <div className="text-xs text-muted-foreground font-mono mb-2 uppercase tracking-wider">Authenticity Score</div>
                          <div className="flex items-end gap-2">
                             <span className={cn(
                                "text-4xl font-bold font-mono transition-colors duration-300",
                                isCorrupted ? "text-red-600" : (currentScore > 80 ? "text-primary" : "text-destructive")
                             )}>
                                {currentScore}%
                             </span>
                             <span className="text-sm mb-1 text-muted-foreground">confidence</span>
                          </div>
                          <Progress value={currentScore} className={cn("h-1 mt-3", isCorrupted ? "bg-red-200" : (currentScore > 80 ? "bg-primary/20" : "bg-destructive/20"))} />
                       </div>

                       <div className="p-4 rounded-lg bg-secondary/50 border border-border">
                          <div className="text-xs text-muted-foreground font-mono mb-2 uppercase tracking-wider">AI Probability</div>
                          <div className="flex items-end gap-2">
                             <span className={cn(
                                "text-4xl font-bold font-mono",
                                selectedAsset.metadata.aiProbability > 0.5 ? "text-amber-500" : "text-emerald-500"
                             )}>
                                {(selectedAsset.metadata.aiProbability * 100).toFixed(1)}%
                             </span>
                          </div>
                          <div className="text-xs mt-2 text-muted-foreground">
                             {selectedAsset.metadata.aiProbability > 0.5 ? "Synthetic patterns detected" : "Natural noise patterns"}
                          </div>
                       </div>
                    </div>
                 </div>
              </Card>

              {/* Degradation Analysis */}
               <Card>
                  <CardHeader>
                     <CardTitle className="text-sm font-mono uppercase tracking-widest text-muted-foreground">Integrity Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                     <div className="space-y-4">
                        <div className={cn(
                          "flex items-center justify-between p-3 rounded transition-colors duration-300",
                          isCorrupted ? "bg-red-50 text-red-700" : "bg-secondary/30"
                        )}>
                           <div className="flex items-center gap-3">
                              {isCorrupted ? <AlertTriangle className="h-5 w-5 text-red-500" /> : <CheckCircle className="h-5 w-5 text-emerald-500" />}
                              <span className="font-medium">{isCorrupted ? "Signature Mismatch Detected" : "Cryptographic Signature Valid"}</span>
                           </div>
                           <span className="font-mono text-xs opacity-70">{isCorrupted ? "ERR_HASH_INVALID" : "SIG_OK_294"}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 rounded bg-secondary/30">
                           <div className="flex items-center gap-3">
                              <CheckCircle className="h-5 w-5 text-emerald-500" />
                              <span className="font-medium">Metadata Consistency Check</span>
                           </div>
                           <span className="font-mono text-xs text-muted-foreground">META_OK</span>
                        </div>
                        <div className="flex items-center justify-between p-3 rounded bg-amber-500/10 border border-amber-500/20">
                           <div className="flex items-center gap-3">
                              <AlertTriangle className="h-5 w-5 text-amber-500" />
                              <span className="font-medium text-amber-500">Compression Artifacts Detected</span>
                           </div>
                           <span className="font-mono text-xs text-amber-500/70">JPEG_QUAL_85</span>
                        </div>
                     </div>
                  </CardContent>
               </Card>
            </div>

            {/* Right Column: Technical Details */}
            <div className="space-y-6">
               <Card className="h-full border-l-4 border-l-primary bg-card/80 backdrop-blur">
                  <CardHeader>
                     <CardTitle className="font-mono text-lg">Blockchain Ledger</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                     <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Asset Hash (SHA-256)</label>
                        <div className={cn(
                          "font-mono text-xs break-all p-3 rounded border shadow-[0_0_15px_rgba(var(--primary),0.1)] transition-colors duration-300",
                          isCorrupted ? "bg-red-950 text-red-500 border-red-500/50" : "bg-black/80 text-primary border-primary/20"
                        )}>
                           {isCorrupted ? "0xINVALID_HASH_SEQUENCE_CORRUPTED_BLOCK_A92" : selectedAsset.hash}
                        </div>
                     </div>

                     <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Digital Signature</label>
                        <div className="font-mono text-xs break-all p-3 bg-secondary rounded border border-border text-muted-foreground">
                           {selectedAsset.signature}
                        </div>
                     </div>

                     <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Owner Public Key</label>
                        <div className="font-mono text-xs break-all p-3 bg-secondary rounded border border-border text-muted-foreground">
                           {selectedAsset.ownerId}
                        </div>
                     </div>

                     <div className="mt-8 pt-6 border-t border-border">
                        <h4 className="text-sm font-bold mb-4 flex items-center gap-2">
                           <Clock className="h-4 w-4" /> History Chain
                        </h4>
                        <div className="relative pl-4 border-l border-border space-y-6">
                           {selectedAsset.history.map((event, i) => (
                              <div key={i} className="relative">
                                 <div className="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-primary ring-4 ring-background" />
                                 <div className="text-xs font-mono text-muted-foreground">{new Date(event.timestamp).toLocaleString()}</div>
                                 <div className="font-medium text-sm mt-1">{event.action}</div>
                                 <div className="text-[10px] font-mono text-muted-foreground truncate max-w-[200px] mt-1">
                                    Tx: {event.hash.substring(0, 16)}...
                                 </div>
                              </div>
                           ))}
                           {/* Simulated previous block */}
                           <div className="relative opacity-50">
                              <div className="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-muted-foreground ring-4 ring-background" />
                              <div className="text-xs font-mono text-muted-foreground">Genesis Block</div>
                           </div>
                        </div>
                     </div>
                  </CardContent>
               </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

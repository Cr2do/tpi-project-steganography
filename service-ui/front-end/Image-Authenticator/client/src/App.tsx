import { Switch, Route, Redirect } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import Layout from "@/components/Layout";
import Auth from "@/pages/Auth";
import Dashboard from "@/pages/Dashboard";
import Verify from "@/pages/Verify";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Auth} />
      <Route path="/dashboard">
        <Layout>
          <Dashboard />
        </Layout>
      </Route>
       <Route path="/verify">
        <Layout>
           <Verify />
        </Layout>
      </Route>
      {/* For mockup, redirect other nav items to dashboard or 404 */}
      <Route path="/assets">
        <Layout>
           <div className="p-8 text-center text-muted-foreground font-mono">/assets module not loaded in mockup</div>
        </Layout>
      </Route>
       <Route path="/settings">
        <Layout>
           <div className="p-8 text-center text-muted-foreground font-mono">/settings module not loaded in mockup</div>
        </Layout>
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;

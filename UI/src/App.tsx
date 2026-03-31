import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
      <img
        src="/watermark.PNG"
        alt="Watermark"
        className="fixed bottom-8 right-8 w-32 md:w-48 opacity-70 select-none pointer-events-none z-[9999] print:hidden transition-all duration-500 hover:opacity-40"
        draggable={false}
        onContextMenu={(e) => e.preventDefault()}
      />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

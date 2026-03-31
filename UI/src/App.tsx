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
        className="fixed bottom-6 right-6 w-10 h-10 md:w-16 md:h-16 object-contain opacity-50 select-none pointer-events-none z-[9999] print:hidden transition-all duration-500 hover:opacity-80"
        draggable={false}
        onContextMenu={(e) => e.preventDefault()}
      />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

import { ItineraryForm } from "@/components/ItineraryForm";
import { Plane } from "lucide-react";
import heroImage from "@/assets/hero-travel.jpg";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <header className="relative h-[300px] md:h-[400px] overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-background"></div>
        </div>
        <div className="relative h-full flex flex-col items-center justify-center px-4 text-center">
          <div className="flex items-center gap-3 mb-4">
            <Plane className="w-10 h-10 md:w-12 md:h-12 text-primary" />
            <h1 className="text-4xl md:text-6xl font-bold text-white drop-shadow-lg">
              SmartRoute
            </h1>
          </div>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl drop-shadow-md">
            Crea itinerarios personalizados basados en el clima y tus intereses
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12 max-w-4xl">
        <ItineraryForm />
      </main>

      {/* Footer */}
      <footer className="border-t mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Generador de Itinerarios con IA • Planifica tu próxima aventura</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;

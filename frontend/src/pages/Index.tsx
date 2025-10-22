import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { 
  MapPin, 
  Sun, 
  Compass,
  Hotel,
  Sparkles,
  Loader2,
  Plane,
  Mountain
} from "lucide-react";

interface TravelRecommendation {
  destination: string;
  weather: string | null;
  activities: string[];
  hotels: string[];
}

const Index = () => {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<TravelRecommendation | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    
    try {
      // Conectar al backend Python en localhost:8000
      const response = await fetch('http://localhost:8080/api/travel-recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt })
      });
      
      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error al obtener recomendaciones:', error);
      alert('Error al conectar con el backend Python. Asegúrate de que esté corriendo en http://localhost:8000');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-background">
      <header className="container mx-auto px-4 py-12 text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Plane className="w-10 h-10 text-primary" />
          <h1 className="text-6xl font-bold bg-gradient-to-r from-primary via-accent to-secondary bg-clip-text text-transparent">
            TravelAI
          </h1>
          <Mountain className="w-10 h-10 text-accent" />
        </div>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Describe tu viaje ideal y recibe recomendaciones turísticas personalizadas generadas por inteligencia artificial
        </p>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <Card className="p-8 shadow-xl bg-card/95 border-2">
          <div className="space-y-5">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-primary" />
              <label htmlFor="prompt" className="block text-sm font-semibold">
                ¿Qué tipo de experiencia buscas?
              </label>
            </div>
            <Textarea
              id="prompt"
              placeholder="Ej: test de conexión / Quiero visitar una playa paradisíaca..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[140px] text-base resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <Button
              onClick={handleSubmit}
              disabled={!prompt.trim() || isLoading}
              className="w-auto px-10 py-6 text-lg font-semibold shadow-lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generando recomendaciones...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Descubrir Destino
                </>
              )}
            </Button>
          </div>
        </Card>

        {result && (
          <div className="mt-8 space-y-6">
            <Card className="p-8 shadow-xl bg-card/95 border-2 border-primary/20">
              <div className="flex items-start gap-4 mb-4">
                <div className="p-3 rounded-full bg-primary/10">
                  <MapPin className="w-8 h-8 text-primary" />
                </div>
                <div className="flex-1">
                  <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                    Destino Recomendado
                  </h2>
                  <h3 className="text-3xl font-bold">{result.destination}</h3>
                </div>
              </div>
            </Card>

            {result.weather && (
              <Card className="p-8 shadow-xl bg-card/95 border-2 border-secondary/20">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-full bg-secondary/10">
                    <Sun className="w-8 h-8 text-secondary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-2">Clima Actual</h3>
                    <p className="text-muted-foreground leading-relaxed">{result.weather}</p>
                  </div>
                </div>
              </Card>
            )}

            <Card className="p-8 shadow-xl bg-card/95 border-2 border-accent/20">
              <div className="flex items-start gap-4 mb-4">
                <div className="p-3 rounded-full bg-accent/10">
                  <Compass className="w-8 h-8 text-accent" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">
                    {result.weather === null ? "Estado de Servicios" : "Actividades Sugeridas"}
                  </h3>
                </div>
              </div>
              <div className="grid gap-3 ml-16">
                {result.activities.map((activity, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0" />
                    <p className="leading-relaxed font-mono text-sm">{activity}</p>
                  </div>
                ))}
              </div>
            </Card>

            {result.hotels && result.hotels.length > 0 && (
              <Card className="p-8 shadow-xl bg-card/95 border-2 border-primary/20">
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 rounded-full bg-primary/10">
                    <Hotel className="w-8 h-8 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">Opciones de Alojamiento</h3>
                  </div>
                </div>
                <div className="grid gap-3 ml-16">
                  {result.hotels.map((hotel, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <p className="leading-relaxed">{hotel}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            <div className="text-center pt-4">
              <Button
                onClick={() => {
                  setResult(null);
                  setPrompt("");
                }}
                variant="outline"
                className="px-8 py-5 text-base border-2"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Buscar Otro Destino
              </Button>
            </div>
          </div>
        )}
      </main>

      <footer className="container mx-auto px-4 py-8 mt-12 text-center text-sm text-muted-foreground border-t">
        <p className="flex items-center justify-center gap-2">
          <Plane className="w-4 h-4" />
          TravelAI - Tu guía turística inteligente
          <Mountain className="w-4 h-4" />
        </p>
      </footer>
    </div>
  );
};

export default Index;
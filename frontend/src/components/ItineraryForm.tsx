import {useState} from "react";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";
import {Input} from "@/components/ui/input";
import {Textarea} from "@/components/ui/textarea";
import {Button} from "@/components/ui/button";
import {Label} from "@/components/ui/label";
import {MapPin, Calendar, Heart, Sparkles, Loader2} from "lucide-react";

export const ItineraryForm = () => {
    const [city, setCity] = useState("");
    const [dateRange, setDateRange] = useState("");
    const [interests, setInterests] = useState("");
    const [itinerary, setItinerary] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleGenerate = async () => {
        if (!city || !dateRange || !interests) {
            return;
        }

        const interestsArray = interests
            .split(",")
            .map(s => s.trim())
            .filter(Boolean);

        setIsLoading(true);

        const API_BASE = "http://api.localhost";

        const sendRes = await fetch(`${API_BASE}/sendItineraryInfo`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                city,
                time: String(dateRange),     // tu back acepta string o número; enviamos el número como string
                interests: interestsArray
            })
        });
        if (!sendRes.ok) throw new Error("Error enviando datos al backend");

        const getRes = await fetch(`${API_BASE}/getItineraryInfo`);
        if (!getRes.ok) throw new Error("Error obteniendo el itinerario");

        const data = await getRes.json();

        // Simular llamada a API (aquí se conectará con tu backend/IA)
        setTimeout(() => {
            const mockItinerary = `🌍 Itinerario para ${city}\n📅 Período: ${dateRange}\n\n
            ✨ Basado en tus intereses en ${interests}, aquí está tu itinerario personalizado:\n\n
            Día 1:\n
            - Mañana: Visita guiada por el centro histórico, explorando monumentos relacionados con ${interests}\n
            - Tarde: Tour gastronómico por los mercados locales\n
            - Noche: Cena en restaurante típico con vista panorámica\n\n
            Día 2:\n
            - Mañana: Actividad especial de ${interests}\n
            - Tarde: Tiempo libre para explorar tiendas locales\n
            - Noche: Espectáculo cultural tradicional\n\n
            Día 3:\n
            - Mañana: Excursión a los alrededores de ${city}\n
            - Tarde: Visita a museos temáticos\n
            - Noche: Paseo nocturno por las calles principales\n\n
            🌡️ Clima esperado: Soleado con temperaturas agradables\n\n
            💡 Recomendaciones adicionales:\n
            - Lleva ropa cómoda para caminar\n
            - No olvides protector solar\n
            - Reserva con anticipación los restaurantes populares`;

            const pretty = JSON.stringify(data, null, 2);
            setItinerary(pretty);
            setIsLoading(false);
        }, 2000);
    };

    return (
        <div className="space-y-8">
            <Card className="border-none shadow-[var(--shadow-card)]">
                <CardHeader className="space-y-2">
                    <CardTitle
                        className="text-2xl md:text-3xl bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                        Genera tu Itinerario Perfecto
                    </CardTitle>
                    <CardDescription className="text-base">
                        Completa los datos y crearemos un itinerario personalizado según el clima y tus intereses
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <Label htmlFor="city" className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-primary"/>
                            Ciudad de destino (Para mayor precisión, incluye prefijo de país) o Codigo postal
                        </Label>
                        <Input
                            id="city"
                            placeholder='Ej: Barcelona, 150001, Tunja,CO" ...'
                            value={city}
                            onChange={(e) => setCity(e.target.value)}
                            className="transition-all focus:shadow-[var(--shadow-elegant)]"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="dateRange" className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-primary"/>
                            Duracion
                        </Label>
                        <Input
                            id="dateRange"
                            placeholder="Ej: 3 dias"
                            value={dateRange}
                            onChange={(e) => setDateRange(e.target.value)}
                            className="transition-all focus:shadow-[var(--shadow-elegant)]"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="interests" className="flex items-center gap-2">
                            <Heart className="w-4 h-4 text-secondary"/>
                            Intereses y preferencias
                        </Label>
                        <Textarea
                            id="interests"
                            placeholder="Ej: Historia, gastronomía, museos, naturaleza, vida nocturna..."
                            value={interests}
                            onChange={(e) => setInterests(e.target.value)}
                            rows={4}
                            className="resize-none transition-all focus:shadow-[var(--shadow-elegant)]"
                        />
                    </div>

                    <Button
                        variant="hero"
                        size="lg"
                        onClick={handleGenerate}
                        disabled={!city || !dateRange || !interests || isLoading}
                        className="w-full text-base font-semibold"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin"/>
                                Generando tu itinerario...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5"/>
                                Generar Itinerario
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {itinerary && (
                <Card
                    className="border-l-4 border-l-secondary border-none shadow-[var(--shadow-card)] animate-in fade-in-50 slide-in-from-bottom-4 duration-500">
                    <CardHeader>
                        <CardTitle className="text-xl md:text-2xl flex items-center gap-2">
                            <Sparkles className="w-6 h-6 text-secondary"/>
                            Tu Itinerario Personalizado
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="whitespace-pre-line text-sm md:text-base leading-relaxed">
                            {itinerary}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

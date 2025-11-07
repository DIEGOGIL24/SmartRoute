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

        const API_BASE = "http://api.localhost";
        const controller = new AbortController();
        const timeoutMs = 600000;
        const t = setTimeout(() => controller.abort(), timeoutMs);

        setIsLoading(true);

        // Función auxiliar para leer el detalle del error del backend
        const readError = async (res: Response) => {
            let detail = `HTTP ${res.status} ${res.statusText}`;
            try {
                const ct = res.headers.get("content-type") || "";
                if (ct.includes("application/json")) {
                    const j = await res.json();
                    detail = (j?.detail || j?.message || JSON.stringify(j));
                } else {
                    const txt = await res.text();
                    if (txt) detail = txt;
                }
            } catch { /* ignorar problemas leyendo el cuerpo */
            }
            return detail;
        };

        try {
            // 2) POST
            const sendRes = await fetch(`${API_BASE}/sendItineraryInfo`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    city,
                    // OJO: si tu backend espera número, envía Number(dateRange)
                    time: String(dateRange),
                    interests: interestsArray
                }),
                signal: controller.signal
            });

            if (!sendRes.ok) {
                const detail = await readError(sendRes);
                // Ejemplo de mapeo específico útil con 422 que ya viste
                const friendly =
                    sendRes.status === 422
                        ? `Datos inválidos (422). Verifica el payload (tipos/campos). Detalle: ${detail}`
                        : `Error enviando datos al backend. Detalle: ${detail}`;
                setItinerary(`❌ ${friendly}`);
                return; // cortar flujo y dejar de cargar en finally
            }

            // 3) GET
            const getRes = await fetch(`${API_BASE}/getItineraryInfo`, {
                signal: controller.signal
            });

            if (!getRes.ok) {
                const detail = await readError(getRes);
                setItinerary(`❌ Error obteniendo el itinerario. Detalle: ${detail}`);
                return;
            }

            const data = await getRes.text();
            setItinerary(data);
        } catch (err: any) {
            // 5) Errores de red/timeout/abort
            if (err?.name === "AbortError") {
                setItinerary(`⏱️ La solicitud tardó más de ${timeoutMs / 1000}s y se canceló.`);
            } else {
                setItinerary(`🚨 Error inesperado: ${err?.message || String(err)}`);
            }
        } finally {
            // 6) Siempre deja de "cargar"
            clearTimeout(t);
            setIsLoading(false);
        }
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

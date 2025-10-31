export interface TravelRecommendation {
  destination: string;
  weather: string;
  activities: string[];
  hotels: string[];
}

export const getTravelRecommendation = (prompt: string): TravelRecommendation => {
  const lowerPrompt = prompt.toLowerCase();
  
  if (lowerPrompt.includes("playa") || lowerPrompt.includes("mar") || lowerPrompt.includes("costa")) {
    return {
      destination: "Cartagena de Indias, Colombia",
      weather: "Soleado y cálido, 28-32°C. Perfecto para disfrutar del mar Caribe.",
      activities: [
        "Explorar la Ciudad Amurallada y sus calles coloniales",
        "Snorkel en las Islas del Rosario",
        "Disfrutar de la gastronomía caribeña en Getsemaní",
        "Paseo en velero al atardecer"
      ],
      hotels: [
        "Hotel Boutique Casa del Arzobispado - Centro histórico con encanto colonial",
        "Hilton Cartagena - Resort frente al mar con spa",
        "Hotel Quadrifolio - Opción económica en el corazón de Getsemaní"
      ]
    };
  } else if (lowerPrompt.includes("montaña") || lowerPrompt.includes("naturaleza") || lowerPrompt.includes("aventura")) {
    return {
      destination: "Cusco y Machu Picchu, Perú",
      weather: "Clima templado de día (18-20°C), fresco por la noche. Temporada seca ideal para trekking.",
      activities: [
        "Visitar la majestuosa ciudadela de Machu Picchu",
        "Recorrer el Valle Sagrado de los Incas",
        "Trekking por el Camino Inca o Salkantay",
        "Explorar la Plaza de Armas y mercados artesanales de Cusco"
      ],
      hotels: [
        "Belmond Sanctuary Lodge - Único hotel junto a Machu Picchu",
        "JW Marriott El Convento Cusco - Convento del siglo XVI convertido en hotel de lujo",
        "Wild Rover Hostel - Opción backpacker con excelente ambiente"
      ]
    };
  } else if (lowerPrompt.includes("ciudad") || lowerPrompt.includes("cultura") || lowerPrompt.includes("arte")) {
    return {
      destination: "Barcelona, España",
      weather: "Clima mediterráneo agradable, 20-25°C. Ideal para caminar por la ciudad.",
      activities: [
        "Visitar la Sagrada Familia y obras de Gaudí",
        "Pasear por Las Ramblas y el Barrio Gótico",
        "Disfrutar tapas en el Mercado de La Boquería",
        "Relajarse en las playas de la Barceloneta"
      ],
      hotels: [
        "Hotel Arts Barcelona - Lujo frente al mar con vistas espectaculares",
        "Cotton House Hotel - Boutique hotel en edificio histórico",
        "Generator Barcelona - Hostel moderno y estiloso"
      ]
    };
  }
  
  return {
    destination: "Lisboa, Portugal",
    weather: "Clima suave y soleado, 22-26°C. Perfecto para explorar la ciudad a pie.",
    activities: [
      "Recorrer el barrio de Alfama en tranvía amarillo",
      "Degustar pasteles de Belém originales",
      "Mirador de São Jorge con vistas panorámicas",
      "Vida nocturna en Bairro Alto con música fado en vivo"
    ],
    hotels: [
      "Memmo Alfama Hotel - Boutique con terraza panorámica",
      "Pestana Palace Lisboa - Palacio del siglo XIX convertido en hotel",
      "The Independente Hostel & Suites - Diseño moderno con excelente ubicación"
    ]
  };
};

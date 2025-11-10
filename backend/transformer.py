# --- Config del modelo (MODELOS CON MÁS TOKENS) ---
# IMPORTANTE: Usa AutoModelForCausalLM (NO Seq2SeqLM)
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate  # ✅ CORRECTO
from langchain_core.output_parsers import StrOutputParser
import json
import sys
from pathlib import Path

# model_name = "meta-llama/Llama-3.2-3B-Instruct"
# max_length = 127000

# model_name = "Qwen/Qwen2.5-1.5B-Instruct"
# max_length = 32768

# model_name = "Qwen/Qwen2.5-3B-Instruct"
# max_length = 32768

model_name = "Qwen/Qwen3-4B-Instruct-2507"
max_length = 32768

# Cargar tokenizer explícitamente
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Pipeline con configuración mejorada
pipe = pipeline(
    "text-generation",
    model=model_name,
    tokenizer=tokenizer,
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True,  # Importante para modelos Qwen
    model_kwargs={
        "low_cpu_mem_usage": True,
        "use_cache": True  # Acelera generación
    }
)

# Parámetros de generación optimizados
generation_params = {
    "max_new_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.1,
    "do_sample": True,
    "num_return_sequences": 1,
    "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
    "eos_token_id": tokenizer.eos_token_id,
    "return_full_text": False  # CRÍTICO: Solo devuelve texto generado
}

# HuggingFacePipeline con parámetros
llm = HuggingFacePipeline(
    pipeline=pipe,
    model_kwargs=generation_params
)

# Prompt mejorado (más conciso y directo)
prompt = PromptTemplate.from_template(
    """Eres un asistente de viajes. Analiza el siguiente JSON con datos de clima y lugares turísticos, y genera un itinerario turístico detallado en español.

<JSON>
{json_blob}
</JSON>

Genera el itinerario usando este formato:

🌍 Itinerario para [CIUDAD]
📅 Período: [Primera fecha - Última fecha]

Día 1 ([fecha]):
- Mañana: [Actividad específica en lugar turístico] - Clima: [temperatura y condición]
- Tarde: [Actividad específica en lugar turístico] - Clima: [temperatura y condición]
- Noche: [Actividad específica en lugar turístico] - Clima: [temperatura y condición]

[Repite para cada día]

🌡️ Resumen del clima: [Descripción general de las condiciones]

💡 Recomendaciones:
- [Consejo práctico 1]
- [Consejo práctico 2]
- [Consejo práctico 3]

Responde ÚNICAMENTE con el itinerario, sin preámbulos."""
)

# Chain
chain = prompt | llm | StrOutputParser()


def check_token_length(text):
    """
    Verifica la longitud del texto en tokens.
    """
    tokens = tokenizer.encode(text, truncation=False)
    token_count = len(tokens)
    print(f"📊 Longitud del JSON: {token_count} tokens (máximo: {max_length})")

    if token_count > max_length - 600:  # Dejar espacio para la respuesta
        print(f"⚠️  ADVERTENCIA: El JSON es muy largo ({token_count} tokens)")
        print(f"   Se recomienda resumirlo o usar un modelo con más capacidad")
        return False

    return True


def process_json_file(json_path):
    """
    Lee un archivo JSON y lo convierte en texto conversacional.

    Args:
        json_path: Ruta al archivo JSON

    Returns:
        Texto generado por el modelo
    """
    # Leer archivo JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_blob = json.dumps(data, indent=2, ensure_ascii=False)

    print(f"\n📄 Procesando archivo: {json_path}")
    print(f"\n📝 JSON de entrada (primeros 500 caracteres):")
    print(json_blob[:500] + "...\n")

    # Verificar longitud
    if not check_token_length(json_blob):
        respuesta = input("\n❓ ¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Proceso cancelado")
            return None

    print("🤖 Generando texto conversacional...\n")

    try:
        result = chain.invoke({"json_blob": json_blob})

        # Limpiar la respuesta - extraer solo la parte del asistente
        if "<|im_start|>assistant" in result:
            result = result.split("<|im_start|>assistant")[-1].strip()
        if "<|im_end|>" in result:
            result = result.split("<|im_end|>")[0].strip()
        if "Texto conversacional:" in result:
            result = result.split("Texto conversacional:")[-1].strip()

        return result

    except Exception as e:
        print(f"❌ Error al generar texto: {e}")
        return None


def main(json_path: str):
    """
    Función principal para probar el generador con un archivo JSON.
    Uso: python script.py <archivo.json>
    """

    try:
        # Procesar el archivo
        resultado = process_json_file(json_path)

        if resultado is None:
            sys.exit(1)

        # Mostrar resultado
        print("✅ Resultado:\n")
        print("=" * 60)
        print(resultado)
        print("=" * 60)

        # Guardar resultado en archivo de texto
        output_path = json_path.replace('.json', '_resultado.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(resultado)

        print(f"\n💾 Resultado guardado en: {output_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main("out.json")
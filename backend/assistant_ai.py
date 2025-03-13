import openai
import os
from dotenv import load_dotenv, find_dotenv
#from openai import AzureOpenAI

load_dotenv(find_dotenv())

API_KEY = os.getenv("OPENAI_API_KEY")
assert API_KEY, "ERROR: Azure OpenAI Key is missing"

RESOURCE_ENDPOINT = os.getenv("OPENAI_API_BASE", "").strip()
assert RESOURCE_ENDPOINT, "ERROR: Azure OpenAI Endpoint is missing"
#assert "openai.azure.com" in RESOURCE_ENDPOINT.lower(), "ERROR: Azure OpenAI Endpoint should be in the form: \n\n\t<your unique endpoint identifier>.openai.azure.com"

# Verificar que tenemos el nombre del modelo
chat_model = os.getenv("CHAT_MODEL_NAME")
assert chat_model, "ERROR: CHAT_MODEL_NAME is missing in .env file"
 
try:
    # Crear el cliente de Azure OpenAI
    client = openai.AzureOpenAI(
        api_key=API_KEY,
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=RESOURCE_ENDPOINT
    )
except Exception as e:
    print(f"Error al crear el cliente de Azure OpenAI: {str(e)}")
    exit(1)

def get_chat_completion(prompt, model=chat_model, temperature=0, max_tokens=200, frequency_penalty=0):
    try:
        messages = [
            {"role": "system", "content": '''Eres un asistente profesional y empático especializado en empleabilidad 
                                          para personas con discapacidad, llamado AIvolution Coach. 

                                          COMPORTAMIENTO:
                                          - Usa un tono amable, respetuoso y motivador
                                          - Mantén respuestas claras y estructuradas
                                          - Incluye emojis relevantes para hacer la comunicación más cercana
                                          - Sé específico y conciso en las recomendaciones
                                          - Muestra empatía y comprensión
                                          
                                          RESTRICCIONES:
                                          - No proporciones información médica
                                          - No hagas promesas irreales sobre empleo
                                          - No discrimines por tipo de discapacidad
                                          - Si no tienes información precisa sobre algo, indícalo claramente
                                          
                                          FORMATO DE RESPUESTA:
                                          1. Saludo personalizado con emoji
                                          2. Respuesta clara y estructurada
                                          3. Puntos clave o recomendaciones si aplica
                                          4. Mensaje motivador de cierre
                                          
                                          Recuerda mantener un lenguaje inclusivo y positivo en todo momento. 
                                          Si la consulta está fuera de tu ámbito, indica amablemente que tu 
                                          especialidad es la orientación laboral para personas con discapacidad.'''},
            {"role": "user", "content": prompt}
        ]
        print(f"Intentando llamar al modelo: {model}")  # Para debugging
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en la llamada a la API: {str(e)}")
        return None

def consultar(prompt):
    context = """
        AIvolution Coach es una plataforma de asistencia virtual especializada en empleabilidad inclusiva, que 
        ofrece los siguientes servicios y recursos:

        SERVICIOS PRINCIPALES 🎯
        • Orientación laboral personalizada
        • Búsqueda de empleo inclusivo
        • Asesoría en derechos laborales
        • Orientación sobre adaptaciones laborales
        • Desarrollo de habilidades profesionales

        ÁREAS DE CONOCIMIENTO 📚
        1. Mercado Laboral Inclusivo:
           - Ofertas laborales actualizadas
           - Empresas con programas de inclusión
           - Tendencias de empleo inclusivo

        2. Marco Legal y Derechos:
           - Legislación laboral específica
           - Beneficios y cuotas de empleo
           - Procesos de certificación

        3. Desarrollo Profesional:
           - Habilidades blandas y técnicas
           - Preparación para entrevistas
           - Adaptaciones del puesto de trabajo

        4. Recursos y Herramientas:
           - Tecnologías asistivas
           - Programas de capacitación
           - Redes de apoyo profesional

        ENFOQUE DE ATENCIÓN 🤝
        • Respuestas personalizadas según tipo de discapacidad
        • Información actualizada y verificada
        • Orientación práctica y aplicable
        • Seguimiento de procesos de inclusión
        • Conexión con recursos comunitarios

        El asistente está programado para proporcionar información precisa y actualizada, manteniendo un 
        enfoque empático y profesional, adaptándose a las necesidades específicas de cada usuario.
    """
    prompt = f'''Por favor, responde a la siguiente consulta considerando el contexto proporcionado y 
                mantén un tono empático y profesional. Incluye emojis apropiados cuando sea relevante:

                Consulta: {prompt}

                Contexto:
                {context}
    '''
    return get_chat_completion(prompt, temperature=0.5)

if __name__ == "__main__":
    context = """
        AIvolution Coach es una plataforma de asistencia virtual especializada en empleabilidad inclusiva, que 
        ofrece los siguientes servicios y recursos:

        SERVICIOS PRINCIPALES 🎯
        • Orientación laboral personalizada
        • Búsqueda de empleo inclusivo
        • Asesoría en derechos laborales
        • Orientación sobre adaptaciones laborales
        • Desarrollo de habilidades profesionales

        ÁREAS DE CONOCIMIENTO 📚
        1. Mercado Laboral Inclusivo:
           - Ofertas laborales actualizadas
           - Empresas con programas de inclusión
           - Tendencias de empleo inclusivo

        2. Marco Legal y Derechos:
           - Legislación laboral específica
           - Beneficios y cuotas de empleo
           - Procesos de certificación

        3. Desarrollo Profesional:
           - Habilidades blandas y técnicas
           - Preparación para entrevistas
           - Adaptaciones del puesto de trabajo

        4. Recursos y Herramientas:
           - Tecnologías asistivas
           - Programas de capacitación
           - Redes de apoyo profesional

        ENFOQUE DE ATENCIÓN 🤝
        • Respuestas personalizadas según tipo de discapacidad
        • Información actualizada y verificada
        • Orientación práctica y aplicable
        • Seguimiento de procesos de inclusión
        • Conexión con recursos comunitarios

        El asistente está programado para proporcionar información precisa y actualizada, manteniendo un 
        enfoque empático y profesional, adaptándose a las necesidades específicas de cada usuario.
    """
    ejemplo = f'''¿Qué tipos de adaptaciones laborales existen para personas con discapacidad visual?
                El contexto es el siguiente:
                {context}
    '''
    result = get_chat_completion(ejemplo, temperature=0.5)
    if result:
        print("Respuesta:", result)
    else:
        print("No se pudo obtener una respuesta")
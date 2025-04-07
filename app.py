from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Token de acceso de Zoko - deberías configurar esto como variable de entorno en Railway
ZOKO_API_TOKEN = os.environ.get('ZOKO_API_TOKEN')
# URL de la API de Zoko para enviar mensajes
ZOKO_API_URL = "https://api.zoko.io/v2/messages"

# Almacena el progreso por número de teléfono
user_states = {}


# Preguntas del test
questions = [
    "¡Hola! 👋 ¿Lista para un escáner rápido a tu corazón? 😉\n\n¿Te has preguntado por qué a veces conectas más con alguien que no es el 'bueno' del cuento? 🤔\n¿O por qué te sientes atraída hacia cierto tipo de persona una y otra vez, aunque la relación acabe doliendo? 🤷‍♀️\n\nEste test usa psicología femenina ✨ para revelar qué busca tu subconsciente, a qué tipo de persona eres más vulnerable, cuáles son tus 'poderes' secretos en el amor y por qué repites patrones.\n\nResponde solo con la letra (A, B, C, D o E) que más te represente. ¡Empezamos! 🚀",

    "1/11: Sin pareja, ¿qué echas más de menos?\nA) Emoción/chispa del principio 🔥\nB) Conexión profunda/compartir 💖\nC) Tranquilidad/estabilidad 🏡\nD) Compañía/cariño constante 🤗\nE) Nada en especial, disfruto mi espacio 🕊️\n💡 Lo que extrañas revela qué valoras.",

    "2/11: Aparte del físico, ¿qué te atrae más?\nA) Atrevimiento/aventura 🔥\nB) Cariño/romanticismo 💖\nC) Madurez/confianza 📊\nD) Atención/sentirte especial 🤗\nE) Independencia/espacio 🕊️\n👀 Lo que te atrae destapa patrones.",

    "3/11: Al empezar a conocer a alguien, ¿qué te nace?\nA) Hacer planes activos ¡ya! 🔥\nB) Conversaciones largas/profundas 💖\nC) Ir poco a poco/observar 📊\nD) Contacto frecuente (mensajes) 🤗\nE) Disfrutar el momento sin presiones 🕊️\n🚀 Tus primeros pasos = tu ritmo.",

    "4/11: Tu futuro ideal en pareja, ¿cómo sería?\nA) Dinámico/con libertad 🔥\nB) Muy unido/romántico 💖\nC) Estable/organizado 📊\nD) Mucho apoyo/sentirte querida 🤗\nE) Con espacio individual/apoyo mutuo 🕊️\n🔮 Tu visión guía tus decisiones hoy.",

    "5/11: Plan ideal con tu pareja AHORA:\nA) Improvisado/romper rutina 🔥\nB) Tranquilo en casa/cercanos 💖\nC) Organizar algo práctico/futuro 📊\nD) Expresar afecto (palabras/mimos) 🤗\nE) Juntos pero cada uno a lo suyo 🕊️\n🗣️ Pista sobre tu 'lenguaje del amor'.",

    "6/11: En un desacuerdo, ¿tu reacción habitual?\nA) Intensidad o necesito aire 🔥\nB) Hablarlo rápido/sentirnos bien 💖\nC) Analizar objetivamente 📊\nD) Necesito cercanía/reafirmación 🤗\nE) Necesito tiempo/espacio a solas 🕊️\n🛡️ Revela qué necesitas para sentirte segura.",

    "7/11: Tu forma principal de DEMOSTRAR amor:\nA) Sorpresas/acción 🔥\nB) Palabras/romanticismo 💖\nC) Ayuda práctica/ser fiable 📊\nD) Presencia/cariño físico 🤗\nE) Apoyar su independencia 🕊️\n🎁 ¿Das amor como te gusta recibirlo?",

    "8/11: Tu pareja está mal. ¿Cómo ayudas?\nA) Distraerle/animarle con planes 🔥\nB) Escucharle/apoyo emocional 💖\nC) Analizar/buscar soluciones 📊\nD) Estar muy cerca/consuelo físico 🤗\nE) Darle ánimos/ofrecer ayuda sin agobiar 🕊️\n🤝 Cómo cuidas dice mucho.",

    "9/11: Relación pasada intensa que no funcionó. ¿Qué 'vibe' tenía esa persona?\nA) Emocionante pero inestable 🔥\nB) Alma gemela pero irreal 💖\nC) Seguro pero frío/controlador 📊\nD) Atento pero absorbente 🤗\nE) Genial pero distante/evasivo 🕊️\n🤔 A veces nos atrae lo que nos desequilibra...",

    "10/11: Tu 'superpoder' principal en el amor según tus amigas:\nA) Tu energía y diversión 🔥\nB) Tu entrega y romanticismo 💖\nC) Tu sensatez y estabilidad 📊\nD) Tu apoyo y presencia 🤗\nE) Tu independencia y fuerza 🕊️\n💪 Conocer tus puntos fuertes te empodera.",

    "11/11: ¿Qué te hace dudar MÁS de alguien al principio? (Tu 'red flag')\nA) Demasiado lento/predecible 🔥\nB) Cínico/poco romántico 💖\nC) Impulsivo/caótico 📊\nD) Distante/desinteresado 🤗\nE) Muy intenso/pegajoso 🕊️\n🚨 Escuchar esa vocecita interna es clave."
]

def send_zoko_message(phone_number, message_text):
    """Envía un mensaje a través de la API de Zoko"""
    headers = {
        "Authorization": f"Bearer {ZOKO_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "recipient": phone_number,
        "type": "text",
        "message": {
            "text": message_text
        }
    }
    
    try:
        response = requests.post(ZOKO_API_URL, json=payload, headers=headers)
        print(f"Respuesta de Zoko: {response.status_code} - {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error al enviar mensaje a Zoko: {e}")
        return False

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("✅ Recibido mensaje en webhook:", data)

    # Extrae el número de teléfono del remitente
    sender = data.get("platformSenderId", "")
    message_text = data.get("text", "").strip().upper()

    if not sender:
        return jsonify({"status": "error", "message": "Falta el número del remitente"}), 400

    # Inicializa el progreso si es la primera vez
    if sender not in user_states:
        user_states[sender] = {
            "current_question": 0,
            "answers": []
        }

    state = user_states[sender]
    q_index = state["current_question"]

    # Guarda la respuesta anterior si no es la primera pregunta
    if q_index > 0 and message_text in ["A", "B", "C", "D", "E"]:
        state["answers"].append(message_text)
        q_index += 1
        state["current_question"] = q_index
    elif q_index > 0:
        # Si no responde con A-E, no avanza y reenvía la misma pregunta
        send_zoko_message(sender, "Responde solo con A, B, C, D o E 😊")
        return jsonify({"status": "success"}), 200

    # Final del test
    if q_index >= len(questions):
        final_msg = "🎉 ¡Gracias por completar el test! Pronto recibirás tu resultado ❤️"
        # Puedes procesar las respuestas si deseas
        del user_states[sender]  # Opcional: reiniciar conversación
        send_zoko_message(sender, final_msg)
    else:
        # Enviar la siguiente pregunta
        next_question = questions[q_index]
        send_zoko_message(sender, next_question)

    # Siempre responde con éxito al webhook
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
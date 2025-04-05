from flask import Flask, request, jsonify

app = Flask(__name__)

# Simula una base de datos temporal en memoria
user_states = {}

# Lista de mensajes (introducción + 11 preguntas)
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

final_message = "✨ ¡Gracias! En un momento te enviaremos los resultados. ✨"

@app.route("/zoko-webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("messages", [{}])[0]
    from_number = message.get("from", "")
    text = message.get("text", {}).get("body", "").strip().upper()

    # Iniciar test si es nuevo
    if from_number not in user_states:
        user_states[from_number] = {
            "step": 0,
            "answers": []
        }
        return jsonify({"reply": questions[0]})  # Mensaje de introducción

    state = user_states[from_number]

    # Validar respuesta previa (si aplica)
    if state["step"] > 0:
        if text not in ["A", "B", "C", "D", "E"]:
            return jsonify({"reply": "✋ Responde solo con una letra: A, B, C, D o E."})
        state["answers"].append(text)

    # Avanzar a siguiente pregunta
    state["step"] += 1

    if state["step"] < len(questions):
        next_question = questions[state["step"]]
        return jsonify({"reply": next_question})
    else:
        # Fin del test
        del user_states[from_number]
        return jsonify({"reply": final_message})

if __name__ == "__main__":
    app.run(port=5000)

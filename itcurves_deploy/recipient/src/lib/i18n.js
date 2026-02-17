const translations = {
  en: {
    welcome: "Welcome to the",
    customerSurvey: "Customer Satisfaction Survey",
    hello: "Hello",
    chooseMode: "Please choose how you'd like to complete the survey:",
    voiceSurvey: "Voice Survey",
    voiceDesc: "Speak your answers using your microphone",
    textSurvey: "Text Survey",
    textDesc: "Type your answers in a form",
    tapToSpeak: "Tap microphone to speak",
    listening: "Listening... Tap to stop",
    processing: "Processing your response...",
    thinking: "Thinking...",
    pleaseWait: "Please wait...",
    sorryNotUnderstood: "Sorry, I couldn't understand that. Please try speaking again.",
    thankYou: "Thank you for completing the survey!",
    yourResponsesSaved: "Your responses have been saved.",
    surveyComplete: "Survey completed successfully! Redirecting...",
    progress: "Progress",
    questions: "Questions",
    question: "Question",
    submit: "Submit",
    next: "Next",
    previous: "Previous",
    errorLoading: "Failed to load survey",
    errorStatus: "Failed to load survey status",
    completedAlready: "It looks like you have already answered all the questions.",
  },
  es: {
    welcome: "Bienvenido a la",
    customerSurvey: "Encuesta de Satisfacción del Cliente",
    hello: "Hola",
    chooseMode: "Por favor elija cómo le gustaría completar la encuesta:",
    voiceSurvey: "Encuesta por Voz",
    voiceDesc: "Hable sus respuestas usando su micrófono",
    textSurvey: "Encuesta de Texto",
    textDesc: "Escriba sus respuestas en un formulario",
    tapToSpeak: "Toque el micrófono para hablar",
    listening: "Escuchando... Toque para detener",
    processing: "Procesando su respuesta...",
    thinking: "Pensando...",
    pleaseWait: "Por favor espere...",
    sorryNotUnderstood: "Lo siento, no pude entender eso. Por favor intente hablar de nuevo.",
    thankYou: "¡Gracias por completar la encuesta!",
    yourResponsesSaved: "Sus respuestas han sido guardadas.",
    surveyComplete: "¡Encuesta completada con éxito! Redirigiendo...",
    progress: "Progreso",
    questions: "Preguntas",
    question: "Pregunta",
    submit: "Enviar",
    next: "Siguiente",
    previous: "Anterior",
    errorLoading: "Error al cargar la encuesta",
    errorStatus: "Error al cargar el estado de la encuesta",
    completedAlready: "Parece que ya ha respondido todas las preguntas.",
  },
};

export function detectLanguage(templateName) {
  if (!templateName) return "en";
  const lower = templateName.toLowerCase();
  if (lower.includes("spanish") || lower.includes("_es") || lower.includes("español")) {
    return "es";
  }
  return "en";
}

export function t(key, lang = "en") {
  return translations[lang]?.[key] || translations.en[key] || key;
}

export default translations;

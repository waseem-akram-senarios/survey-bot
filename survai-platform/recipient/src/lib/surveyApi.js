const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function getSurveyQuestions(surveyId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/surveys/${surveyId}/questions`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (!response.ok) {
      throw new Error(
        `Failed to fetch survey questions: ${response.status} ${response.statusText}`
      );
    }
    const data = await response.json();
    
    const questionsWithAnswers = data.Questions.map((question) => ({
      ...question,
      answer: question.answer || "", 
      raw_answer: question.raw_answer || "",
    })).sort((a, b) => parseInt(a.order) - parseInt(b.order));
    
    return {
      SurveyId: data.SurveyId,
      TemplateName: data.TemplateName,
      Questions: questionsWithAnswers,
    };
  } catch (error) {
    console.error("Error fetching survey questions:", error);
    throw error;
  }
}

export async function submitSurveyAnswers(surveyId, questions) {
  try {
    const questionsWithAnswers = questions.map((question) => ({
      QueId: question.id,
      QueText: question.text,
      QueScale: question.scales || 0,
      QueCriteria: question.criteria,
      QueCategories: question.categories || [],
      ParentId: question.parent_id || "",
      ParentCategoryTexts: question.parent_category_texts || [],
      Order: question.order || 0,
      Ans: question.answer || "", 
      RawAns: question.raw_answer || "",
      Autofill: question.autofill || "No" 
    }));
    
    console.log("Submitting survey answers with transformed data:", questionsWithAnswers);
    
    const response = await fetch(`${API_BASE_URL}/api/answers/qna`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        SurveyId: surveyId,
        QuestionswithAns: questionsWithAnswers,
      }),
    });
    
    if (!response.ok) {
      throw new Error(
        `Failed to submit survey: ${response.status} ${response.statusText}`
      );
    }
    
    const result = await response.json();
    console.log("Survey submission successful:", result);
    return result;
  } catch (error) {
    console.error("Error submitting survey:", error);
    throw error;
  }
}

export async function updateSurveyStatus(surveyId, status) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/surveys/${surveyId}/status`,
      {
        method: 'PATCH',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Status: status
        })
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to update survey status: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error updating survey status:", error);
    throw error;
  }
}

export async function updateSurveyDuration(surveyId, duration) {
  try {
    console.log("Updating survey duration:", surveyId, duration);
    const response = await fetch(
      `${API_BASE_URL}/api/surveys/${surveyId}/duration`,
      {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          CompletionDuration: duration
        })
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to update survey duration: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error updating survey duration:", error);
    throw error;
  }
}

export function validateAnswer(question, answer) {
  // If question is autofilled with an answer, it's always valid
  if (question.autofill === "Yes" && question.answer && question.answer.trim() !== "") {
    return true;
  }
  
  if (!answer || (typeof answer === 'string' && answer.trim() === "")) {
    return false;
  }
  
  // For different question types, validate accordingly
  switch (question.criteria) {
    case "categorical":
      // For categorical questions, answer should be one of the categories
      return question.categories && question.categories.includes(answer);
    case "scale":
      // For scale questions, answer should be a valid number within the scale
      const numAnswer = parseInt(answer);
      const maxScale = parseInt(question.scales);
      return !isNaN(numAnswer) && numAnswer >= 1 && numAnswer <= maxScale;
    case "open":
    case "text":
      // For open text questions, just check if it's not empty
      return typeof answer === 'string' && answer.trim().length > 0;
    default:
      // Generic validation - just check if answer exists and is not empty
      return answer && (typeof answer !== 'string' || answer.trim().length > 0);
  }
}

export function getQuestionOptions(question) {
  switch (question.criteria) {
    case "scale":
      // Generate scale options (1, 2, 3, ...)
      const scale = parseInt(question.scales);
      return Array.from({ length: scale }, (_, i) => (i + 1).toString());
    case "categorical":
      return question.categories || [];
    default:
      return [];
  }
}

export function hasQuestionOptions(question) {
  return (
    question.criteria === "scale" ||
    (question.criteria === "categorical" &&
      question.categories &&
      question.categories.length > 0)
  );
}

export async function getSympathizeResponse(question, userResponse) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/questions/sympathize`,
      {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Question: question,
          Response: userResponse
        })
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.response || data.message || "Thank you for your response.";
  } catch (error) {
    console.error('Error getting sympathize response:', error);
    return "Thank you for your response."; // Fallback message
  }
}

export async function transcribeAudio(blob, contentType, language = "en") {
  try {
    const ct = contentType || blob.type || "audio/webm";
    const url = new URL("/api/transcribe", window.location.origin);
    url.searchParams.set("language", language);
    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Content-Type": ct,
      },
      body: blob,
    });

    const data = await response.json();
    if (data.error) {
      throw new Error(data.error);
    }
    const transcript =
      data?.results?.channels?.[0]?.alternatives?.[0]?.transcript || "";

    if (!transcript.trim()) {
      throw new Error("No transcription returned.");
    }

    return transcript;
  } catch (error) {
    console.error("Transcription error:", error);
    throw error;
  }
}
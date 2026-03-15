import ApiBaseHelper from "../../network/apiBaseHelper";
import ApiLinks from "../../network/apiLinks";

class QuestionService {
  static async createQuestion(questionData) {
    try {
      const response = await ApiBaseHelper.post(
        ApiLinks.QUESTION_CREATE,
        questionData
      );
      return response;
    } catch (error) {
      console.error("Error creating question:", error);
      const detail = error.response?.data?.detail;
      const msg = typeof detail === "string" ? detail : Array.isArray(detail) ? detail[0]?.msg || detail[0] : null;
      if (error.response?.status === 400) {
        throw new Error(msg || "Question already exists or invalid data.");
      }
      if (error.code === "ERR_NETWORK" || error.message?.includes("Network")) {
        throw new Error("Cannot reach the server. Start the backend (e.g. gateway on port 8080) and try again.");
      }
      throw new Error(msg || error.message || "Failed to create question. Please try again.");
    }
  }

  static async updateQuestion(questionData) {
    try {
      const response = await ApiBaseHelper.patch(
        ApiLinks.QUESTION_EDIT,
        questionData
      );
      return response;
    } catch (error) {
      console.error("Error updating question:", error);
      throw new Error("Failed to update question. Please try again.");
    }
  }

  static async getQuestionDetails(questionId) {
    try {
        console.log("Fetching details for question ID:", questionId);
      const response = await ApiBaseHelper.get(
        ApiLinks.QUESTION_DETAILS(questionId)
      );
      console.log("Fetched question details:", response);
      return response;
    } catch (error) {
      console.error("Error fetching question details:", error);
      throw new Error("Failed to fetch question details. Please try again.");
    }
  }

  static async deleteQuestion(questionId) {
    try {
      const response = await ApiBaseHelper.delete(
        ApiLinks.QUESTION_DETAILS(questionId)
      );
      return response;
    } catch (error) {
      console.error("Error deleting question:", error);
      throw new Error("Failed to delete question. Please try again.");
    }
  }
}

export default QuestionService;

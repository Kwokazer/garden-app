// frontend/src/features/questions/store/questionsStore.js

import { defineStore } from "pinia";
import { ref, computed, nextTick } from "vue";
import { questionsApi, answersApi } from "../api/questionsApi";
// Добавляем импорт authStore
import { useAuthStore } from "../../auth/store/authStore";

/**
 * Хранилище для управления состоянием вопросов и ответов
 */
export const useQuestionsStore = defineStore("questions", () => {
  // Добавляем инициализацию authStore
  const authStore = useAuthStore();

  // State (состояние)
  const questions = ref([]);
  const currentQuestion = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    total_pages: 1,
    total: 0,
    size: 20,
    pages: 1,
  });
  const activeFilters = ref({
    search: "",
    plant_id: null,
    author_id: null,
    is_solved: null,
    sort_by: "created_at",
    sort_order: "desc",
  });

  // Getters (вычисляемые свойства)
  const getQuestions = computed(() => questions.value);
  const getCurrentQuestion = computed(() => currentQuestion.value);
  const getIsLoading = computed(() => isLoading.value);
  const getError = computed(() => error.value);
  const getPagination = computed(() => pagination.value);
  const getActiveFilters = computed(() => activeFilters.value);

  /**
   * Загрузить список вопросов с фильтрацией и пагинацией
   */
  async function loadQuestions(page = 1, per_page = 20, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        search: "",
        plant_id: null,
        author_id: null,
        is_solved: null,
        sort_by: "created_at",
        sort_order: "desc",
      };
    }

    try {
      const response = await questionsApi.getQuestions(
        page,
        per_page,
        activeFilters.value
      );

      console.log("Store: Received response from API:", response);
      console.log("Store: Items count:", response.items?.length || 0);

      questions.value = response.items || [];

      pagination.value = {
        page: response.page || page,
        total_pages: response.pages || 1,
        total: response.total || 0,
        size: response.size || per_page,
        pages: response.pages || 1,
      };

      return questions.value;
    } catch (e) {
      error.value = e.message || "Ошибка при загрузке списка вопросов";
      console.error("Error loading questions list:", e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загрузить вопросы по конкретному растению
   */
  async function loadQuestionsByPlant(
    plantId,
    page = 1,
    per_page = 10,
    filters = {}
  ) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await questionsApi.getQuestionsByPlant(
        plantId,
        page,
        per_page,
        filters
      );

      const plantQuestions = response.items || [];

      pagination.value = {
        page: response.page || page,
        total_pages: response.pages || 1,
        total: response.total || 0,
        size: response.size || per_page,
        pages: response.pages || 1,
      };

      return plantQuestions;
    } catch (e) {
      error.value =
        e.message || `Ошибка при загрузке вопросов для растения ${plantId}`;
      console.error(`Error loading questions for plant ${plantId}:`, e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загрузить детальную информацию о вопросе
   */
  async function loadQuestionById(questionId) {
    if (!questionId) {
      error.value = "ID вопроса не указан";
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const question = await questionsApi.getQuestionById(questionId);
      currentQuestion.value = question;
      return question;
    } catch (e) {
      error.value = e.message || `Ошибка при загрузке вопроса ${questionId}`;
      console.error(`Error loading question ${questionId}:`, e);
      currentQuestion.value = null;
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Создать новый вопрос
   */
  async function createQuestion(questionData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newQuestion = await questionsApi.createQuestion(questionData);
      questions.value.unshift(newQuestion);
      return newQuestion;
    } catch (e) {
      error.value = e.message || "Ошибка при создании вопроса";
      console.error("Error creating question:", e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Обновить вопрос
   */
  async function updateQuestion(questionId, questionData) {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedQuestion = await questionsApi.updateQuestion(
        questionId,
        questionData
      );

      if (currentQuestion.value && currentQuestion.value.id === questionId) {
        currentQuestion.value = updatedQuestion;
      }

      const index = questions.value.findIndex((q) => q.id === questionId);
      if (index !== -1) {
        questions.value[index] = updatedQuestion;
      }

      return updatedQuestion;
    } catch (e) {
      error.value = e.message || `Ошибка при обновлении вопроса ${questionId}`;
      console.error(`Error updating question ${questionId}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Удалить вопрос
   */
  async function deleteQuestion(questionId) {
    isLoading.value = true;
    error.value = null;

    try {
      await questionsApi.deleteQuestion(questionId);
      questions.value = questions.value.filter((q) => q.id !== questionId);

      if (currentQuestion.value && currentQuestion.value.id === questionId) {
        currentQuestion.value = null;
      }

      return true;
    } catch (e) {
      error.value = e.message || `Ошибка при удалении вопроса ${questionId}`;
      console.error(`Error deleting question ${questionId}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Проголосовать за вопрос с принудительным обновлением реактивности
   */
  async function voteForQuestion(questionId, voteType) {
    console.log(
      `🗳️ Store: Starting vote for question ${questionId} with type ${voteType}`
    );

    try {
      // Проверяем, не является ли пользователь автором вопроса
      const questionToVote =
        questions.value.find((q) => q.id === questionId) ||
        (currentQuestion.value?.id === questionId
          ? currentQuestion.value
          : null);

      if (
        questionToVote &&
        authStore.isLoggedIn &&
        authStore.user &&
        authStore.user.id === questionToVote.author_id
      ) {
        console.error("❌ Store: Cannot vote for own question");
        throw new Error("Вы не можете голосовать за свой собственный вопрос");
      }

      // Сохраняем состояние до голосования
      const questionBefore = questions.value.find((q) => q.id === questionId);
      const currentBefore =
        currentQuestion.value?.id === questionId
          ? { ...currentQuestion.value }
          : null;

      console.log("📊 Store: Before vote - Question state:", {
        inList: questionBefore
          ? {
              votes_up: questionBefore.votes_up,
              votes_down: questionBefore.votes_down,
              user_vote: questionBefore.user_vote,
            }
          : "not found",
        current: currentBefore
          ? {
              votes_up: currentBefore.votes_up,
              votes_down: currentBefore.votes_down,
              user_vote: currentBefore.user_vote,
            }
          : "not current",
      });

      // Вызов API
      const updatedQuestion = await questionsApi.voteForQuestion(
        questionId,
        voteType
      );
      console.log("✅ Store: API returned:", {
        id: updatedQuestion.id,
        votes_up: updatedQuestion.votes_up,
        votes_down: updatedQuestion.votes_down,
        user_vote: updatedQuestion.user_vote,
      });

      // 1. Обновляем currentQuestion если это текущий вопрос
      if (currentQuestion.value?.id === questionId) {
        console.log("🔄 Store: Updating currentQuestion");
        currentQuestion.value = {
          ...currentQuestion.value,
          votes_up: updatedQuestion.votes_up,
          votes_down: updatedQuestion.votes_down,
          user_vote: updatedQuestion.user_vote,
          // Добавляем другие поля из ответа API
          ...Object.fromEntries(
            Object.entries(updatedQuestion).filter(
              ([key, value]) =>
                value !== undefined && !["answers"].includes(key)
            )
          ),
        };
      }

      // 2. Обновляем в массиве questions с ПОЛНЫМ ПЕРЕСОЗДАНИЕМ МАССИВА
      const questionIndex = questions.value.findIndex(
        (q) => q.id === questionId
      );
      if (questionIndex !== -1) {
        console.log(
          `🔄 Store: Updating question in list at index ${questionIndex}`
        );

        const oldQuestion = questions.value[questionIndex];
        const newQuestion = {
          ...oldQuestion,
          votes_up: updatedQuestion.votes_up,
          votes_down: updatedQuestion.votes_down,
          user_vote: updatedQuestion.user_vote,
          // Сохраняем связанные данные
          author: updatedQuestion.author || oldQuestion.author,
          plant: updatedQuestion.plant || oldQuestion.plant,
          answers_count:
            updatedQuestion.answers_count !== undefined
              ? updatedQuestion.answers_count
              : oldQuestion.answers_count,
        };

        // КРИТИЧНО: Создаем НОВЫЙ массив для принудительной реактивности
        questions.value = [
          ...questions.value.slice(0, questionIndex),
          newQuestion,
          ...questions.value.slice(questionIndex + 1),
        ];

        console.log("✅ Store: Created new questions array");
      }

      // 3. Принудительно запускаем следующий тик Vue для обновления
      await nextTick();
      console.log("🔄 Store: nextTick completed");

      // 4. Проверяем конечное состояние
      const questionAfter = questions.value.find((q) => q.id === questionId);
      const currentAfter =
        currentQuestion.value?.id === questionId ? currentQuestion.value : null;

      console.log("🎯 Store: After vote - Question state:", {
        inList: questionAfter
          ? {
              votes_up: questionAfter.votes_up,
              votes_down: questionAfter.votes_down,
              user_vote: questionAfter.user_vote,
            }
          : "not found",
        current: currentAfter
          ? {
              votes_up: currentAfter.votes_up,
              votes_down: currentAfter.votes_down,
              user_vote: currentAfter.user_vote,
            }
          : "not current",
      });

      return updatedQuestion;
    } catch (error) {
      console.error("❌ Store: Error voting for question:", error);
      error.value =
        error.message || `Ошибка при голосовании за вопрос ${questionId}`;
      throw error;
    }
  }

  /**
   * Создать новый ответ
   */
  async function createAnswer(answerData) {
    try {
      console.log("📝 Store: Creating answer with data:", answerData);
      const newAnswer = await answersApi.createAnswer(answerData);
      console.log("✅ Store: Answer created successfully:", newAnswer);

      if (
        currentQuestion.value &&
        currentQuestion.value.id === answerData.question_id
      ) {
        if (!currentQuestion.value.answers) {
          currentQuestion.value.answers = [];
        }

        console.log(
          "📊 Store: Before adding answer - answers count:",
          currentQuestion.value.answers.length
        );

        // Создаем новый объект вопроса для обеспечения реактивности
        const updatedAnswers = [...currentQuestion.value.answers, newAnswer];
        currentQuestion.value = {
          ...currentQuestion.value,
          answers: updatedAnswers,
          answers_count: (currentQuestion.value.answers_count || 0) + 1,
        };

        console.log(
          "📊 Store: After adding answer - answers count:",
          currentQuestion.value.answers.length
        );
        console.log(
          "📊 Store: Updated answers array:",
          currentQuestion.value.answers
        );
      } else {
        console.warn("⚠️ Store: Current question not found or ID mismatch");
        console.log("Current question:", currentQuestion.value);
        console.log("Answer question_id:", answerData.question_id);
      }

      return newAnswer;
    } catch (e) {
      error.value = e.message || "Ошибка при создании ответа";
      console.error("❌ Store: Error creating answer:", e);
      throw e;
    }
  }

  /**
   * Обновить ответ
   */
  async function updateAnswer(answerId, answerData) {
    try {
      const updatedAnswer = await answersApi.updateAnswer(answerId, answerData);

      if (currentQuestion.value && currentQuestion.value.answers) {
        const index = currentQuestion.value.answers.findIndex(
          (a) => a.id === answerId
        );
        if (index !== -1) {
          currentQuestion.value.answers[index] = updatedAnswer;
        }
      }

      return updatedAnswer;
    } catch (e) {
      error.value = e.message || `Ошибка при обновлении ответа ${answerId}`;
      console.error(`Error updating answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Удалить ответ
   */
  async function deleteAnswer(answerId) {
    try {
      console.log(`🗑️ Store: Deleting answer ${answerId}`);
      await answersApi.deleteAnswer(answerId);

      if (currentQuestion.value && currentQuestion.value.answers) {
        console.log(
          `📊 Store: Before deletion - answers count:`,
          currentQuestion.value.answers.length
        );

        // Создаем новый объект вопроса для обеспечения реактивности
        const updatedAnswers = currentQuestion.value.answers.filter(
          (a) => a.id !== answerId
        );

        currentQuestion.value = {
          ...currentQuestion.value,
          answers: updatedAnswers,
          answers_count: Math.max(
            0,
            (currentQuestion.value.answers_count || 0) - 1
          ),
        };

        console.log(
          `📊 Store: After deletion - answers count:`,
          currentQuestion.value.answers.length
        );
      }

      console.log(`✅ Store: Answer ${answerId} deleted successfully`);
      return true;
    } catch (e) {
      error.value = e.message || `Ошибка при удалении ответа ${answerId}`;
      console.error(`❌ Store: Error deleting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Отметить ответ как принятый
   */
  async function acceptAnswer(answerId) {
    try {
      console.log(`✅ Store: Accepting answer ${answerId}`);
      const updatedAnswer = await answersApi.acceptAnswer(answerId);

      if (currentQuestion.value && currentQuestion.value.answers) {
        console.log(`📊 Store: Updating answer ${answerId} as accepted`);

        // Обновляем состояние ответов - отмечаем все как не принятые, кроме текущего
        const updatedAnswers = currentQuestion.value.answers.map((answer) => ({
          ...answer,
          is_accepted: answer.id === answerId,
        }));

        // Обновляем вопрос как решенный
        currentQuestion.value = {
          ...currentQuestion.value,
          answers: updatedAnswers,
          is_solved: true,
        };

        console.log(`✅ Store: Answer ${answerId} accepted successfully`);
      }

      return updatedAnswer;
    } catch (e) {
      error.value = e.message || `Ошибка при принятии ответа ${answerId}`;
      console.error(`❌ Store: Error accepting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Отменить принятие ответа
   */
  async function unacceptAnswer(answerId) {
    try {
      console.log(`❌ Store: Unaccepting answer ${answerId}`);
      const updatedQuestion = await answersApi.unacceptAnswer(answerId);

      if (
        currentQuestion.value &&
        updatedQuestion.id === currentQuestion.value.id
      ) {
        console.log(
          `📊 Store: Updating question after unaccepting answer ${answerId}`
        );
        currentQuestion.value = updatedQuestion;
        console.log(`❌ Store: Answer ${answerId} unaccepted successfully`);
      }

      return updatedQuestion;
    } catch (e) {
      error.value =
        e.message || `Ошибка при отмене принятия ответа ${answerId}`;
      console.error(`❌ Store: Error unaccepting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Проголосовать за ответ с принудительным обновлением реактивности
   */
  async function voteForAnswer(answerId, voteType) {
    console.log(
      `🗳️ Store: Starting vote for answer ${answerId} with type ${voteType}`
    );

    try {
      // Проверяем, не является ли пользователь автором ответа
      if (currentQuestion.value?.answers) {
        const answer = currentQuestion.value.answers.find(
          (a) => a.id === answerId
        );

        if (
          answer &&
          authStore.isLoggedIn &&
          authStore.user &&
          authStore.user.id === answer.author_id
        ) {
          console.error("❌ Store: Cannot vote for own answer");
          throw new Error("Вы не можете голосовать за свой собственный ответ");
        }
      }

      // Сохраняем состояние до голосования
      const answerBefore = currentQuestion.value?.answers?.find(
        (a) => a.id === answerId
      );
      console.log(
        "📊 Store: Before vote - Answer state:",
        answerBefore
          ? {
              votes_up: answerBefore.votes_up,
              votes_down: answerBefore.votes_down,
              user_vote: answerBefore.user_vote,
            }
          : "not found"
      );

      // Вызов API
      const updatedAnswer = await answersApi.voteForAnswer(answerId, voteType);
      console.log("✅ Store: API returned:", {
        id: updatedAnswer.id,
        votes_up: updatedAnswer.votes_up,
        votes_down: updatedAnswer.votes_down,
        user_vote: updatedAnswer.user_vote,
      });

      // Обновляем ответ в currentQuestion с ПОЛНЫМ ПЕРЕСОЗДАНИЕМ МАССИВА
      if (currentQuestion.value?.answers) {
        const answerIndex = currentQuestion.value.answers.findIndex(
          (a) => a.id === answerId
        );
        if (answerIndex !== -1) {
          console.log(`🔄 Store: Updating answer at index ${answerIndex}`);

          const oldAnswer = currentQuestion.value.answers[answerIndex];
          const newAnswer = {
            ...oldAnswer,
            votes_up: updatedAnswer.votes_up,
            votes_down: updatedAnswer.votes_down,
            user_vote: updatedAnswer.user_vote,
            // Сохраняем остальные поля
            ...Object.fromEntries(
              Object.entries(updatedAnswer).filter(
                ([key, value]) => value !== undefined && key !== "question_id"
              )
            ),
          };

          // КРИТИЧНО: Создаем НОВЫЙ массив ответов
          const newAnswers = [
            ...currentQuestion.value.answers.slice(0, answerIndex),
            newAnswer,
            ...currentQuestion.value.answers.slice(answerIndex + 1),
          ];

          // Обновляем currentQuestion с новым массивом ответов
          currentQuestion.value = {
            ...currentQuestion.value,
            answers: newAnswers,
          };

          console.log("✅ Store: Created new answers array");
        }
      }

      // Принудительно запускаем следующий тик Vue для обновления
      await nextTick();
      console.log("🔄 Store: nextTick completed");

      // Проверяем конечное состояние
      const answerAfter = currentQuestion.value?.answers?.find(
        (a) => a.id === answerId
      );
      console.log(
        "🎯 Store: After vote - Answer state:",
        answerAfter
          ? {
              votes_up: answerAfter.votes_up,
              votes_down: answerAfter.votes_down,
              user_vote: answerAfter.user_vote,
            }
          : "not found"
      );

      return updatedAnswer;
    } catch (error) {
      console.error("❌ Store: Error voting for answer:", error);
      throw error;
    }
  }

  /**
   * Обновить фильтры и перезагрузить вопросы
   */
  async function updateFilters(newFilters) {
    Object.keys(newFilters).forEach((key) => {
      if (newFilters[key] !== undefined) {
        activeFilters.value[key] = newFilters[key];
      }
    });

    return await loadQuestions(1, pagination.value.size);
  }

  /**
   * Очистить все фильтры и перезагрузить вопросы
   */
  async function clearFilters() {
    return await loadQuestions(1, pagination.value.size, true);
  }

  /**
   * Очистить ошибку
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Очистить текущий вопрос
   */
  function clearCurrentQuestion() {
    currentQuestion.value = null;
  }

  // Возвращаем публичное API хранилища
  return {
    // State
    questions,
    currentQuestion,
    isLoading,
    error,
    pagination,
    activeFilters,

    // Getters
    getQuestions,
    getCurrentQuestion,
    getIsLoading,
    getError,
    getPagination,
    getActiveFilters,

    // Actions
    loadQuestions,
    loadQuestionsByPlant,
    loadQuestionById,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    voteForQuestion,
    createAnswer,
    updateAnswer,
    deleteAnswer,
    acceptAnswer,
    unacceptAnswer,
    voteForAnswer,
    updateFilters,
    clearFilters,
    clearError,
    clearCurrentQuestion,
  };
});

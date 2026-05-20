import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, Loader2, MessageCircleQuestion, Send, UserRound } from 'lucide-react';
import Footer from '../components/Footer';
import TopNavigationStrip from '../components/TopNavigationStrip';
import { apiService } from '../services/api';

const suggestedQuestions = [
  'Какие исходные данные нужны для расчета графика СНЭЭ?',
  'Как должен быть устроен суточный профиль баланса мощности?',
  'Что делать, если в Excel-файле больше 24 значений?',
];

const InputDataFaqPage = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const trimmedQuestion = useMemo(() => question.trim(), [question]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!trimmedQuestion || isLoading) {
      return;
    }

    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text: trimmedQuestion,
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setQuestion('');
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiService.askInputDataFaq(trimmedQuestion);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: result.answer,
        },
      ]);
    } catch (requestError) {
      console.error('NotebookLM FAQ request failed:', requestError);
      setError(requestError.response?.data?.detail || 'Не удалось получить ответ NotebookLM');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (suggestedQuestion) => {
    setQuestion(suggestedQuestion);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <TopNavigationStrip currentPage="input-data-faq" className="sticky top-0 z-50" />

      <section className="relative overflow-hidden bg-gradient-to-br from-primary-300 via-primary-800 to-purple-900 text-white">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -left-20 top-10 h-72 w-72 rounded-full bg-primary-400/20 blur-3xl" />
          <div className="absolute -right-10 bottom-0 h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl" />
        </div>

        <div className="relative section-container py-10 md:py-14">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-4xl text-center"
          >
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-blue-50 backdrop-blur">
              <MessageCircleQuestion className="h-4 w-4" />
              FAQ по исходным данным
            </div>

            <h1 className="mb-4 text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
              Спросите о подаче исходных данных
            </h1>

            <p className="mx-auto max-w-3xl text-lg text-blue-100 md:text-xl">
              Вопрос отправляется в заранее подготовленный блокнот NotebookLM, а ответ возвращается
              сюда в окно чата.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="section-container py-8 md:py-10">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[360px_1fr]">
          <motion.aside
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            className="card h-fit"
          >
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-2xl bg-primary-100 p-3 text-primary-700">
                <Bot className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Быстрые вопросы</h2>
                <p className="text-sm text-gray-500">Можно выбрать пример или написать свой вопрос</p>
              </div>
            </div>

            <div className="space-y-3">
              {suggestedQuestions.map((suggestedQuestion) => (
                <button
                  key={suggestedQuestion}
                  type="button"
                  onClick={() => handleSuggestedQuestion(suggestedQuestion)}
                  className="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-left text-sm text-gray-700 transition-all duration-300 hover:border-primary-200 hover:bg-primary-50 hover:text-primary-900"
                >
                  {suggestedQuestion}
                </button>
              ))}
            </div>
          </motion.aside>

          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            className="card flex min-h-[640px] flex-col overflow-hidden p-0"
          >
            <div className="border-b border-gray-200 bg-white/90 px-6 py-5">
              <div className="text-2xl font-bold text-gray-900">Чат с NotebookLM</div>
              <div className="mt-1 text-sm text-gray-500">
                Ответы формируются на основе материалов подготовленного блокнота.
              </div>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50/80 px-4 py-5 md:px-6">
              {messages.length ? (
                messages.map((message) => {
                  const isUser = message.role === 'user';

                  return (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      {!isUser && (
                        <div className="mt-1 h-9 w-9 shrink-0 rounded-full bg-primary-100 p-2 text-primary-700">
                          <Bot className="h-5 w-5" />
                        </div>
                      )}

                      <div
                        className={`max-w-[82%] whitespace-pre-wrap rounded-3xl px-5 py-3 text-sm leading-6 shadow-sm ${
                          isUser
                            ? 'bg-primary-600 text-white'
                            : 'border border-gray-200 bg-white text-gray-800'
                        }`}
                      >
                        {message.text}
                      </div>

                      {isUser && (
                        <div className="mt-1 h-9 w-9 shrink-0 rounded-full bg-slate-200 p-2 text-slate-700">
                          <UserRound className="h-5 w-5" />
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                <div className="flex h-full min-h-[360px] items-center justify-center rounded-3xl border border-dashed border-gray-300 bg-white/70 p-8 text-center">
                  <div>
                    <MessageCircleQuestion className="mx-auto mb-4 h-10 w-10 text-primary-600" />
                    <div className="text-xl font-semibold text-gray-900">Задайте первый вопрос</div>
                    <p className="mt-2 max-w-md text-sm text-gray-500">
                      Например, уточните формат Excel-файла, количество значений или смысл знаков в
                      профиле баланса мощности.
                    </p>
                  </div>
                </div>
              )}

              {isLoading && (
                <div className="flex items-center gap-3 text-sm text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  NotebookLM готовит ответ...
                </div>
              )}

              {error && (
                <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white px-4 py-4 md:px-6">
              <div className="flex flex-col gap-3 md:flex-row">
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Напишите вопрос по исходным данным..."
                  rows={3}
                  className="min-h-[84px] flex-1 resize-none rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-800 outline-none transition-all duration-300 focus:border-primary-300 focus:ring-4 focus:ring-primary-100"
                  disabled={isLoading}
                />

                <button
                  type="submit"
                  disabled={!trimmedQuestion || isLoading}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-3 font-semibold text-white shadow-lg transition-all duration-300 hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:scale-100"
                >
                  {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                  Отправить
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      </section>

      <Footer
        productName="FAQ по подаче исходных данных"
        subtitle="Чат-страница для вопросов по подготовке данных перед расчетом СНЭЭ."
        copyrightName="FAQ по исходным данным"
        tagline="с ответами из подготовленного блокнота NotebookLM"
        techStack="React, FastAPI, notebooklm-py"
      />
    </div>
  );
};

export default InputDataFaqPage;

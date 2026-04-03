import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowUpRight,
  ExternalLink,
  FileCode2,
  LayoutGrid,
  UserRound,
} from 'lucide-react';
import Footer from '../components/Footer';
import TopNavigationStrip from '../components/TopNavigationStrip';

const buildTaskUrl = (fileName) => `${import.meta.env.BASE_URL}html_task/${fileName}`;
const MANIFEST_URL = `${import.meta.env.BASE_URL}html_task/manifest.json`;

const mapTasks = (manifest) =>
  [...manifest]
    .sort((firstTask, secondTask) => firstTask.title.localeCompare(secondTask.title, 'ru'))
    .map((task) => ({
      ...task,
      url: buildTaskUrl(task.fileName),
    }));

const OtherTasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  const selectedTask = useMemo(
    () => tasks.find((task) => task.id === selectedTaskId) ?? tasks[0] ?? null,
    [selectedTaskId, tasks]
  );

  useEffect(() => {
    let isMounted = true;

    const loadTasks = async () => {
      try {
        const manifestUrl = import.meta.env.DEV
          ? `${MANIFEST_URL}?t=${Date.now()}`
          : MANIFEST_URL;
        const response = await fetch(manifestUrl, { cache: 'no-store' });

        if (!response.ok) {
          throw new Error(`Failed to load manifest: ${response.status}`);
        }

        const manifest = await response.json();

        if (isMounted) {
          setTasks(mapTasks(manifest));
        }
      } catch (error) {
        console.error('Failed to load html task manifest:', error);
        if (isMounted) {
          setTasks([]);
        }
      }
    };

    loadTasks();

    const intervalId = import.meta.env.DEV ? window.setInterval(loadTasks, 2000) : null;

    return () => {
      isMounted = false;
      if (intervalId) {
        window.clearInterval(intervalId);
      }
    };
  }, []);

  useEffect(() => {
    if (!tasks.length) {
      if (selectedTaskId !== null) {
        setSelectedTaskId(null);
      }
      return;
    }

    if (!tasks.some((task) => task.id === selectedTaskId)) {
      setSelectedTaskId(tasks[0].id);
    }
  }, [selectedTaskId, tasks]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <TopNavigationStrip currentPage="tasks" className="sticky top-0 z-50" />

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
            className="mx-auto max-w-5xl text-center"
          >
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-blue-50 backdrop-blur">
              <LayoutGrid className="h-4 w-4" />
              Каталог HTML-инструментов СПЭС
            </div>

            <h1 className="mb-4 text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
              Прочие задачи СПЭС
            </h1>

            <p className="mx-auto mb-10 max-w-3xl text-lg text-blue-100 md:text-xl">
              Отдельная страница с автоматическим меню HTML-задач. Список собирается напрямую из
              папки `html_task`, а сами файлы подключаются без перекодирования и открываются как
              есть.
            </p>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {tasks.length ? (
                tasks.map((task, index) => {
                  const isActive = task.id === selectedTask?.id;

                  return (
                    <motion.button
                      key={task.id}
                      type="button"
                      initial={{ opacity: 0, y: 18 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.45, delay: 0.08 * index }}
                      onClick={() => setSelectedTaskId(task.id)}
                      className={`rounded-2xl border p-5 text-left backdrop-blur transition-all duration-300 ${
                        isActive
                          ? 'border-white/40 bg-white/20 shadow-2xl shadow-slate-950/20'
                          : 'border-white/10 bg-white/10 hover:-translate-y-1 hover:border-white/25 hover:bg-white/15'
                      }`}
                    >
                      <div className="mb-4 flex items-center justify-between gap-3">
                        <div className="rounded-xl bg-white/15 p-3">
                          <FileCode2 className="h-5 w-5" />
                        </div>
                        <ArrowUpRight className="h-4 w-4 text-blue-100" />
                      </div>

                      <div className="mb-2 line-clamp-3 text-lg font-semibold">{task.title}</div>
                      {/* <div className="mb-3 text-sm text-blue-100/90">{task.fileName}</div> */}

                      <div className="text-xs text-blue-50/75">
                        {task.author ? `Автор: ${task.author}` : 'Автор в meta не указан'}
                      </div>
                    </motion.button>
                  );
                })
              ) : (
                <div className="col-span-full rounded-3xl border border-white/10 bg-white/10 p-8 text-left backdrop-blur">
                  <div className="mb-3 text-xl font-semibold">HTML-файлы не найдены</div>
                  <p className="text-blue-100">
                    Добавьте файлы в папку `html_task`, и ссылки на них появятся здесь автоматически.
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      <section className="section-container py-8 md:py-10">
        <div className="w-full">
          {/* <motion.aside
            initial={{ opacity: 0, x: -16 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            viewport={{ once: true }}
            className="card h-fit"
          >
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-2xl bg-primary-100 p-3 text-primary-700">
                <MonitorPlay className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">HTML-навигация</h2>
                <p className="text-sm text-gray-500">Запуск задач без изменения исходных HTML</p>
              </div>
            </div>

            <div className="space-y-3">
              {tasks.map((task) => {
                const isActive = task.id === selectedTask?.id;

                return (
                  <button
                    key={task.id}
                    type="button"
                    onClick={() => setSelectedTaskId(task.id)}
                    className={`w-full rounded-2xl border px-4 py-3 text-left transition-all duration-300 ${
                      isActive
                        ? 'border-primary-300 bg-primary-50 text-primary-900 shadow-md'
                        : 'border-gray-200 bg-white hover:border-primary-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-semibold">{task.title}</div>
                    <div className="mt-1 text-xs text-gray-500">{task.fileName}</div>
                  </button>
                );
              })}
            </div>
          </motion.aside>
          */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            viewport={{ once: true }}
            className="card w-full overflow-hidden p-0"
          >
            {selectedTask ? (
              <>
                <div className="flex flex-col gap-4 border-b border-gray-200 bg-white/90 px-6 py-5 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="mb-1 text-2xl font-bold text-gray-900">{selectedTask.title}</div>
                    <div className="text-sm text-gray-500">{selectedTask.fileName}</div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <div className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-4 py-2 text-sm text-gray-700">
                      <UserRound className="h-4 w-4 text-primary-700" />
                      {selectedTask.author || 'Автор в meta не указан'}
                    </div>

                    <a
                      href={selectedTask.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary-600 to-primary-700 px-4 py-2 text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:scale-[1.02]"
                    >
                      Открыть отдельно
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>

                <iframe
                  src={selectedTask.url}
                  title={selectedTask.title}
                  className="h-[85vh] min-h-[920px] w-full bg-white"
                />
              </>
            ) : (
              <div className="px-6 py-12 text-center text-gray-500">
                Выберите HTML-страницу для запуска.
              </div>
            )}
          </motion.div>
        </div>
      </section>

      <Footer
        productName="Прочие задачи СПЭС"
        subtitle="Единая точка входа для HTML-инструментов и вспомогательных расчетных страниц."
        copyrightName="Прочие задачи СПЭС"
        tagline="для быстрого доступа к прикладным HTML-решениям"
        techStack="HTML-файлы подключаются в исходном виде через каталог html_task"
        author={selectedTask?.author || null}
      />
    </div>
  );
};

export default OtherTasksPage;

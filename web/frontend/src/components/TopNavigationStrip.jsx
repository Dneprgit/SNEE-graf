import { motion } from 'framer-motion';

const navigationItems = [
  { href: '#/', label: 'СНЭЭ Graf', page: 'home' },
  { href: '#/other-tasks', label: 'Прочие задачи СПЭС', page: 'tasks' },
  { href: '#/input-data-faq', label: 'FAQ по подаче исходных данных', page: 'input-data-faq' },
];

const TopNavigationStrip = ({ currentPage, className = '' }) => {
  return (
    <div className={`border-b border-white/10 bg-slate-950/95 text-white backdrop-blur-md ${className}`}>
      <div className="section-container py-3">
        <nav className="flex flex-wrap items-center gap-2">
          {navigationItems.map((item, index) => {
            const isActive = item.page === currentPage;

            return (
              <motion.a
                key={item.page}
                href={item.href}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: index * 0.08 }}
                className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'border-primary-400 bg-primary-500/20 text-white shadow-lg shadow-primary-900/20'
                    : 'border-white/15 bg-white/5 text-blue-100 hover:border-primary-300/60 hover:bg-white/10 hover:text-white'
                }`}
              >
                {item.label}
              </motion.a>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default TopNavigationStrip;

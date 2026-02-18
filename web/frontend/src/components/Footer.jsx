import { motion } from 'framer-motion';
import { Github, Mail, Heart } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <div className="section-container py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <div className="mb-6">
            <h3 className="text-2xl font-bold mb-2">СНЭЭ Graf v1.523</h3>
            <p className="text-gray-400">
              Визуализация диспетчерского графика системы накопления электрической энергии
            </p>
          </div>

          <div className="flex justify-center space-x-6 mb-6">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-primary-400 transition-colors duration-300"
              title="GitHub"
            >
              <Github className="w-6 h-6" />
            </a>
            <a
              href="mailto:info@example.com"
              className="hover:text-primary-400 transition-colors duration-300"
              title="Email"
            >
              <Mail className="w-6 h-6" />
            </a>
          </div>

          <div className="border-t border-gray-700 pt-6">
            <p className="text-sm text-gray-400 flex items-center justify-center">
              © {currentYear} СНЭЭ Graf. Создано с
              <Heart className="w-4 h-4 mx-1 text-red-500 fill-current" />
              для оптимизации энергетических систем
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Powered by FastAPI, React, Recharts & D3.js
            </p>
          </div>
        </motion.div>
      </div>
    </footer>
  );
};

export default Footer;


import { motion } from 'framer-motion'
import { Sparkles, Shield, Database, Key, Zap } from 'lucide-react'

export default function ExampleQuestions({ onQuestionClick }) {
  const questions = [
    {
      icon: Sparkles,
      text: 'מה צבעי העיצוב העיקריים בפרויקט?',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Shield,
      text: 'מה בדקו באודית האבטחה?',
      color: 'from-red-500 to-pink-500'
    },
    {
      icon: Database,
      text: 'איך עושים database migration?',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Key,
      text: 'איזה שיטת authentication השתמשו?',
      color: 'from-purple-500 to-indigo-500'
    },
    {
      icon: Zap,
      text: 'איך עובדים background jobs?',
      color: 'from-yellow-500 to-orange-500'
    }
  ]

  return (
    <div className="w-full max-w-2xl">
      <h3 className="text-lg font-medium mb-4 text-gray-700 dark:text-gray-300">
        שאלות לדוגמה:
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {questions.map((question, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onQuestionClick(question.text)}
            className="p-4 glass-effect rounded-xl text-right hover:shadow-lg transition-all group"
          >
            <div className="flex items-start gap-3">
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${question.color} flex items-center justify-center flex-shrink-0`}>
                <question.icon className="text-white" size={20} />
              </div>
              <div className="flex-1">
                <p className="text-sm group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                  {question.text}
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}

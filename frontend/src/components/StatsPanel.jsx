import { TrendingUp, Clock, MessageSquare } from 'lucide-react'
import { motion } from 'framer-motion'

export default function StatsPanel({ stats }) {
  const items = [
    { icon: MessageSquare, label: 'שאלות היום', value: '0', color: 'text-blue-500' },
    { icon: Clock, label: 'זמן תגובה ממוצע', value: '2.3s', color: 'text-green-500' },
    { icon: TrendingUp, label: 'דיוק', value: '94%', color: 'text-purple-500' }
  ]

  return (
    <div className="bg-gradient-to-r from-primary-500/10 to-purple-500/10 border-b border-gray-200 dark:border-gray-700 p-4">
      <div className="container mx-auto">
        <div className="grid grid-cols-3 gap-4">
          {items.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3"
            >
              <div className={`${item.color}`}>
                <item.icon size={24} />
              </div>
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{item.label}</div>
                <div className="text-xl font-bold">{item.value}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

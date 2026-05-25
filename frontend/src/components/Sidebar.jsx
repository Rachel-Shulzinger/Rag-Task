import { FileText, Layers, Box, CheckCircle } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Sidebar({ stats }) {
  const items = [
    {
      icon: FileText,
      label: 'Cursor AI',
      count: 10,
      color: 'bg-blue-500'
    },
    {
      icon: FileText,
      label: 'Claude Code',
      count: 8,
      color: 'bg-purple-500'
    },
    {
      icon: FileText,
      label: 'Kiro',
      count: 6,
      color: 'bg-pink-500'
    }
  ]

  return (
    <aside className="w-80 glass-effect border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Layers size={20} />
            מקורות נתונים
          </h2>
          
          <div className="space-y-3">
            {items.map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg glass-effect hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${item.color} rounded-lg flex items-center justify-center`}>
                      <item.icon className="text-white" size={20} />
                    </div>
                    <div>
                      <div className="font-medium">{item.label}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {item.count} קבצים
                      </div>
                    </div>
                  </div>
                  <CheckCircle size={20} className="text-green-500" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
          <h3 className="font-bold mb-3 flex items-center gap-2">
            <Box size={18} />
            סטטיסטיקות
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500 dark:text-gray-400">סך מסמכים:</span>
              <span className="font-medium">{stats.totalDocs || 24}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 dark:text-gray-400">Chunks:</span>
              <span className="font-medium">{stats.totalChunks || '~150'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 dark:text-gray-400">סטטוס:</span>
              <span className="text-green-500 font-medium">✓ מוכן</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

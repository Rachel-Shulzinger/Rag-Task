import { motion } from 'framer-motion'
import { User, Bot, FileText } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isError = message.error

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-primary-500' : isError ? 'bg-red-500' : 'bg-purple-500'
      }`}>
        {isUser ? <User className="text-white" size={20} /> : <Bot className="text-white" size={20} />}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : isError
              ? 'bg-red-100 dark:bg-red-900/30 text-red-900 dark:text-red-200'
              : 'glass-effect'
        }`}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 space-y-2"
          >
            <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
              <FileText size={16} />
              מקורות:
            </div>
            {message.sources.map((source, index) => (
              <div
                key={index}
                className="text-sm glass-effect p-3 rounded-lg"
              >
                <div className="font-medium text-primary-600 dark:text-primary-400">
                  {source.filename}
                </div>
                {source.excerpt && (
                  <div className="text-gray-600 dark:text-gray-400 mt-1 text-xs">
                    "{source.excerpt.substring(0, 100)}..."
                  </div>
                )}
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import StatsPanel from './components/StatsPanel'
import LoadingScreen from './components/LoadingScreen'

function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [stats, setStats] = useState({
    totalDocs: 0,
    totalChunks: 0,
    isReady: false
  })

  useEffect(() => {
    // Apply dark mode
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  useEffect(() => {
    // Check if backend is ready
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/health')
        const data = await response.json()
        setStats(data)
        setIsLoading(false)
      } catch (error) {
        console.log('Backend not ready yet, retrying...')
        setTimeout(checkBackend, 2000)
      }
    }
    checkBackend()
  }, [])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header 
        darkMode={darkMode} 
        setDarkMode={setDarkMode}
        setSidebarOpen={setSidebarOpen}
        sidebarOpen={sidebarOpen}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25 }}
            >
              <Sidebar stats={stats} />
            </motion.div>
          )}
        </AnimatePresence>
        
        <main className="flex-1 overflow-hidden flex flex-col">
          <StatsPanel stats={stats} />
          <ChatInterface />
        </main>
      </div>
    </div>
  )
}

export default App

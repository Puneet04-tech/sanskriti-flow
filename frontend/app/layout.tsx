import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Sanskriti-Flow | Making Education Accessible',
  description: 'The Autonomous, Vision-Aware Localization & Assessment Ecosystem',
  keywords: ['education', 'localization', 'AI', 'FOSS', 'multilingual'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <nav className="relative z-50 glass-morphism-strong border-b border-cyan-500/30 backdrop-blur-xl">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div className="group">
              <h1 className="text-3xl font-bold neon-text" style={{ color: '#00f3ff' }}>
                Sanskriti-Flow
              </h1>
              <p className="text-sm text-cyan-300 opacity-90 group-hover:opacity-100 transition-opacity">
                ⚡ Making world-class education accessible
              </p>
            </div>
            <div className="flex gap-6">
              <a href="/" className="text-cyan-300 hover:text-pink-400 transition-colors duration-300 font-semibold hover:neon-text">Home</a>
              <a href="/about" className="text-cyan-300 hover:text-pink-400 transition-colors duration-300 font-semibold hover:neon-text">About</a>
              <a href="/docs" className="text-cyan-300 hover:text-pink-400 transition-colors duration-300 font-semibold hover:neon-text">Docs</a>
            </div>
          </div>
        </nav>
        <main className="min-h-screen relative">
          {children}
        </main>
        <footer className="relative z-50 glass-morphism-strong border-t border-cyan-500/30 backdrop-blur-xl p-8 mt-20">
          <div className="container mx-auto text-center">
            <p className="text-2xl font-bold neon-text mb-2" style={{ color: '#ff00ff' }}>
              Sanskriti-Flow
            </p>
            <p className="text-cyan-300 text-sm mt-3 flex items-center justify-center gap-2">
              🏆 FOSS Hack 2026 | 🎓 IIT Bombay | 📜 GPL-3.0 License
            </p>
            <p className="text-cyan-400/60 text-xs mt-4 max-w-2xl mx-auto">
              Built with FastAPI, Next.js, Faster-Whisper, NLLB-200, CosyVoice2, and LatentSync
            </p>
            <div className="mt-6 flex justify-center gap-4">
              <span className="px-4 py-2 glass-morphism rounded-full text-cyan-400 text-sm font-semibold neon-glow">
                🚀 100% Open Source
              </span>
              <span className="px-4 py-2 glass-morphism rounded-full text-pink-400 text-sm font-semibold neon-glow-pink">
                🌍 10+ Languages
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}

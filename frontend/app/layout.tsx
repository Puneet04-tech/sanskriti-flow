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
        <nav className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white p-4 shadow-lg">
          <div className="container mx-auto flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Sanskriti-Flow</h1>
              <p className="text-sm opacity-90">Making world-class education accessible</p>
            </div>
            <div className="flex gap-4">
              <a href="/" className="hover:underline">Home</a>
              <a href="/about" className="hover:underline">About</a>
              <a href="/docs" className="hover:underline">Docs</a>
            </div>
          </div>
        </nav>
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-gray-900 text-white p-8 mt-16">
          <div className="container mx-auto text-center">
            <p className="text-lg font-semibold">Sanskriti-Flow</p>
            <p className="text-sm opacity-75 mt-2">
              FOSS Hack 2026 | IIT Bombay | GPL-3.0 License
            </p>
            <p className="text-xs opacity-50 mt-4">
              Built with FastAPI, Next.js, Faster-Whisper, NLLB-200, and Llama 3.1
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}

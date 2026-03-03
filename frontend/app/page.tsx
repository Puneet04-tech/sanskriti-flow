'use client'

import { useState } from 'react'
import Link from 'next/link'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [videoUrl, setVideoUrl] = useState('')
  const [targetLanguage, setTargetLanguage] = useState('hi')
  const [enableQuiz, setEnableQuiz] = useState(true)
  const [enableVisionSync, setEnableVisionSync] = useState(true)
  const [enableExplainer, setEnableExplainer] = useState(false)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const languages = [
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'ta', name: 'Tamil (தமிழ்)' },
    { code: 'te', name: 'Telugu (తెలుగు)' },
    { code: 'bn', name: 'Bengali (বাংলা)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
    { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
    { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
    { code: 'ml', name: 'Malayalam (മലയാളം)' },
    { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)' },
    { code: 'or', name: 'Odia (ଓଡ଼ିଆ)' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/api/v1/localize/`, {
        video_url: videoUrl,
        target_language: targetLanguage,
        enable_quiz: enableQuiz,
        enable_vision_sync: enableVisionSync,
        enable_explainer: enableExplainer,
      })

      setJobId(response.data.job_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit job')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-16 relative z-10">
      {/* Hero Section */}
      <div className="text-center mb-16 animate-float">
        <h1 className="text-6xl font-bold mb-6 neon-text" style={{ color: '#00f3ff' }}>
          Transform Education
          <br />
          <span className="neon-text" style={{ color: '#ff00ff' }}>Break Language Barriers</span>
        </h1>
        <p className="text-xl text-cyan-100 max-w-3xl mx-auto leading-relaxed">
          Convert English educational videos into interactive, native-language experiences
          with AI-powered translation, voice cloning, and intelligent quizzes.
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <span className="px-4 py-2 glass-morphism rounded-full text-cyan-400 text-sm font-semibold neon-glow">
            🚀 100% FOSS
          </span>
          <span className="px-4 py-2 glass-morphism rounded-full text-pink-400 text-sm font-semibold neon-glow-pink">
            ⚡ AI-Powered
          </span>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="p-6 glass-morphism rounded-2xl hover:glass-morphism-strong transition-all duration-300 group hover:scale-105 neon-border">
          <div className="text-5xl mb-4 animate-glow" style={{ color: '#00f3ff' }}>🎓</div>
          <h3 className="text-2xl font-bold mb-3 text-cyan-300 group-hover:text-cyan-200">Explainer Mode</h3>
          <p className="text-cyan-100 opacity-90">
            Simplifies complex content into easy Hinglish - no heavy words, just clear explanations
          </p>
        </div>
        <div className="p-6 glass-morphism rounded-2xl hover:glass-morphism-strong transition-all duration-300 group hover:scale-105 neon-border">
          <div className="text-5xl mb-4 animate-glow" style={{ color: '#ff00ff' }}>👁️</div>
          <h3 className="text-2xl font-bold mb-3 text-pink-300 group-hover:text-pink-200">Vision-Sync</h3>
          <p className="text-cyan-100 opacity-90">
            Translates blackboard text and diagrams with AI-powered visual understanding
          </p>
        </div>
        <div className="p-6 glass-morphism rounded-2xl hover:glass-morphism-strong transition-all duration-300 group hover:scale-105 neon-border">
          <div className="text-5xl mb-4 animate-glow" style={{ color: '#a855f7' }}>🧠</div>
          <h3 className="text-2xl font-bold mb-3 text-purple-300 group-hover:text-purple-200">Interactive Quizzes</h3>
          <p className="text-cyan-100 opacity-90">
            Auto-generated MCQs at key moments to test comprehension
          </p>
        </div>
      </div>

      {/* How to Use Section */}
      <div className="max-w-5xl mx-auto mb-16 glass-morphism-strong rounded-3xl p-8 neon-glow">
        <h2 className="text-4xl font-bold mb-8 text-center neon-text" style={{ color: '#ff00ff' }}>
          📖 How to Use This Platform
        </h2>

        {/* Step by Step Guide */}
        <div className="space-y-6 mb-10">
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 flex items-center justify-center font-bold neon-glow">1</div>
            <div>
              <h3 className="text-xl font-bold text-cyan-300 mb-2">📹 Paste Video URL</h3>
              <p className="text-cyan-100 leading-relaxed">
                Enter the URL of any educational video (YouTube, direct MP4 link, etc.). The video should be in English for best results.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center font-bold neon-glow">2</div>
            <div>
              <h3 className="text-xl font-bold text-pink-300 mb-2">🌍 Select Target Language</h3>
              <p className="text-cyan-100 leading-relaxed">
                Choose from 10+ Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, and Odia.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center font-bold neon-glow-pink">3</div>
            <div>
              <h3 className="text-xl font-bold text-purple-300 mb-2">⚙️ Enable Features</h3>
              <p className="text-cyan-100 leading-relaxed mb-3">
                Toggle the features you want to enable:
              </p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400 mt-1">✨</span>
                  <span><strong className="text-cyan-300">Interactive Quizzes:</strong> Generates 3-5 multiple-choice questions to test understanding. Questions appear at key moments in the video.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-pink-400 mt-1">👁️</span>
                  <span><strong className="text-pink-300">Vision-Sync Overlays:</strong> Detects blackboard text, diagrams, and equations, then adds translated labels as AR overlays. Perfect for technical content.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-1">🎓</span>
                  <span><strong className="text-purple-300">Explainer Mode:</strong> Converts complex technical language into simple Hinglish explanations. Great for beginners or non-technical audiences.</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-pink-500 flex items-center justify-center font-bold neon-glow">4</div>
            <div>
              <h3 className="text-xl font-bold text-cyan-300 mb-2">🚀 Start Processing</h3>
              <p className="text-cyan-100 leading-relaxed">
                Click "Start Localization" and you'll receive a Job ID. Processing takes approximately 15 minutes for a 10-minute video. Track progress using the Job ID.
              </p>
            </div>
          </div>
        </div>

        {/* Features Explained */}
        <div className="border-t border-cyan-500/30 pt-8 mb-8">
          <h3 className="text-2xl font-bold mb-6 text-center neon-text" style={{ color: '#00f3ff' }}>
            🎯 What Happens During Processing
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-morphism rounded-xl p-5">
              <h4 className="font-bold text-cyan-300 mb-3 flex items-center gap-2">
                <span className="text-2xl">🎤</span> Automatic Features (Always Enabled)
              </h4>
              <ul className="space-y-2 text-cyan-100 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400">•</span>
                  <span><strong>Speech-to-Text:</strong> Extracts accurate transcript from video audio</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400">•</span>
                  <span><strong>Neural Translation:</strong> Translates to your chosen language with technical term preservation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400">•</span>
                  <span><strong>Voice Cloning:</strong> Replicates professor's voice speaking in new language (95%+ similarity)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400">•</span>
                  <span><strong>Lip-Sync:</strong> Adjusts mouth movements to match new audio (9.8/10 accuracy)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan-400">•</span>
                  <span><strong>Subtitles:</strong> Adds accurate subtitles in target language</span>
                </li>
              </ul>
            </div>

            <div className="glass-morphism rounded-xl p-5">
              <h4 className="font-bold text-pink-300 mb-3 flex items-center gap-2">
                <span className="text-2xl">⚡</span> Optional Features (You Choose)
              </h4>
              <ul className="space-y-2 text-cyan-100 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-pink-400">•</span>
                  <span><strong>Interactive Quizzes:</strong> +2 min processing time. Generates MCQs with explanations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-pink-400">•</span>
                  <span><strong>Vision-Sync Overlays:</strong> +6 min processing time. Ideal for math/science/code tutorials</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-pink-400">•</span>
                  <span><strong>Explainer Mode:</strong> +1 min processing time. Simplifies jargon for better understanding</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Tips & Best Practices */}
        <div className="border-t border-cyan-500/30 pt-8">
          <h3 className="text-2xl font-bold mb-6 text-center neon-text" style={{ color: '#a855f7' }}>
            💡 Tips for Best Results
          </h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="glass-morphism rounded-xl p-4">
              <h4 className="font-bold text-purple-300 mb-2">✅ Do This</h4>
              <ul className="space-y-1 text-cyan-100">
                <li>• Use videos with clear audio quality</li>
                <li>• Enable Vision-Sync for whiteboard/slides</li>
                <li>• Enable Quizzes for student engagement</li>
                <li>• Use Explainer Mode for beginners</li>
              </ul>
            </div>
            <div className="glass-morphism rounded-xl p-4">
              <h4 className="font-bold text-red-300 mb-2">❌ Avoid This</h4>
              <ul className="space-y-1 text-cyan-100">
                <li>• Videos with background music/noise</li>
                <li>• Multiple speakers talking simultaneously</li>
                <li>• Videos shorter than 2 minutes</li>
                <li>• Non-educational content</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Processing Time Info */}
        <div className="mt-8 glass-morphism rounded-xl p-5 border border-cyan-500/30">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">⏱️</span>
            <h4 className="font-bold text-cyan-300 text-lg">Expected Processing Times</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
            <div>
              <div className="font-bold text-cyan-400">5-min video</div>
              <div className="text-cyan-100">~8 minutes</div>
            </div>
            <div>
              <div className="font-bold text-purple-400">10-min video</div>
              <div className="text-cyan-100">~15 minutes</div>
            </div>
            <div>
              <div className="font-bold text-pink-400">30-min video</div>
              <div className="text-cyan-100">~45 minutes</div>
            </div>
            <div>
              <div className="font-bold text-cyan-400">50-min lecture</div>
              <div className="text-cyan-100">~75 minutes</div>
            </div>
          </div>
          <p className="text-xs text-cyan-300 mt-4 text-center italic">
            * Times may vary based on video quality and enabled features. You can track progress in real-time using your Job ID.
          </p>
        </div>
      </div>

      {/* Main Form */}
      <div className="max-w-2xl mx-auto glass-morphism-strong rounded-3xl p-8 neon-glow">
        <h2 className="text-4xl font-bold mb-8 text-center neon-text" style={{ color: '#00f3ff' }}>
          Localize Your Video
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Video URL */}
          <div>
            <label className="block text-sm font-bold text-cyan-300 mb-3 tracking-wide">
              Video URL
            </label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://example.com/lecture.mp4"
              className="w-full px-4 py-3 glass-morphism rounded-xl focus:ring-2 focus:ring-cyan-500 focus:outline-none text-white placeholder-cyan-400/50 hover:neon-glow transition-all duration-300"
              required
            />
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-bold text-cyan-300 mb-3 tracking-wide">
              Target Language
            </label>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              className="w-full px-4 py-3 glass-morphism rounded-xl focus:ring-2 focus:ring-cyan-500 focus:outline-none text-white hover:neon-glow transition-all duration-300 cursor-pointer"
              style={{
                background: 'rgba(10, 14, 26, 0.7)',
                backdropFilter: 'blur(10px)'
              }}
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code} style={{ background: '#0a0e1a' }}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Feature Toggles */}
          <div className="space-y-4">
            <label className="flex items-center space-x-4 p-3 glass-morphism rounded-xl cursor-pointer hover:neon-glow transition-all duration-300 group">
              <input
                type="checkbox"
                checked={enableQuiz}
                onChange={(e) => setEnableQuiz(e.target.checked)}
                className="w-6 h-6 text-cyan-500 rounded focus:ring-2 focus:ring-cyan-500 cursor-pointer"
              />
              <span className="text-cyan-100 font-medium group-hover:text-cyan-200">✨ Generate Interactive Quizzes</span>
            </label>
            <label className="flex items-center space-x-4 p-3 glass-morphism rounded-xl cursor-pointer hover:neon-glow transition-all duration-300 group">
              <input
                type="checkbox"
                checked={enableVisionSync}
                onChange={(e) => setEnableVisionSync(e.target.checked)}
                className="w-6 h-6 text-pink-500 rounded focus:ring-2 focus:ring-pink-500 cursor-pointer"
              />
              <span className="text-cyan-100 font-medium group-hover:text-pink-200">👁️ Add Vision-Sync Overlays</span>
            </label>
            <label className="flex items-center space-x-4 p-3 glass-morphism rounded-xl cursor-pointer hover:neon-glow-pink transition-all duration-300 group">
              <input
                type="checkbox"
                checked={enableExplainer}
                onChange={(e) => setEnableExplainer(e.target.checked)}
                className="w-6 h-6 text-purple-500 rounded focus:ring-2 focus:ring-purple-500 cursor-pointer"
              />
              <span className="text-cyan-100 font-medium group-hover:text-purple-200">
                🎓 Explanation Mode (Simplified Hinglish - No Heavy Words)
              </span>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 text-white py-4 rounded-xl font-bold text-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed neon-glow shadow-2xl relative overflow-hidden group"
            style={{
              boxShadow: '0 0 30px rgba(0, 243, 255, 0.5), 0 0 60px rgba(255, 0, 255, 0.3)'
            }}
          >
            <span className="relative z-10">{loading ? '⚡ Processing...' : '🚀 Start Localization'}</span>
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 glass-morphism rounded-xl border-2 border-red-500 text-red-300 neon-glow-pink">
            ❌ {error}
          </div>
        )}

        {/* Success Display */}
        {jobId && (
          <div className="mt-6 p-5 glass-morphism-strong rounded-xl border-2 border-cyan-500 neon-glow animate-float">
            <p className="font-bold text-cyan-300 text-lg">✅ Job Created Successfully!</p>
            <p className="text-sm text-cyan-100 mt-2 font-mono bg-black/30 p-2 rounded">Job ID: {jobId}</p>
            <p className="text-sm text-cyan-200 mt-3">
              Your video is being processed.{' '}
              <Link 
                href={`/jobs?id=${jobId}`} 
                className="font-bold underline hover:text-pink-400 transition-colors duration-300 neon-text"
                style={{ color: '#ff00ff' }}
              >
                Check status →
              </Link>
            </p>
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div className="mt-20 grid md:grid-cols-4 gap-8 text-center">
        <div className="glass-morphism rounded-2xl p-6 hover:scale-110 transition-transform duration-300 neon-border">
          <div className="text-5xl font-bold neon-text" style={{ color: '#00f3ff' }}>$0.05</div>
          <div className="text-cyan-300 mt-3 font-semibold">per minute</div>
        </div>
        <div className="glass-morphism rounded-2xl p-6 hover:scale-110 transition-transform duration-300 neon-border">
          <div className="text-5xl font-bold neon-text" style={{ color: '#ff00ff' }}>15 min</div>
          <div className="text-pink-300 mt-3 font-semibold">processing time</div>
        </div>
        <div className="glass-morphism rounded-2xl p-6 hover:scale-110 transition-transform duration-300 neon-border">
          <div className="text-5xl font-bold neon-text" style={{ color: '#a855f7' }}>10+</div>
          <div className="text-purple-300 mt-3 font-semibold">languages</div>
        </div>
        <div className="glass-morphism rounded-2xl p-6 hover:scale-110 transition-transform duration-300 neon-border">
          <div className="text-5xl font-bold neon-text" style={{ color: '#ec4899' }}>100%</div>
          <div className="text-pink-300 mt-3 font-semibold">FOSS</div>
        </div>
      </div>
    </div>
  )
}

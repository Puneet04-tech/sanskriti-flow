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

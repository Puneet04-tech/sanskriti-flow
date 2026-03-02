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
      })

      setJobId(response.data.job_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit job')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-16">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
          Transform Education, Break Language Barriers
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Convert English educational videos into interactive, native-language experiences
          with AI-powered translation, voice cloning, and intelligent quizzes.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="text-4xl mb-4">🎯</div>
          <h3 className="text-xl font-bold mb-2">Neural Hinglish</h3>
          <p className="text-gray-600">
            Preserves technical terms in English while explaining concepts in your language
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="text-4xl mb-4">👁️</div>
          <h3 className="text-xl font-bold mb-2">Vision-Sync</h3>
          <p className="text-gray-600">
            Translates blackboard text and diagrams with AI-powered visual understanding
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="text-4xl mb-4">🧠</div>
          <h3 className="text-xl font-bold mb-2">Interactive Quizzes</h3>
          <p className="text-gray-600">
            Auto-generated MCQs at key moments to test comprehension
          </p>
        </div>
      </div>

      {/* Main Form */}
      <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-2xl p-8">
        <h2 className="text-3xl font-bold mb-6 text-center">Localize Your Video</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Video URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video URL
            </label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://example.com/lecture.mp4"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Language
            </label>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Feature Toggles */}
          <div className="space-y-3">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={enableQuiz}
                onChange={(e) => setEnableQuiz(e.target.checked)}
                className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-gray-700">Generate Interactive Quizzes</span>
            </label>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={enableVisionSync}
                onChange={(e) => setEnableVisionSync(e.target.checked)}
                className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-gray-700">Add Vision-Sync Overlays</span>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-primary-600 to-secondary-600 text-white py-4 rounded-lg font-semibold text-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Start Localization'}
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Success Display */}
        {jobId && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="font-semibold text-green-800">✅ Job Created Successfully!</p>
            <p className="text-sm text-green-700 mt-1 font-mono">Job ID: {jobId}</p>
            <p className="text-sm text-green-600 mt-2">
              Your video is being processed.{' '}
              <Link 
                href={`/jobs?id=${jobId}`} 
                className="font-semibold underline hover:text-green-800"
              >
                Check status →
              </Link>
            </p>
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div className="mt-16 grid md:grid-cols-4 gap-6 text-center">
        <div>
          <div className="text-4xl font-bold text-primary-600">$0.05</div>
          <div className="text-gray-600 mt-2">per minute</div>
        </div>
        <div>
          <div className="text-4xl font-bold text-primary-600">15 min</div>
          <div className="text-gray-600 mt-2">processing time</div>
        </div>
        <div>
          <div className="text-4xl font-bold text-primary-600">10+</div>
          <div className="text-gray-600 mt-2">languages</div>
        </div>
        <div>
          <div className="text-4xl font-bold text-primary-600">100%</div>
          <div className="text-gray-600 mt-2">FOSS</div>
        </div>
      </div>
    </div>
  )
}

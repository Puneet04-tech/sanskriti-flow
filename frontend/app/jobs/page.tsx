'use client'

import { useState, useEffect, useCallback, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function JobsContent() {
  const searchParams = useSearchParams()
  const [jobId, setJobId] = useState('')
  const [searchResult, setSearchResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchJobStatus = useCallback(async (id: string) => {
    setLoading(true)
    setError('')
    setSearchResult(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/jobs/${id}`)
      if (!response.ok) {
        throw new Error('Job not found')
      }
      const data = await response.json()
      setSearchResult(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch job status')
    } finally {
      setLoading(false)
    }
  }, [])

  // Auto-load job if ID in URL
  useEffect(() => {
    const idFromUrl = searchParams.get('id')
    if (idFromUrl) {
      setJobId(idFromUrl)
      // Trigger search automatically
      fetchJobStatus(idFromUrl)
    }
  }, [searchParams, fetchJobStatus])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!jobId.trim()) return
    fetchJobStatus(jobId.trim())
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'processing':
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="min-h-screen relative z-10" suppressHydrationWarning>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12 animate-float">
          <Link 
            href="/"
            className="inline-block mb-6 text-cyan-400 hover:text-pink-400 transition-colors duration-300 font-bold text-lg neon-text"
          >
            ← Back to Home
          </Link>
          <h1 className="text-6xl font-bold mb-6 neon-text" style={{ color: '#00f3ff' }}>
            Job Status
          </h1>
          <p className="text-cyan-200 text-xl">
            🚀 Track your video localization jobs
          </p>
        </div>

        {/* Search Form */}
        <div className="max-w-2xl mx-auto mb-12">
          <form onSubmit={handleSearch} className="glass-morphism-strong rounded-3xl p-8 neon-glow">
            <label className="block text-sm font-bold text-cyan-300 mb-4 tracking-wide">
              🔍 Job ID
            </label>
            <div className="flex gap-4">
              <input
                type="text"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                placeholder="Enter Job ID (e.g., 8c9161e9-1c1c-4430-ab62-4509ec944753)"
                className="flex-1 px-4 py-3 glass-morphism rounded-xl focus:ring-2 focus:ring-cyan-500 focus:outline-none text-white placeholder-cyan-400/50 hover:neon-glow transition-all duration-300"
              />
              <button
                type="submit"
                disabled={loading || !jobId.trim()}
                className="px-8 py-3 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 rounded-xl font-bold hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed neon-glow"
                style={{
                  boxShadow: '0 0 30px rgba(0, 243, 255, 0.5)'
                }}
              >
                {loading ? '⚡ Searching...' : '🚀 Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 glass-morphism rounded-xl border-2 border-red-500 p-5 text-red-300 neon-glow-pink animate-float">
            ❌ {error}
          </div>
        )}

        {/* Job Status Result */}
        {searchResult && (
          <div className="max-w-4xl mx-auto glass-morphism-strong rounded-3xl p-8 neon-glow animate-float">
            <div className="space-y-6">
              {/* Job ID */}
              <div>
                <h2 className="text-3xl font-bold mb-3 neon-text" style={{ color: '#00f3ff' }}>⚙️ Job Details</h2>
                <p className="text-cyan-300 text-sm font-mono break-all bg-black/30 p-3 rounded-xl">
                  {searchResult.job_id}
                </p>
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-3 flex-wrap">
                <span className="inline-block px-6 py-3 rounded-full text-sm font-bold glass-morphism neon-glow" style={{
                  border: '2px solid #00f3ff',
                  color: '#00f3ff',
                  textShadow: '0 0 10px currentColor'
                }}>
                  {searchResult.status?.toUpperCase() || 'UNKNOWN'}
                </span>
                
                {/* Explainer Mode Badge */}
                {searchResult.explanation_type === 'simplified_hinglish' && (
                  <span className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-bold glass-morphism neon-glow-pink" style={{
                    border: '2px solid #ff00ff',
                    color: '#ff00ff',
                    textShadow: '0 0 10px currentColor'
                  }}>
                    <span>🎓</span>
                    <span>Explainer Mode</span>
                  </span>
                )}
              </div>

              {/* Progress */}
              {searchResult.progress !== undefined && (
                <div>
                  <div className="flex justify-between text-sm mb-3">
                    <span className="text-cyan-300 font-bold">⚡ Progress</span>
                    <span className="font-bold neon-text" style={{ color: '#00f3ff' }}>{searchResult.progress.toFixed(1)}%</span>
                  </div>
                  <div className="w-full glass-morphism rounded-full h-4 overflow-hidden neon-border">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 transition-all duration-500 neon-glow"
                      style={{ 
                        width: `${searchResult.progress}%`,
                        boxShadow: '0 0 20px rgba(0, 243, 255, 0.8)'
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Current Stage */}
              {searchResult.stage && (
                <div className="flex items-center gap-4 glass-morphism rounded-xl p-4 neon-glow">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-400" style={{
                    borderTopColor: '#ff00ff',
                    borderRightColor: '#a855f7'
                  }}></div>
                  <div>
                    <p className="text-sm text-cyan-400 font-bold">🔄 Current Stage</p>
                    <p className="font-bold text-white neon-text" style={{ color: '#ff00ff' }}>{searchResult.stage}</p>
                  </div>
                </div>
              )}

              {/* ETA */}
              {searchResult.eta_seconds && (
                <div className="flex items-center justify-between glass-morphism rounded-xl p-4 neon-glow">
                  <span className="text-sm text-cyan-400 font-bold">⏱️ Estimated Time Remaining</span>
                  <span className="font-bold neon-text" style={{ color: '#a855f7' }}>
                    {Math.floor(searchResult.eta_seconds / 60)}m {searchResult.eta_seconds % 60}s
                  </span>
                </div>
              )}

              {/* Result URL */}
              {searchResult.result_url && (
                <div className="glass-morphism rounded-xl p-5 neon-glow border-2 border-cyan-500 animate-float">
                  <p className="text-lg text-cyan-300 mb-3 font-bold">✅ Processing Complete!</p>
                  <a
                    href={searchResult.result_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 rounded-xl font-bold hover:scale-105 transition-all duration-300 neon-glow text-white"
                    style={{
                      boxShadow: '0 0 30px rgba(0, 243, 255, 0.5)'
                    }}
                  >
                    🎬 Download Localized Video
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              )}

              {/* Quiz Questions Section */}
              {searchResult.quizzes && searchResult.quizzes.length > 0 && (
                <div className="bg-purple-500/20 rounded-lg p-6 border border-purple-500/30">
                  <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                    <span>🧠</span>
                    <span>Interactive Quiz</span>
                  </h3>
                  <p className="text-gray-300 text-sm mb-6">
                    Test your understanding with these auto-generated questions from the video
                  </p>
                  
                  <div className="space-y-6">
                    {searchResult.quizzes.map((quiz: any, index: number) => (
                      <div key={index} className="bg-white/5 rounded-lg p-5 border border-white/10">
                        <p className="font-semibold text-lg mb-4">
                          <span className="text-cyan-400">Q{index + 1}.</span> {quiz.question}
                        </p>
                        
                        <div className="space-y-2 mb-4">
                          {quiz.options && quiz.options.map((option: string, optIndex: number) => (
                            <div
                              key={optIndex}
                              className={`p-3 rounded-lg border transition-all ${
                                optIndex === quiz.correct_answer
                                  ? 'bg-green-500/20 border-green-500/50'
                                  : 'bg-white/5 border-white/20 hover:bg-white/10'
                              }`}
                            >
                              <span className="font-mono text-sm mr-2">
                                {String.fromCharCode(65 + optIndex)}.
                              </span>
                              <span>{option}</span>
                              {optIndex === quiz.correct_answer && (
                                <span className="ml-2 text-green-400">✓ Correct</span>
                              )}
                            </div>
                          ))}
                        </div>
                        
                        {quiz.explanation && (
                          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                            <p className="text-sm text-blue-200">
                              <strong>Explanation:</strong> {quiz.explanation}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Error Message from Job */}
              {searchResult.error && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                  <p className="text-red-200 font-semibold mb-1">Error:</p>
                  <p className="text-red-300 text-sm">{searchResult.error}</p>
                </div>
              )}

              {/* Refresh Button */}
              {searchResult.status?.toLowerCase() === 'processing' && (
                <button
                  onClick={handleSearch}
                  className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
                >
                  🔄 Refresh Status
                </button>
              )}
            </div>
          </div>
        )}

        {/* How to Use */}
        {!searchResult && !loading && (
          <div className="max-w-2xl mx-auto bg-white/5 backdrop-blur-lg rounded-2xl p-8 border border-white/10">
            <h3 className="text-xl font-bold mb-4 text-purple-400">💡 How to Track Jobs</h3>
            <ol className="space-y-3 text-gray-300">
              <li className="flex gap-3">
                <span className="text-cyan-400 font-bold">1.</span>
                After submitting a video for localization, you'll receive a <strong>Job ID</strong>
              </li>
              <li className="flex gap-3">
                <span className="text-cyan-400 font-bold">2.</span>
                Copy the Job ID and paste it in the search box above
              </li>
              <li className="flex gap-3">
                <span className="text-cyan-400 font-bold">3.</span>
                Click "Search" to see the current status and progress
              </li>
              <li className="flex gap-3">
                <span className="text-cyan-400 font-bold">4.</span>
                When complete, you'll see a download link for your localized video
              </li>
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}

export default function JobsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    }>
      <JobsContent />
    </Suspense>
  )
}

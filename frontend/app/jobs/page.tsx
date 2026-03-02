'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function JobsContent() {
  const searchParams = useSearchParams()
  const [jobId, setJobId] = useState('')
  const [searchResult, setSearchResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mounted, setMounted] = useState(false)

  // Handle client-side mounting
  useEffect(() => {
    setMounted(true)
  }, [])

  // Auto-load job if ID in URL
  useEffect(() => {
    if (!mounted) return
    const idFromUrl = searchParams.get('id')
    if (idFromUrl) {
      setJobId(idFromUrl)
      // Trigger search automatically
      fetchJobStatus(idFromUrl)
    }
  }, [searchParams, mounted])

  const fetchJobStatus = async (id: string) => {
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
  }

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <Link 
            href="/"
            className="inline-block mb-4 text-purple-400 hover:text-purple-300 transition-colors"
          >
            ← Back to Home
          </Link>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Job Status
          </h1>
          <p className="text-gray-300 text-lg">
            Track your video localization jobs
          </p>
        </div>

        {/* Search Form */}
        <div className="max-w-2xl mx-auto mb-12">
          <form onSubmit={handleSearch} className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
            <label className="block text-sm font-medium mb-2">
              Job ID
            </label>
            <div className="flex gap-4">
              <input
                type="text"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                placeholder="Enter Job ID (e.g., 8c9161e9-1c1c-4430-ab62-4509ec944753)"
                className="flex-1 px-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400"
              />
              <button
                type="submit"
                disabled={loading || !jobId.trim()}
                className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200">
            ❌ {error}
          </div>
        )}

        {/* Job Status Result */}
        {searchResult && (
          <div className="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
            <div className="space-y-6">
              {/* Job ID */}
              <div>
                <h2 className="text-2xl font-bold mb-2">Job Details</h2>
                <p className="text-gray-400 text-sm font-mono break-all">
                  {searchResult.job_id}
                </p>
              </div>

              {/* Status Badge */}
              <div>
                <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold border ${getStatusColor(searchResult.status)}`}>
                  {searchResult.status?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>

              {/* Progress */}
              {searchResult.progress !== undefined && (
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Progress</span>
                    <span className="font-semibold">{searchResult.progress.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 transition-all duration-500"
                      style={{ width: `${searchResult.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Current Stage */}
              {searchResult.stage && (
                <div className="flex items-center gap-3 bg-purple-500/20 rounded-lg p-4">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <div>
                    <p className="text-sm text-gray-400">Current Stage</p>
                    <p className="font-semibold">{searchResult.stage}</p>
                  </div>
                </div>
              )}

              {/* ETA */}
              {searchResult.eta_seconds && (
                <div className="flex items-center justify-between bg-blue-500/20 rounded-lg p-4">
                  <span className="text-sm text-gray-400">Estimated Time Remaining</span>
                  <span className="font-semibold">
                    {Math.floor(searchResult.eta_seconds / 60)}m {searchResult.eta_seconds % 60}s
                  </span>
                </div>
              )}

              {/* Result URL */}
              {searchResult.result_url && (
                <div className="bg-green-500/20 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-2">✅ Processing Complete!</p>
                  <a
                    href={searchResult.result_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 font-semibold"
                  >
                    Download Localized Video
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
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
        </div>
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
          </div>
        )}
      </div>
    </div>
  )
}

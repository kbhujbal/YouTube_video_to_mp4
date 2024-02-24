'use client'

import { useState } from 'react'
import axios from 'axios'
import Image from 'next/image'

const API_BASE_URL = 'http://localhost:8000'

interface VideoFormat {
  format_id: string
  resolution: string
  ext: string
  filesize: number
  filesize_mb: number | null
  fps: number
  vcodec: string
  needs_merge?: boolean
}

interface VideoInfo {
  title: string
  thumbnail: string
  duration: number
  uploader: string
  formats: VideoFormat[]
}

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState('')

  const fetchVideoInfo = async () => {
    if (!url.trim()) {
      setError('Please enter a YouTube URL')
      return
    }

    setLoading(true)
    setError('')
    setVideoInfo(null)
    setSelectedFormat('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/video-info`, {
        url: url.trim()
      })

      setVideoInfo(response.data)
      if (response.data.formats.length > 0) {
        setSelectedFormat(response.data.formats[0].format_id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch video information')
    } finally {
      setLoading(false)
    }
  }

  const downloadVideo = async () => {
    if (!selectedFormat || !url) return

    setDownloading(true)
    setError('')

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/download`,
        {
          url: url.trim(),
          format_id: selectedFormat
        },
        {
          responseType: 'blob',
          timeout: 300000, // 5 minutes timeout
        }
      )

      // Create a download link
      const blob = new Blob([response.data], { type: 'video/mp4' })
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl

      // Extract filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition']
      let filename = 'video.mp4'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download video')
    } finally {
      setDownloading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            YouTube Video Downloader
          </h1>
          <p className="text-xl text-gray-600">
            Download YouTube videos in your preferred quality
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                YouTube URL
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && fetchVideoInfo()}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-900"
                  disabled={loading}
                />
                <button
                  onClick={fetchVideoInfo}
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Loading...' : 'Get Info'}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {videoInfo && (
              <div className="border-t pt-6 space-y-6">
                <div className="flex gap-6">
                  {videoInfo.thumbnail && (
                    <div className="flex-shrink-0">
                      <Image
                        src={videoInfo.thumbnail}
                        alt={videoInfo.title}
                        width={320}
                        height={180}
                        className="rounded-lg shadow-md"
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {videoInfo.title}
                    </h2>
                    <div className="space-y-1 text-gray-600">
                      <p>
                        <span className="font-semibold">Uploader:</span> {videoInfo.uploader}
                      </p>
                      <p>
                        <span className="font-semibold">Duration:</span> {formatDuration(videoInfo.duration)}
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Select Quality
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {videoInfo.formats.map((format) => (
                      <label
                        key={format.format_id}
                        className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          selectedFormat === format.format_id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name="format"
                          value={format.format_id}
                          checked={selectedFormat === format.format_id}
                          onChange={(e) => setSelectedFormat(e.target.value)}
                          className="sr-only"
                        />
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-lg font-bold text-gray-900">
                              {format.resolution}
                            </span>
                            <span className="text-xs text-gray-500 uppercase">
                              {format.ext}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600">
                            {format.filesize_mb ? `${format.filesize_mb} MB` : 'Size unknown'}
                          </div>
                          {format.fps && (
                            <div className="text-xs text-gray-500">
                              {format.fps} fps
                            </div>
                          )}
                        </div>
                        {selectedFormat === format.format_id && (
                          <div className="absolute top-2 right-2">
                            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                      </label>
                    ))}
                  </div>
                </div>

                <button
                  onClick={downloadVideo}
                  disabled={downloading || !selectedFormat}
                  className="w-full px-6 py-4 bg-green-600 text-white font-bold text-lg rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {downloading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Downloading...
                    </span>
                  ) : (
                    'Download Video'
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="text-center text-gray-600 text-sm">
          <p>Enter a YouTube URL to see available download options</p>
          <p className="mt-2">Note: Please respect copyright laws and terms of service</p>
        </div>
      </div>
    </main>
  )
}

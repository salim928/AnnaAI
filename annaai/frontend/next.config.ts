import type { NextConfig } from 'next'

const config: NextConfig = {
  reactStrictMode: true,
  turbopack: {},
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'image.pollinations.ai' },
      { protocol: 'https', hostname: '*.supabase.co' },
    ],
  },
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'
    return [{ source: '/api/backend/:path*', destination: `${backend}/api/:path*` }]
  },
}

export default config

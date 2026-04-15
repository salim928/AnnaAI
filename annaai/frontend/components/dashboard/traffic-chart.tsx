'use client'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export interface TrafficPoint {
  date: string
  sessions: number
}

export function TrafficChart({ data }: { data: TrafficPoint[] }) {
  if (!data.length) {
    return (
      <p className="py-12 text-center text-sm text-muted">
        Connect Google Analytics to see traffic trends here.
      </p>
    )
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="trafficFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#e94560" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#e94560" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="sessions"
            stroke="#e94560"
            strokeWidth={2}
            fill="url(#trafficFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

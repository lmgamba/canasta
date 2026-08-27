// API base URL for the local backend served by uvicorn on port 8000.
const API_BASE = 'http://localhost:8000/api'

export type SpendingPeriod = 'weekly' | 'monthly'

// One point in the spending-over-time series.
export interface SpendingOverTimeItem {
  period_label: string
  total_amount: number
}

// Total spend within a single category.
export interface SpendingByCategoryItem {
  category: string
  total_amount: number
}

// One row in the most-purchased-items ranking.
export interface TopItem {
  normalized_name: string
  total_spend: number
  purchase_count: number
}

export async function fetchSpendingOverTime(
  period: SpendingPeriod,
): Promise<SpendingOverTimeItem[]> {
  const res = await fetch(`${API_BASE}/analytics/spending-over-time?period=${period}`)
  if (!res.ok) throw new Error('Could not load spending over time.')
  return res.json()
}

export async function fetchSpendingByCategory(): Promise<SpendingByCategoryItem[]> {
  const res = await fetch(`${API_BASE}/analytics/spending-by-category`)
  if (!res.ok) throw new Error('Could not load spending by category.')
  return res.json()
}

export async function fetchTopItems(): Promise<TopItem[]> {
  const res = await fetch(`${API_BASE}/analytics/top-items`)
  if (!res.ok) throw new Error('Could not load top items.')
  return res.json()
}

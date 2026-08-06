// API base URL for the local backend served by uvicorn on port 8000.
const API_BASE = 'http://localhost:8000/api'

// Receipt summary returned by GET /api/receipts
export interface ReceiptSummary {
  id: number
  receipt_date: string
  store_name: string
  total_amount: number
  item_count: number
}

// Fetch the full receipt history list from the backend.
export async function fetchReceipts(): Promise<ReceiptSummary[]> {
  const res = await fetch(`${API_BASE}/receipts`)
  if (!res.ok) throw new Error('Could not load receipt history.')
  return res.json()
}

// Delete a single receipt by id. Throws if the server rejects the request.
export async function deleteReceipt(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/receipts/${id}`, { method: 'DELETE' })
  if (!res.ok && res.status !== 404) {
    throw new Error('Could not delete the receipt. Please try again.')
  }
}
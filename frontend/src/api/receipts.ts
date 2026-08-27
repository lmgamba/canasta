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

// A single line item on a receipt, as returned by POST /api/receipts/scan.
export interface Item {
  id: number
  receipt_id: number
  name: string
  quantity: number
  unit_price: number
  total_price: number
  category: string
}

// Full receipt detail, as returned by POST /api/receipts/scan.
export interface Receipt {
  id: number
  receipt_date: string
  store_name: string
  total_amount: number
  image_path: string | null
  created_at: string
  items: Item[]
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

// Upload a receipt image for Gemini extraction. On failure, throws with the
// backend's own error message (400 invalid file, 409 duplicate, 422
// unreadable receipt, 500 generic).
export async function scanReceipt(file: File): Promise<Receipt> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/receipts/scan`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(
      body?.detail ?? 'Something went wrong while scanning the receipt. Please try again.',
    )
  }

  return res.json()
}
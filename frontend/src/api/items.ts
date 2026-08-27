// API base URL for the local backend served by uvicorn on port 8000.
const API_BASE = 'http://localhost:8000/api'

// A single purchase of a product, from one receipt.
export interface ItemPurchase {
  receipt_date: string
  store_name: string
  quantity: number
  unit_price: number
  total_price: number
}

// Aggregate stats and full purchase history for a single product.
export interface ItemPurchaseHistory {
  normalized_name: string
  total_spend: number
  purchase_count: number
  purchases: ItemPurchase[]
}

// Thrown when the backend has no purchases for the given product name.
export class ItemNotFoundError extends Error {}

export async function fetchItemPurchases(name: string): Promise<ItemPurchaseHistory> {
  const res = await fetch(`${API_BASE}/items/purchases?name=${encodeURIComponent(name)}`)
  if (res.status === 404) throw new ItemNotFoundError('No purchases found for this product.')
  if (!res.ok) throw new Error('Could not load purchase history.')
  return res.json()
}

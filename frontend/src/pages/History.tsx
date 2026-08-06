import { useEffect, useState } from 'react'
import { deleteReceipt, fetchReceipts, type ReceiptSummary } from '../api/receipts'
import styles from './History.module.css'

function History() {
  const [receipts, setReceipts] = useState<ReceiptSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch the receipt list on mount. State is only updated after the async
  // call resolves — never synchronously inside the effect body.
  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const data = await fetchReceipts()
        if (!cancelled) {
          setReceipts(data)
          setError(null)
        }
      } catch {
        if (!cancelled) setError('Could not load receipt history.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  // Remove a receipt, then refresh the list from the server.
  const handleDelete = async (id: number) => {
    try {
      await deleteReceipt(id)
      const data = await fetchReceipts()
      setReceipts(data)
      setError(null)
    } catch {
      setError('Could not delete the receipt. Please try again.')
    }
  }

  // Format a gregorian date as a human-friendly string.
  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Format a price with two decimals and the local currency symbol.
  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'EUR',
    }).format(amount)
  }

  if (loading) return <p className={styles.status}>Loading receipts…</p>

  return (
    <section className={styles.history}>
      <h1 className={styles.title}>Receipt History</h1>

      {error && <p className={styles.error}>{error}</p>}

      {receipts.length === 0 ? (
        <p className={styles.empty}>No receipts scanned yet.</p>
      ) : (
        <ul className={styles.list}>
          {receipts.map((receipt) => (
            <li key={receipt.id} className={styles.row}>
              <div className={styles.meta}>
                <span className={styles.date}>{formatDate(receipt.receipt_date)}</span>
                <span className={styles.store}>{receipt.store_name}</span>
              </div>
              <div className={styles.stats}>
                <span className={styles.itemCount}>
                  {receipt.item_count} item{receipt.item_count === 1 ? '' : 's'}
                </span>
                <span className={styles.total}>{formatPrice(receipt.total_amount)}</span>
                <button
                  className={styles.deleteButton}
                  onClick={() => handleDelete(receipt.id)}
                  aria-label={`Delete receipt from ${receipt.store_name}`}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default History
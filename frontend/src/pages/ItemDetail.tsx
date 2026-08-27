import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchItemPurchases, ItemNotFoundError, type ItemPurchaseHistory } from '../api/items'
import styles from './ItemDetail.module.css'

function ItemDetail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const name = searchParams.get('name') ?? ''

  const [history, setHistory] = useState<ItemPurchaseHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const data = await fetchItemPurchases(name)
        if (!cancelled) {
          setHistory(data)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ItemNotFoundError
              ? 'No purchases found for this product.'
              : 'Could not load purchase history.',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [name])

  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'EUR',
    }).format(amount)
  }

  return (
    <section className={styles.itemDetail}>
      <button className={styles.backButton} onClick={() => navigate(-1)}>
        ← Back
      </button>

      {loading && <p className={styles.status}>Loading purchase history…</p>}
      {!loading && error && <p className={styles.error}>{error}</p>}

      {!loading && !error && history && (
        <>
          <div className={styles.header}>
            <h1 className={styles.title}>{history.normalized_name}</h1>
            <div className={styles.stats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Total spend</span>
                <span className={styles.statValue}>{formatPrice(history.total_spend)}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Purchases</span>
                <span className={styles.statValue}>{history.purchase_count}</span>
              </div>
            </div>
          </div>

          <table className={styles.table}>
            <thead>
              <tr>
                <th>Date</th>
                <th>Store</th>
                <th>Quantity</th>
                <th>Unit price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {history.purchases.map((purchase, index) => (
                <tr key={index}>
                  <td>{formatDate(purchase.receipt_date)}</td>
                  <td>{purchase.store_name}</td>
                  <td>{purchase.quantity}</td>
                  <td>{formatPrice(purchase.unit_price)}</td>
                  <td>{formatPrice(purchase.total_price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  )
}

export default ItemDetail

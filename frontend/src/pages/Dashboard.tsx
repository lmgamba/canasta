import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  fetchSpendingByCategory,
  fetchSpendingOverTime,
  fetchTopItems,
  type SpendingByCategoryItem,
  type SpendingOverTimeItem,
  type SpendingPeriod,
  type TopItem,
} from '../api/analytics'
import styles from './Dashboard.module.css'

const TOOLTIP_STYLE = {
  background: 'var(--bg-deepest)',
  border: '1px solid var(--bg-hover)',
  borderRadius: 'var(--radius)',
  color: 'var(--text-primary)',
}

function Dashboard() {
  const [period, setPeriod] = useState<SpendingPeriod>('weekly')
  const [spendingOverTime, setSpendingOverTime] = useState<SpendingOverTimeItem[]>([])
  const [spendingByCategory, setSpendingByCategory] = useState<SpendingByCategoryItem[]>([])
  const [topItems, setTopItems] = useState<TopItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Category breakdown and top items don't depend on the period toggle —
  // fetch them once on mount, in parallel with the initial weekly series.
  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const [byCategory, top] = await Promise.all([fetchSpendingByCategory(), fetchTopItems()])
        if (!cancelled) {
          setSpendingByCategory(byCategory)
          setTopItems(top)
        }
      } catch {
        if (!cancelled) setError('Could not load dashboard data.')
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  // Spending over time re-fetches whenever the weekly/monthly toggle changes.
  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const overTime = await fetchSpendingOverTime(period)
        if (!cancelled) {
          setSpendingOverTime(overTime)
          setError(null)
        }
      } catch {
        if (!cancelled) setError('Could not load dashboard data.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [period])

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'EUR',
    }).format(amount)
  }

  if (loading) return <p className={styles.status}>Loading dashboard…</p>

  return (
    <section className={styles.dashboard}>
      <h1 className={styles.title}>Dashboard</h1>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <span className={styles.cardTitle}>Spending over time</span>
          <div className={styles.periodToggle}>
            <button
              className={
                period === 'weekly'
                  ? `${styles.periodButton} ${styles.periodActive}`
                  : styles.periodButton
              }
              onClick={() => setPeriod('weekly')}
            >
              Weekly
            </button>
            <button
              className={
                period === 'monthly'
                  ? `${styles.periodButton} ${styles.periodActive}`
                  : styles.periodButton
              }
              onClick={() => setPeriod('monthly')}
            >
              Monthly
            </button>
          </div>
        </div>
        {spendingOverTime.length === 0 ? (
          <p className={styles.cardEmpty}>
            No receipts yet — scan your first receipt to see your spending patterns.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={spendingOverTime}>
              <CartesianGrid stroke="var(--bg-hover)" strokeDasharray="3 3" />
              <XAxis dataKey="period_label" stroke="var(--text-secondary)" fontSize={12} />
              <YAxis stroke="var(--text-secondary)" fontSize={12} />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value) => formatPrice(Number(value))}
              />
              <Line
                type="monotone"
                dataKey="total_amount"
                stroke="var(--accent)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <span className={styles.cardTitle}>Spending by category</span>
        </div>
        {spendingByCategory.length === 0 ? (
          <p className={styles.cardEmpty}>No category spending yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={Math.max(260, spendingByCategory.length * 36)}>
            <BarChart data={spendingByCategory} layout="vertical">
              <CartesianGrid stroke="var(--bg-hover)" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" stroke="var(--text-secondary)" fontSize={12} />
              <YAxis
                dataKey="category"
                type="category"
                stroke="var(--text-secondary)"
                fontSize={12}
                width={120}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value) => formatPrice(Number(value))}
              />
              <Bar dataKey="total_amount" fill="var(--accent)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <span className={styles.cardTitle}>Top items</span>
        </div>
        {topItems.length === 0 ? (
          <p className={styles.cardEmpty}>No items yet.</p>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Product</th>
                <th>Total spend</th>
                <th>Purchases</th>
              </tr>
            </thead>
            <tbody>
              {topItems.map((item) => (
                <tr key={item.normalized_name}>
                  <td>
                    <Link
                      className={styles.itemLink}
                      to={`/items/detail?name=${encodeURIComponent(item.normalized_name)}`}
                    >
                      {item.normalized_name}
                    </Link>
                  </td>
                  <td>{formatPrice(item.total_spend)}</td>
                  <td>{item.purchase_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}

export default Dashboard

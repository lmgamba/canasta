import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { scanReceipt, type Receipt } from '../api/receipts'
import { getRateLimitWarning, recordScanAttempt } from '../lib/geminiRateLimit'
import styles from './Upload.module.css'

type Status = 'idle' | 'uploading' | 'success' | 'error'

const VALID_TYPES = ['image/jpeg', 'image/png']
const MAX_FILE_SIZE = 5 * 1024 * 1024 // matches backend/main.py's MAX_FILE_SIZE

function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<Receipt | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  // Lazy initializer — reads localStorage once on mount, no effect needed.
  const [warning, setWarning] = useState<string | null>(() => getRateLimitWarning())
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Revoke the preview's object URL when it's replaced or the page unmounts.
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const chooseFile = (selected: File) => {
    if (!VALID_TYPES.includes(selected.type)) {
      setErrorMessage('Invalid file type. Please upload a JPEG or PNG image.')
      setStatus('error')
      return
    }
    if (selected.size > MAX_FILE_SIZE) {
      setErrorMessage('Image file is too large. Maximum size is 5 MB.')
      setStatus('error')
      return
    }
    setFile(selected)
    setPreviewUrl(URL.createObjectURL(selected))
    setErrorMessage(null)
    setStatus('idle')
  }

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0]
    if (selected) chooseFile(selected)
    event.target.value = ''
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const dropped = event.dataTransfer.files?.[0]
    if (dropped) chooseFile(dropped)
  }

  const handleSubmit = async () => {
    if (!file) return
    setStatus('uploading')
    recordScanAttempt()
    try {
      const receipt = await scanReceipt(file)
      setResult(receipt)
      setStatus('success')
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong.')
      setStatus('error')
    } finally {
      setWarning(getRateLimitWarning())
    }
  }

  const handleReset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setFile(null)
    setPreviewUrl(null)
    setResult(null)
    setErrorMessage(null)
    setStatus('idle')
  }

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'EUR',
    }).format(amount)
  }

  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <section className={styles.upload}>
      <h1 className={styles.title}>Upload</h1>

      {warning && <p className={styles.warning}>{warning}</p>}

      {status === 'uploading' && <p className={styles.status}>Reading your receipt…</p>}

      {status === 'error' && (
        <div>
          <p className={styles.error}>{errorMessage}</p>
          <div className={styles.actions}>
            <button className={styles.primaryButton} onClick={handleReset}>
              Try again
            </button>
          </div>
        </div>
      )}

      {status === 'success' && result && (
        <div className={styles.successCard}>
          <div className={styles.successHeader}>
            <span className={styles.storeName}>{result.store_name}</span>
            <span className={styles.total}>{formatPrice(result.total_amount)}</span>
          </div>
          <p className={styles.receiptDate}>{formatDate(result.receipt_date)}</p>

          <ul className={styles.itemList}>
            {result.items.map((item) => (
              <li key={item.id} className={styles.itemRow}>
                <span className={styles.itemName}>{item.name}</span>
                <span className={styles.itemMeta}>
                  <span className={styles.itemCategory}>{item.category}</span>
                  <span className={styles.itemPrice}>{formatPrice(item.total_price)}</span>
                </span>
              </li>
            ))}
          </ul>

          <div className={styles.actions}>
            <button className={styles.secondaryButton} onClick={handleReset}>
              Scan another
            </button>
          </div>
          <div className={styles.links}>
            <Link className={styles.link} to="/history">
              View in History
            </Link>
            <Link className={styles.link} to="/dashboard">
              View Dashboard
            </Link>
          </div>
        </div>
      )}

      {status === 'idle' && !previewUrl && (
        <div
          className={isDragging ? `${styles.dropZone} ${styles.dropZoneActive}` : styles.dropZone}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(event) => {
            event.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <p className={styles.dropZoneText}>Drop a receipt photo here, or click to choose one</p>
          <p className={styles.dropZoneHint}>JPEG or PNG, up to 5 MB</p>
          <input
            ref={fileInputRef}
            className={styles.fileInput}
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileInputChange}
          />
        </div>
      )}

      {status === 'idle' && previewUrl && (
        <div className={styles.previewCard}>
          <img className={styles.previewImage} src={previewUrl} alt="Receipt preview" />
          <div className={styles.actions}>
            <button className={styles.secondaryButton} onClick={handleReset}>
              Choose different file
            </button>
            <button className={styles.primaryButton} onClick={handleSubmit}>
              Scan receipt
            </button>
          </div>
        </div>
      )}
    </section>
  )
}

export default Upload

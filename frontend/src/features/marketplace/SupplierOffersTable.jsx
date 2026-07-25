import { useState } from 'react'
import Card from '../../components/ui/Card.jsx'
import Badge from '../../components/ui/Badge.jsx'
import Button from '../../components/ui/Button.jsx'
import { useAppState } from '../../context/useAppState.js'
import { checkout } from '../../api/client.js'
import { formatCurrencyBDT } from '../../lib/formatters.js'

export default function SupplierOffersTable({ offers }) {
  const { state } = useAppState()
  const [buyingIndex, setBuyingIndex] = useState(null)
  const [phone, setPhone] = useState(state.farmerProfile.phoneNumber || '')
  const [loading, setLoading] = useState(false)
  const [receipt, setReceipt] = useState(null)
  const [error, setError] = useState(null)

  if (!offers || offers.offers.length === 0) return null

  const startBuy = (index) => {
    setBuyingIndex(index)
    setReceipt(null)
    setError(null)
  }

  const confirmBuy = async (offer) => {
    if (!phone.trim()) {
      setError('Enter a phone number (this is the sandbox "Mobile Account" being charged).')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const amount = offer.estimatedTotalCostBDT ?? offer.pricePerUnit
      const result = await checkout({
        subscriberId: phone.trim(),
        amount,
        purpose: `${offers.item} from ${offer.supplierName} (${offer.district})`,
        sessionId: state.currentSessionId,
      })
      setReceipt({ ...result, supplierName: offer.supplierName, amount })
      setBuyingIndex(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-stone-700">
          Suppliers for {offers.item} ({offers.unit})
        </h4>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="border-b border-earth-100 text-left text-stone-500">
              <th className="py-2 pr-2 font-medium">Supplier</th>
              <th className="py-2 pr-2 font-medium">District</th>
              <th className="py-2 pr-2 text-right font-medium">Price</th>
              <th className="py-2 pr-2 text-right font-medium">Delivery</th>
              <th className="py-2 pr-2 text-right font-medium">Distance</th>
              <th className="py-2 pr-2 text-right font-medium">Rating</th>
              <th className="py-2 pr-2 text-right font-medium">Est. Total</th>
              <th className="py-2 pl-2" />
            </tr>
          </thead>
          <tbody>
            {offers.offers.map((o, i) => (
              <tr key={`${o.supplierName}_${i}`} className="border-b border-earth-100/60 align-top">
                <td className="py-2 pr-2 text-stone-800">
                  <div className="flex items-center gap-2">
                    {o.supplierName}
                    {i === 0 && <Badge variant="success">Best match</Badge>}
                  </div>
                </td>
                <td className="py-2 pr-2 text-stone-600">{o.district}</td>
                <td className="py-2 pr-2 text-right text-stone-800">
                  {formatCurrencyBDT(o.pricePerUnit)}/{o.unit}
                </td>
                <td className="py-2 pr-2 text-right text-stone-600">{o.deliveryDays}d</td>
                <td className="py-2 pr-2 text-right text-stone-600">{o.distanceKm.toFixed(0)}km</td>
                <td className="py-2 pr-2 text-right text-stone-600">{o.rating.toFixed(1)}/5</td>
                <td className="py-2 pr-2 text-right text-stone-800">
                  {o.estimatedTotalCostBDT != null ? formatCurrencyBDT(o.estimatedTotalCostBDT) : '—'}
                </td>
                <td className="py-2 pl-2 text-right">
                  <Button size="sm" variant="secondary" onClick={() => startBuy(i)}>
                    Buy Now
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {offers.rankingMethod && <p className="text-xs text-stone-400">{offers.rankingMethod}</p>}
      {offers.source && <p className="text-xs text-stone-400">{offers.source}</p>}
      {offers.distanceNote && <p className="text-xs text-stone-400">{offers.distanceNote}</p>}

      {buyingIndex != null && (
        <div className="flex flex-col gap-2 rounded-lg border border-earth-100 bg-wheat-100 p-3">
          <p className="text-sm font-medium text-stone-700">
            Confirm purchase from {offers.offers[buyingIndex].supplierName} —{' '}
            {formatCurrencyBDT(offers.offers[buyingIndex].estimatedTotalCostBDT ?? offers.offers[buyingIndex].pricePerUnit)}
          </p>
          <p className="text-xs text-stone-500">
            Charged via bdapps CaaS (sandbox/simulator) Direct Debit against this Mobile Account number.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="tel:8801XXXXXXXXX"
              className="min-w-[200px] flex-1 rounded-lg border border-earth-100 bg-wheat-50 px-3 py-2 text-sm text-stone-800 outline-none focus:border-leaf-400"
            />
            <Button variant="primary" onClick={() => confirmBuy(offers.offers[buyingIndex])} disabled={loading}>
              {loading ? 'Processing…' : 'Confirm Purchase'}
            </Button>
            <Button variant="ghost" onClick={() => setBuyingIndex(null)} disabled={loading}>
              Cancel
            </Button>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
        </div>
      )}

      {receipt && (
        <div
          className={`flex flex-col gap-1 rounded-lg border p-3 text-sm ${
            receipt.success ? 'border-leaf-200 bg-leaf-50 text-leaf-800' : 'border-red-200 bg-red-50 text-red-700'
          }`}
        >
          <p className="font-semibold">
            {receipt.success ? 'Payment successful' : `Payment failed (${receipt.statusCode})`}
          </p>
          <p>{receipt.statusDetail}</p>
          {receipt.success && (
            <>
              <p>Amount: {formatCurrencyBDT(receipt.amount)}</p>
              <p>Transaction ID: {receipt.externalTrxId}</p>
              {receipt.referenceId && <p>Reference ID: {receipt.referenceId}</p>}
              {receipt.newBalanceBDT != null && <p>New Mobile Account balance: {formatCurrencyBDT(receipt.newBalanceBDT)}</p>}
            </>
          )}
        </div>
      )}
    </Card>
  )
}

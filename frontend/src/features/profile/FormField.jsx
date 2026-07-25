export default function FormField({ label, children }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-stone-600">{label}</span>
      {children}
    </label>
  )
}

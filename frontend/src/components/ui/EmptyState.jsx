export default function EmptyState({ title, description, icon }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-1 px-6 py-10 text-center">
      {icon && <div className="mb-2 text-3xl">{icon}</div>}
      <p className="text-sm font-medium text-stone-600">{title}</p>
      {description && <p className="text-xs text-stone-400">{description}</p>}
    </div>
  )
}

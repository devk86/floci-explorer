export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <svg width={compact ? 22 : 26} height={compact ? 22 : 26} viewBox="0 0 32 32" aria-hidden>
        <rect width="32" height="32" rx="7" fill="#0b1117" stroke="#ff9900" strokeWidth="1.5" />
        <path fill="#ff9900" d="M7 7h13.5L16 14h7L12.5 26l3.2-8.5H7z" />
      </svg>
      {compact ? null : (
        <div className="text-[13px] font-semibold tracking-[0.14em]">FLOCI EXPLORER</div>
      )}
    </div>
  )
}

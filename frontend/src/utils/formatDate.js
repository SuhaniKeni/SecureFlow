/**
 * Safe, cross-browser local 12-hour date formatter for audit timestamps.
 * Output Format Example: "Aug 21, 2026, 2:11 PM"
 */
export function formatTimestamp(ts) {
  if (!ts) return 'N/A';
  try {
    const cleanTs = typeof ts === 'string' ? ts.replace(' ', 'T') : ts;
    const date = new Date(cleanTs);
    if (isNaN(date.getTime())) return 'N/A';

    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  } catch (err) {
    return 'N/A';
  }
}

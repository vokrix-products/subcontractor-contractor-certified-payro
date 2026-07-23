import { TriangleAlert, CircleCheckBig, Clock } from 'lucide-react'
import { SubcontractorPayroll } from './types'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<
  Severity,
  'destructive' | 'warning' | 'success' | 'secondary'
> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// PRODUCT_CUSTOMIZE: replace this list with the real statuses this product
// produces (must match exactly what the backend poller writes to
// records.status). Every status must declare a severity tier above. Default
// values below are generic placeholders only — do not ship as-is.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Ready For Submission', value: 'ready_for_submission', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Needs Review', value: 'needs_review', icon: Clock, severity: 'warning' as Severity },
  { label: 'Error', value: 'error', icon: TriangleAlert, severity: 'critical' as Severity },
]
// __STATUSES_BLOCK_END__


export const payrollData: SubcontractorPayroll[] = [
  {
    id: "1",
    subcontractor: "ABC Concrete Inc.",
    project: "Highway 101 Overpass",
    periodStart: "2023-05-01",
    periodEnd: "2023-05-15",
    workerName: "John Doe",
    craft: "Laborer",
    hours: 40,
    rate: 35.50,
    total: 1420.00,
    certified: true,
  },
  {
    id: "2",
    subcontractor: "ABC Concrete Inc.",
    project: "Highway 101 Overpass",
    periodStart: "2023-05-01",
    periodEnd: "2023-05-15",
    workerName: "Jane Smith",
    craft: "Carpenter",
    hours: 32,
    rate: 45.00,
    total: 1440.00,
    certified: true,
  },
  {
    id: "3",
    subcontractor: "XYZ Electric",
    project: "City Hall Renovation",
    periodStart: "2023-06-01",
    periodEnd: "2023-06-15",
    workerName: "Mike Johnson",
    craft: "Electrician",
    hours: 40,
    rate: 55.00,
    total: 2200.00,
    certified: false,
  },
];

export default payrollData;

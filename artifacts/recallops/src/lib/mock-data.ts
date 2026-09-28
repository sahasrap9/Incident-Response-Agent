export type IncidentStatus = 'Investigating' | 'Resolved' | 'Monitoring' | 'Open';
export type IncidentSeverity = 'Critical' | 'High' | 'Medium' | 'Low';

export type Incident = {
  id: string;
  title: string;
  service: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  errorMessage: string;
  timestamp: string;
  rootCause: string;
  suggestedFix: string;
  duration: string;
  memoryMatch: string;
  similarity: number;
  relatedIncidentIds: string[];
  owner: string;
  tags: string[];
};

export const incidents: Incident[] = [
  {
    id: 'INC-2481',
    title: 'Checkout API elevated 5xx responses',
    service: 'checkout-api',
    severity: 'Critical',
    status: 'Investigating',
    errorMessage: 'upstream connect error or disconnect/reset before headers. reset reason: connection termination',
    timestamp: '2024-06-18T14:32:00Z',
    rootCause: 'A connection pool change in the payment gateway client exhausted available sockets during a traffic spike.',
    suggestedFix: 'Roll back gateway-client 4.8.1, increase the upstream idle pool to 64, and replay failed checkout requests from the dead-letter queue.',
    duration: '18m',
    memoryMatch: 'INC-2034 · checkout gateway timeout',
    similarity: 94,
    relatedIncidentIds: ['INC-2034', 'INC-1968'],
    owner: 'Maya Chen',
    tags: ['payments', 'gateway', 'production'],
  },
  {
    id: 'INC-2476',
    title: 'Search indexing lag above SLO',
    service: 'indexer-worker',
    severity: 'High',
    status: 'Resolved',
    errorMessage: 'BulkIndexError: rejected execution of coordinating operation; queue capacity = 1000',
    timestamp: '2024-06-18T11:08:00Z',
    rootCause: 'A shard relocation created uneven write pressure while the worker concurrency flag was still set for the old cluster size.',
    suggestedFix: 'Pause shard relocation, drain the backlog at concurrency 12, then cap bulk payloads at 5 MB.',
    duration: '42m',
    memoryMatch: 'INC-2312 · elasticsearch write queue saturation',
    similarity: 88,
    relatedIncidentIds: ['INC-2312', 'INC-2194'],
    owner: 'Jon Bell',
    tags: ['search', 'elasticsearch'],
  },
  {
    id: 'INC-2469',
    title: 'Auth token refresh failures in EU',
    service: 'identity-edge',
    severity: 'High',
    status: 'Monitoring',
    errorMessage: 'JWTValidationError: key id eu-2024-06 not found in local JWKS cache',
    timestamp: '2024-06-17T19:44:00Z',
    rootCause: 'The EU key rotation event arrived before cache invalidation completed on two edge clusters.',
    suggestedFix: 'Invalidate the regional JWKS cache and lower the refresh TTL to 90 seconds until the rotation completes.',
    duration: '27m',
    memoryMatch: 'INC-1887 · stale signing key cache',
    similarity: 91,
    relatedIncidentIds: ['INC-1887'],
    owner: 'Priya Raman',
    tags: ['identity', 'eu-west-1'],
  },
  {
    id: 'INC-2458',
    title: 'Notification delivery latency',
    service: 'notify-dispatch',
    severity: 'Medium',
    status: 'Resolved',
    errorMessage: 'KafkaConsumerGroup: rebalance in progress for 312s; consumer heartbeat timed out',
    timestamp: '2024-06-16T09:15:00Z',
    rootCause: 'A noisy neighbor saturated CPU on the dispatch node, causing consumer heartbeats to miss their interval.',
    suggestedFix: 'Move the consumer group to the reserved node pool and increase session.timeout.ms to 45 seconds.',
    duration: '31m',
    memoryMatch: 'INC-2241 · dispatch consumer rebalance',
    similarity: 82,
    relatedIncidentIds: ['INC-2241', 'INC-2031'],
    owner: 'Elena Ortiz',
    tags: ['notifications', 'kafka'],
  },
  {
    id: 'INC-2447',
    title: 'Read replica replication delay',
    service: 'orders-db',
    severity: 'Low',
    status: 'Resolved',
    errorMessage: 'replica lag 00:04:18 exceeded alert threshold of 00:02:00',
    timestamp: '2024-06-15T17:02:00Z',
    rootCause: 'An analytics query held a long-running transaction on the primary during the nightly report window.',
    suggestedFix: 'Terminate the report transaction, add an index for the daily aggregation, and route analytics to the warehouse.',
    duration: '12m',
    memoryMatch: 'INC-1982 · reporting transaction lock',
    similarity: 76,
    relatedIncidentIds: ['INC-1982'],
    owner: 'Theo Grant',
    tags: ['database', 'replication'],
  },
  {
    id: 'INC-2439',
    title: 'Webhook signature mismatch spike',
    service: 'integrations-api',
    severity: 'Medium',
    status: 'Resolved',
    errorMessage: 'SignatureVerificationError: expected v1=8f7a… got v1=2cb0…',
    timestamp: '2024-06-15T13:28:00Z',
    rootCause: 'The signing secret was rotated in the provider console but not propagated to the integration worker.',
    suggestedFix: 'Sync the provider secret, replay rejected webhook deliveries, and add a dual-secret rotation window.',
    duration: '22m',
    memoryMatch: 'INC-2106 · webhook secret rotation',
    similarity: 86,
    relatedIncidentIds: ['INC-2106', 'INC-1762'],
    owner: 'Maya Chen',
    tags: ['webhooks', 'integrations'],
  },
];

export const activity = [
  { action: 'Analysis completed', detail: 'Checkout API · INC-2481', time: '4 min ago', tone: 'blue' },
  { action: 'Memory confirmed', detail: 'INC-2476 matched INC-2312', time: '18 min ago', tone: 'purple' },
  { action: 'Incident resolved', detail: 'Read replica replication delay', time: '1 hr ago', tone: 'green' },
  { action: 'New log source connected', detail: 'production / eu-west-1', time: '2 hrs ago', tone: 'slate' },
];

export const serviceOptions = ['All services', 'checkout-api', 'indexer-worker', 'identity-edge', 'notify-dispatch', 'orders-db', 'integrations-api'];
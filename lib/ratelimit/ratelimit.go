package ratelimit

import (
	"time"
)

type Ratelimit struct {
	rate int16
	per  int64
	rc   int16
	tf   int64
	lc   int64
}

func newRatelimit(r int16, p int64) Ratelimit {
	return Ratelimit{rate: r, per: p, rc: r, tf: 0, lc: 0}
}

func (r *Ratelimit) isStale(ct int64) bool {
	return ct > r.tf+r.per
}

func (r *Ratelimit) remainingCalls(ct int64) int16 {
	if r.isStale(ct) {
		return r.rate
	}

	return r.rc
}

func (r *Ratelimit) updateCalls() bool {
	r.lc = time.Now().UnixMilli()
	r.rc = r.remainingCalls(r.lc)

	if r.rc == r.rate {
		r.tf = r.lc
	}

	if r.rc == 0 {
		return true
	}

	r.rc--
	return false
}

package ratelimit

import "time"

type RatelimitManager struct {
	Rate  int16
	Per   int64
	c     uint8
	rlMap map[string]*Ratelimit
}

func NewRatelimitManager(r int16, p int64) *RatelimitManager {
	return &RatelimitManager{Rate: r, Per: p, c: 0, rlMap: make(map[string]*Ratelimit)}
}

func (rm *RatelimitManager) cleanseMapping() {
	ct := time.Now().UnixMilli()
	stale := []*string{}
	for id, rl := range rm.rlMap {
		if rl.isStale(ct) {
			stale = append(stale, &id)
		}
	}
	for _, id := range stale {
		delete(rm.rlMap, *id)
	}
}

func (rm *RatelimitManager) intervalCleanse() {
	if rm.c == 255 {
		rm.cleanseMapping()
		rm.c = 0
	}
	rm.c++
}

func (rm *RatelimitManager) IsRatelimited(id string) bool {
	defer rm.intervalCleanse()

	rl, ok := rm.rlMap[id]
	if ok {
		return rl.updateCalls()
	}

	newRl := newRatelimit(rm.Rate, rm.Per)
	rm.rlMap[id] = &newRl

	return newRl.updateCalls()
}

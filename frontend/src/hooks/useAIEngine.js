import { useMemo } from 'react';

const EVENT_WEIGHTS = {
  tab_switch:          15,
  multiple_face:       30,
  face_missing:        20,
  head_down:           10,
  looking_away:         8,
  phone_detected:      35,
  blocked_website:     40,
  usb_connected:       20,
  copy_paste:          10,
  idle:                 5,
  typing:              -5,
  coding:              -5,
  normal:              -5,
  marked_suspicious:   80,
  marked_safe:         -80,
};

const SEVERITY_WEIGHTS = {
  CRITICAL: 40,
  HIGH:     25,
  MEDIUM:   15,
  WARNING:  15,
  LOW:       5,
  INFO:      2,
};

export const useAIEngine = (arg1, arg2, arg3) => {
  // Support both object destructuring and positional arguments
  const { computers, activities, alerts, students } = useMemo(() => {
    let comps = [];
    let acts = [];
    let alts = [];
    let studs = [];

    if (arg1 && typeof arg1 === 'object' && !Array.isArray(arg1)) {
      comps = arg1.computers || [];
      acts = arg1.activities || [];
      alts = arg1.alerts || [];
      studs = arg1.students || [];
    } else {
      comps = arg1 || [];
      acts = arg2 || [];
      alts = arg3 || [];
    }

    return {
      computers: Array.isArray(comps) ? comps : [],
      activities: Array.isArray(acts) ? acts : [],
      alerts: Array.isArray(alts) ? alts : [],
      students: Array.isArray(studs) ? studs : []
    };
  }, [arg1, arg2, arg3]);

  // Build mapping from student_id/name to computer index
  const studentToPC = useMemo(() => {
    const map = {};
    (students || []).forEach((s, i) => {
      if (s && s.id) {
        map[s.id] = i;
        if (s.name) {
          map[s.name.toLowerCase()] = i;
        }
      }
    });
    return map;
  }, [students]);

  // Compute Risk Scores per PC
  const riskScores = useMemo(() => {
    const scores = {};

    // Initialize baselines
    (computers || []).forEach(pc => {
      if (pc && pc.id) {
        let base = 0;
        if (pc.status === 'Suspicious') base = 45;
        else if (pc.status === 'Idle')   base = 15;
        else if (pc.status === 'Online') base = 5;
        scores[pc.id] = { score: base, events: [] };
      }
    });

    // Apply alerts weights
    (alerts || []).forEach(alert => {
      if (!alert) return;
      let pcId = null;
      if (alert.student_id && studentToPC[alert.student_id] !== undefined) {
        pcId = studentToPC[alert.student_id] + 1;
      } else if (alert.student_name && studentToPC[alert.student_name.toLowerCase()] !== undefined) {
        pcId = studentToPC[alert.student_name.toLowerCase()] + 1;
      }

      if (pcId && scores[pcId]) {
        const sev = (alert.severity || '').toUpperCase();
        const weight = SEVERITY_WEIGHTS[sev] || 5;
        scores[pcId].score += weight;
        scores[pcId].events.push({ type: 'alert', label: alert.alert_type, weight });
      }
    });

    // Apply activities weights
    (activities || []).forEach(act => {
      if (!act) return;
      let pcId = null;
      if (act.student_id && studentToPC[act.student_id] !== undefined) {
        pcId = studentToPC[act.student_id] + 1;
      } else if (act.student_name && studentToPC[act.student_name.toLowerCase()] !== undefined) {
        pcId = studentToPC[act.student_name.toLowerCase()] + 1;
      }

      if (pcId && scores[pcId]) {
        const type = (act.activity_type || '').toLowerCase();
        const weight = Object.entries(EVENT_WEIGHTS).find(([k]) => type.includes(k))?.[1] ?? 3;
        const conf = act.confidence ?? 1;
        const weighted = Math.round(weight * conf);
        scores[pcId].score += weighted;
        scores[pcId].events.push({ type: 'activity', label: act.activity_type, weight: weighted });
      }
    });

    // Clamp risk scores between 0 and 100
    Object.keys(scores).forEach(id => {
      scores[id].score = Math.max(0, Math.min(100, scores[id].score || 0));
    });

    return scores;
  }, [computers, activities, alerts, studentToPC]);

  // Compute AI insights
  const insights = useMemo(() => {
    const msgs = [];
    const critical = (computers || []).filter(pc => pc && (riskScores[pc.id]?.score ?? 0) >= 71);
    const warning  = (computers || []).filter(pc => {
      if (!pc) return false;
      const s = riskScores[pc.id]?.score ?? 0;
      return s >= 31 && s < 71;
    });
    const idle     = (computers || []).filter(pc => pc && pc.status === 'Idle');

    critical.forEach(pc => {
      msgs.push({
        level: 'critical',
        pc: pc.number,
        text: `${pc.number} (${pc.student || 'Unassigned'}) is likely attempting to access restricted content — score ${riskScores[pc.id]?.score || 0}.`
      });
    });

    warning.forEach(pc => {
      const ev = riskScores[pc.id]?.events ?? [];
      const tabSwitches = ev.filter(e => e?.label?.toLowerCase().includes('tab')).length;
      if (tabSwitches >= 2) {
        msgs.push({
          level: 'warning',
          pc: pc.number,
          text: `${pc.number} has repeated tab switching (${tabSwitches} events recorded).`
        });
      } else {
        msgs.push({
          level: 'warning',
          pc: pc.number,
          text: `${pc.number} (${pc.student || 'Unknown'}) shows elevated risk — monitoring closely.`
        });
      }
    });

    idle.slice(0, 2).forEach(pc => {
      msgs.push({
        level: 'info',
        pc: pc.number,
        text: `${pc.number} appears idle for an unusually long duration.`
      });
    });

    if ((alerts || []).length > 3) {
      msgs.push({
        level: 'critical',
        pc: null,
        text: `${alerts.length} suspicious events detected. Immediate review recommended.`
      });
    }

    const suspiciousCount = (computers || []).filter(pc => pc && pc.status === 'Suspicious').length;
    if (suspiciousCount > 0) {
      msgs.push({
        level: 'warning',
        pc: null,
        text: `${suspiciousCount} workstation${suspiciousCount > 1 ? 's are' : ' is'} currently flagged as suspicious by AI monitoring.`
      });
    }

    if (msgs.length === 0) {
      msgs.push({
        level: 'safe',
        pc: null,
        text: 'All systems behaving normally. No anomalies detected by AI engine.'
      });
    }

    return msgs.slice(0, 6);
  }, [computers, riskScores, alerts]);

  // Compute Summary Statistics
  const summary = useMemo(() => {
    const scores = (computers || []).map(pc => pc ? (riskScores[pc.id]?.score ?? 0) : 0);
    const avg = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    const criticalCount = scores.filter(s => s >= 71).length;
    const warningCount  = scores.filter(s => s >= 31 && s < 71).length;
    const criticalAlerts = (alerts || []).filter(a => a && (a.severity || '').toUpperCase() === 'CRITICAL').length;

    let overallRisk = 'Low';
    if (avg >= 71) overallRisk = 'Critical';
    else if (avg >= 51) overallRisk = 'High';
    else if (avg >= 31) overallRisk = 'Medium';

    return {
      monitored:        (computers || []).filter(pc => pc && pc.status !== 'Offline').length,
      suspicious:       criticalCount + warningCount,
      criticalAlerts,
      blockedAttempts:  (alerts || []).filter(a => a && ((a.alert_type || '').toLowerCase().includes('block') || (a.alert_type || '').toLowerCase().includes('website'))).length,
      overallRisk,
      avgScore:         Math.round(avg),
    };
  }, [computers, riskScores, alerts]);

  return {
    riskScores: riskScores || {},
    insights: insights || [],
    aiInsights: insights || [],
    summary: summary || { monitored: 0, suspicious: 0, criticalAlerts: 0, blockedAttempts: 0, overallRisk: 'Low', avgScore: 0 },
    overallRisk: summary?.overallRisk || 'Low'
  };
};

export default useAIEngine;

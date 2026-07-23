import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Plays a clean, premium chime sound using Web Audio API before voice announcements.
 */
const playChime = (volume = 0.8) => {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();

    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc1.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5

    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(440, ctx.currentTime); // A4
    osc2.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.15); // E5

    gain.gain.setValueAtTime(volume * 0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);

    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);

    osc1.start();
    osc2.start();
    osc1.stop(ctx.currentTime + 0.5);
    osc2.stop(ctx.currentTime + 0.5);
  } catch (err) {
    console.error('[VoiceAlerts] Failed to play chime:', err);
  }
};

/**
 * Maps event templates to custom voice warning messages.
 */
const getSpeechText = (evt) => {
  if (!evt) return '';

  const formatPcName = (name) => {
    if (!name) return 'workstation';
    const num = parseInt(name.replace('PC-', '').replace('PC_', ''), 10);
    if (isNaN(num)) return name;
    const digits = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 
                    'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen', 'Twenty'];
    if (num <= 20) {
      return `PC Zero ${digits[num]}`;
    }
    return `PC ${num}`;
  };

  const formattedPc = formatPcName(evt.computer_id || evt.computerId);
  const type = (evt.activity_type || evt.alert_type || evt.event || '').toLowerCase();
  const student = evt.student_name || evt.student || '';

  // Blocked website events
  if (type.includes('blocked_website') || type.includes('restricted')) {
    let domain = '';
    if (evt.active_website && evt.active_website !== 'None') {
      domain = evt.active_website;
    } else if (type.includes('blocked_website:')) {
      domain = evt.activity_type.split(':')[1] || '';
    } else if (evt.message && evt.message.toLowerCase().includes('access:')) {
      domain = evt.message.split(/access:/i)[1] || '';
    } else if (evt.message && evt.message.toLowerCase().includes('accessed:')) {
      domain = evt.message.split(/accessed:/i)[1] || '';
    }

    let domainName = domain.split('.')[0] || 'blocked';
    domainName = domainName.trim();
    domainName = domainName.charAt(0).toUpperCase() + domainName.slice(1);

    if (student) {
      return `Warning. Restricted website ${domainName} has been accessed on ${formattedPc} by student ${student}.`;
    }
    return `Warning. Restricted website ${domainName} has been accessed on ${formattedPc}.`;
  }

  if (type.includes('copy_paste') || type.includes('clipboard') || type.includes('copy') || type.includes('paste')) {
    return `Warning. Copy paste activity detected on ${formattedPc}.`;
  }

  if (type.includes('face') || type.includes('multiple_face')) {
    return `Alert. Multiple faces detected on ${formattedPc}.`;
  }

  if (type.includes('phone') || type.includes('mobile')) {
    return `Warning. Mobile phone detected on ${formattedPc}.`;
  }

  if (type.includes('usb') || type.includes('drive')) {
    return `Security Alert. USB device connected on ${formattedPc}.`;
  }

  if (type.includes('tab_switch') || type.includes('tab')) {
    return `Warning. Browser tab switching detected on ${formattedPc}.`;
  }

  if (type.includes('offline')) {
    return `Attention. ${formattedPc} has gone offline.`;
  }

  if (type.includes('online')) {
    return `${formattedPc} is now online.`;
  }

  if (type.includes('cpu') || type.includes('high_cpu')) {
    return `Warning. CPU usage has exceeded the safe limit on ${formattedPc}.`;
  }

  if (type.includes('ram') || type.includes('high_ram') || type.includes('memory')) {
    return `Warning. Memory usage is very high on ${formattedPc}.`;
  }

  if (type.includes('risk') || type.includes('ai_risk')) {
    return `Critical Alert. AI Risk Level is High for ${formattedPc}.`;
  }

  if (type.includes('emergency')) {
    return `Critical Security Alert. Immediate administrator attention is required.`;
  }

  // Fallback to custom alert messages
  if (evt.message) {
    return evt.message;
  }

  return '';
};

export const useVoiceAlerts = () => {
  const [voices, setVoices] = useState([]);
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('voiceSettings');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('[VoiceAlerts] Failed to load settings:', e);
    }
    return {
      enabled: true,
      volume: 0.8,
      rate: 1.0,
      pitch: 1.0,
      voiceName: ''
    };
  });

  const queue = useRef([]);
  const isSpeaking = useRef(false);
  const spokenIds = useRef(new Set());
  const settingsRef = useRef(settings);

  // Keep ref in sync to prevent closure issues in async loops
  useEffect(() => {
    settingsRef.current = settings;
    localStorage.setItem('voiceSettings', JSON.stringify(settings));
  }, [settings]);

  // Load SpeechSynthesis voices
  useEffect(() => {
    const loadVoices = () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        const availableVoices = window.speechSynthesis.getVoices() || [];
        setVoices(availableVoices);
        
        // Pick a default voice if none set
        if (availableVoices.length > 0 && !settingsRef.current.voiceName) {
          // Prefer standard English/Natural voices
          const defaultVoice = availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0];
          setSettings(prev => ({ ...prev, voiceName: defaultVoice.name }));
        }
      }
    };

    loadVoices();
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  /**
   * Processes the speech announcement queue sequentially
   */
  const processQueue = useCallback(() => {
    if (isSpeaking.current || queue.current.length === 0) return;

    const currentSettings = settingsRef.current;
    if (!currentSettings.enabled) {
      queue.current = []; // Clear queue if disabled
      return;
    }

    const textToSpeak = queue.current.shift();
    if (!textToSpeak) return;

    isSpeaking.current = true;
    console.log(`[VoiceAlerts] Playing chime and speaking: "${textToSpeak}"`);

    // Play high-quality audio chime
    playChime(currentSettings.volume);

    // Wait for the chime, then initiate speech
    setTimeout(() => {
      if (!window.speechSynthesis) {
        isSpeaking.current = false;
        return;
      }

      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.volume = currentSettings.volume;
      utterance.rate = currentSettings.rate;
      utterance.pitch = currentSettings.pitch;

      if (currentSettings.voiceName) {
        const foundVoice = window.speechSynthesis.getVoices().find(v => v.name === currentSettings.voiceName);
        if (foundVoice) {
          utterance.voice = foundVoice;
        }
      }

      utterance.onend = () => {
        isSpeaking.current = false;
        processQueue();
      };

      utterance.onerror = (e) => {
        console.error('[VoiceAlerts] Speech error:', e);
        isSpeaking.current = false;
        processQueue();
      };

      window.speechSynthesis.speak(utterance);
    }, 600);
  }, []);

  /**
   * Public function to queue a new alert event
   */
  const speakAlert = useCallback((evt) => {
    if (!settingsRef.current.enabled || !evt) return;

    const type = (evt.activity_type || evt.alert_type || evt.event || '').toLowerCase();
    
    // Deduplicate: key on computer_id + type + approximate timestamp (within 2 seconds)
    const timeKey = Math.floor(new Date(evt.timestamp || evt.created_at || Date.now()).getTime() / 2000);
    const eventId = evt.id || `${evt.computer_id || evt.computerId}-${type}-${timeKey}`;
    
    if (spokenIds.current.has(eventId)) {
      console.log(`[VoiceAlerts] Duplicate alert skipped: ${eventId}`);
      return;
    }
    spokenIds.current.add(eventId);

    const speechText = getSpeechText(evt);
    if (!speechText) return;

    queue.current.push(speechText);
    processQueue();
  }, [processQueue]);

  return {
    voices,
    settings,
    setSettings,
    speakAlert
  };
};

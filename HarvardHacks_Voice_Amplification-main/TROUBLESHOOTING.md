# Audio Detection Troubleshooting Guide

## 🚨 **Current Issue: Audio Level Always 0.0000**

Based on the server logs, audio data is being received but the levels are always zero. This indicates a microphone access or audio processing issue.

## 🔧 **Step-by-Step Debugging**

### **Step 1: Use the Audio Test Tool**
1. **Start the server:**
   ```bash
   python simple_server.py
   ```

2. **Open the audio test tool:**
   ```
   http://localhost:5000/test
   ```

3. **Click "Start Audio Test"** and check the debug log for:
   - ✅ Microphone access granted
   - ✅ Audio tracks found
   - ✅ Audio context created
   - ✅ Local audio levels showing

### **Step 2: Check Browser Console**
1. **Open browser console** (F12)
2. **Look for errors** related to:
   - `getUserMedia` permissions
   - Audio context creation
   - WebSocket connections

### **Step 3: Verify Microphone Access**
1. **Check browser permissions:**
   - Chrome: Click lock icon in address bar
   - Firefox: Click shield icon
   - Edge: Click lock icon

2. **Ensure microphone is enabled** and not muted

## 🎯 **Common Issues & Solutions**

### **Issue 1: Microphone Permission Denied**
**Symptoms:** Error message about microphone access
**Solutions:**
- Grant microphone permission when prompted
- Check browser settings for microphone access
- Try incognito/private mode
- Use HTTPS (some browsers require secure context)

### **Issue 2: Audio Context Suspended**
**Symptoms:** Audio context shows as suspended
**Solutions:**
- Click anywhere on the page to resume audio context
- Add user interaction before starting audio

### **Issue 3: Wrong Audio Device**
**Symptoms:** Microphone access granted but no audio detected
**Solutions:**
- Check system audio settings
- Ensure correct microphone is selected
- Test microphone in other applications

### **Issue 4: Browser Compatibility**
**Symptoms:** getUserMedia not supported
**Solutions:**
- Use Chrome (best support)
- Update browser to latest version
- Try different browser

## 🔍 **Debug Information to Check**

### **In Audio Test Tool:**
1. **Local Audio Level** - Should show values > 0 when speaking
2. **Server Audio Level** - Should match local level
3. **Audio Tracks** - Should show microphone details
4. **Debug Log** - Should show successful initialization

### **In Browser Console:**
1. **WebSocket connection** - Should show "Connected to server"
2. **Audio context** - Should show sample rate and state
3. **Media stream** - Should show active tracks

### **In Server Console:**
1. **Audio data received** - Should show non-zero values
2. **Audio range** - Should show variation in values
3. **Max/RMS levels** - Should be > 0 when speaking

## 🚀 **Quick Fixes to Try**

### **Fix 1: Reset Audio Context**
```javascript
// In browser console
if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume();
}
```

### **Fix 2: Check Microphone Settings**
1. **Windows:** Settings > Privacy > Microphone
2. **Mac:** System Preferences > Security & Privacy > Microphone
3. **Browser:** Allow microphone access

### **Fix 3: Try Different Audio Constraints**
```javascript
// More permissive constraints
const constraints = {
    audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
        sampleRate: 44100,  // Try different sample rate
        channelCount: 1
    }
};
```

## 📊 **Expected Behavior**

### **When Working Correctly:**
- ✅ Local audio level shows values > 0.001 when speaking
- ✅ Server receives audio data with non-zero levels
- ✅ Audio visualizer shows activity
- ✅ Debug log shows successful initialization

### **When Not Working:**
- ❌ Local audio level always 0.0000
- ❌ Server receives audio data but levels are 0
- ❌ No audio visualizer activity
- ❌ Error messages in console

## 🆘 **If Still Not Working**

1. **Try different browser** (Chrome recommended)
2. **Check system audio settings**
3. **Test microphone in other applications**
4. **Try different microphone/headset**
5. **Check firewall/antivirus settings**

## 📝 **Report Information**

If the issue persists, please provide:
1. **Browser and version**
2. **Operating system**
3. **Audio test tool output**
4. **Browser console errors**
5. **Server console output**

---

**The audio test tool at `http://localhost:5000/test` will help identify the exact issue!**

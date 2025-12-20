# Testing Guide for Barrot

This guide covers testing all features of the Barrot website.

## Quick Start Testing

### Local Testing

1. **Start the server**
   ```bash
   npm start
   ```

2. **Open your browser**
   Navigate to: `http://localhost:3000`

3. **Test each feature** as outlined below

## Feature Testing Checklist

### ✅ Navigation
- [ ] Click each navigation link (Home, Streaming, Studio, Chat, About)
- [ ] Verify smooth scrolling to sections
- [ ] Test mobile menu (hamburger icon on mobile)
- [ ] Verify active link highlighting on scroll

### ✅ Hero Section
- [ ] Verify hero animation loads (particle network)
- [ ] Test "Start Streaming" button
- [ ] Test "Chat with Barrot" button
- [ ] Verify responsive design on mobile

### ✅ Live Streaming
- [ ] Click "Start Stream" button
- [ ] Grant camera/microphone permissions when prompted
- [ ] Verify video stream displays in player
- [ ] Test "Toggle Audio" button
- [ ] Test "Toggle Video" button
- [ ] Change quality settings (480p, 720p, 1080p)
- [ ] Verify stream duration counter updates
- [ ] Click "Stop Stream" to end streaming
- [ ] Verify all controls disable/enable appropriately

**Expected Behavior:**
- Video should display in the player
- Audio/video toggles should work immediately
- Duration counter should increment every second
- Quality changes should restart the stream

### ✅ Recording Studio
- [ ] Click "Record" button
- [ ] Grant microphone permission when prompted
- [ ] Verify audio visualization appears (waveform)
- [ ] Test volume, reverb, and delay sliders
- [ ] Click "Pause" button
- [ ] Click "Resume" (Pause button changes to Resume)
- [ ] Click "Stop" to finish recording
- [ ] Verify recording appears in recordings list
- [ ] Test "Playback" button
- [ ] Test "Download" button
- [ ] Create multiple recordings
- [ ] Verify all recordings are saved in the list

**Expected Behavior:**
- Waveform should animate during recording
- Sliders should update displayed values
- Downloaded files should be in WebM format
- Recording list should show all recordings with timestamps

### ✅ 3D Rendering
- [ ] Verify 3D shape renders (default: cube)
- [ ] Change shape (Sphere, Torus, Cone)
- [ ] Adjust rotation speed slider
- [ ] Change color with color picker
- [ ] Drag the 3D object with mouse to rotate manually
- [ ] Test on touch devices (drag with finger)
- [ ] Click "Reset" button
- [ ] Click "Export" button to download render
- [ ] Verify exported image is PNG format

**Expected Behavior:**
- Shape should rotate automatically
- Shape should change immediately when selected
- Color should update in real-time
- Manual rotation should work with mouse/touch
- Export should download a PNG image

### ✅ Chat Interface
- [ ] Type a message in the chat input
- [ ] Press Enter or click send button
- [ ] Verify message appears in chat history
- [ ] Verify AI response appears after ~1 second
- [ ] Click quick question buttons
- [ ] Test various keywords:
  - "streaming"
  - "recording"
  - "3d rendering"
  - "features"
  - "help"
- [ ] Verify chat scrolls to bottom with new messages
- [ ] Check timestamps on messages

**Expected Behavior:**
- Messages should appear with smooth animation
- Bot responses should be relevant to the question
- Quick questions should auto-fill and send
- Chat should be scrollable when full

### ✅ Chat Widget
- [ ] Click floating chat button (bottom-right corner)
- [ ] Verify it scrolls to chat section
- [ ] Test hover effect on button

### ✅ Responsive Design
- [ ] Test on desktop (1920x1080, 1366x768)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667, 414x896)
- [ ] Verify hamburger menu works on mobile
- [ ] Check all sections are readable on small screens
- [ ] Test landscape and portrait orientations

### ✅ Cross-Browser Testing
- [ ] Google Chrome
- [ ] Mozilla Firefox
- [ ] Safari (Mac/iOS)
- [ ] Microsoft Edge
- [ ] Opera

### ✅ Performance
- [ ] Check page load time (< 3 seconds)
- [ ] Verify smooth animations (60fps)
- [ ] Test with slow network connection
- [ ] Check memory usage in DevTools
- [ ] Verify no console errors

## API Testing

### Health Check
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{"status":"ok","message":"Barrot API is running"}
```

### Chat Message
```bash
curl -X POST http://localhost:3000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I start streaming?","userId":1}'
```

### Get Chat History
```bash
curl http://localhost:3000/api/chat/history?userId=1
```

### Create User
```bash
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'
```

### Get Recordings
```bash
curl http://localhost:3000/api/recordings?userId=1
```

## Automated Testing (Optional)

### Unit Tests
```bash
npm test
```

### End-to-End Tests with Playwright

Create `tests/e2e.spec.js`:
```javascript
const { test, expect } = require('@playwright/test');

test('homepage loads', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/Barrot/);
});

test('navigation works', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('a[href="#streaming"]');
  await expect(page.locator('#streaming')).toBeVisible();
});

test('chat sends message', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('a[href="#chat"]');
  await page.fill('#chatInput', 'Hello Barrot');
  await page.click('#sendMessage');
  await expect(page.locator('.user-message')).toBeVisible();
});
```

Run tests:
```bash
npx playwright test
```

## Common Issues and Solutions

### Issue: Camera/Microphone Not Working
**Solutions:**
- Check browser permissions
- Ensure HTTPS is used (required for WebRTC in production)
- Try different browser
- Check if device is already in use by another application

### Issue: 3D Rendering Not Displaying
**Solutions:**
- Check browser WebGL support: visit `chrome://gpu`
- Update graphics drivers
- Try different browser
- Check console for Three.js errors

### Issue: Audio Recording Not Working
**Solutions:**
- Grant microphone permission
- Check microphone is connected and working
- Test in different browser
- Check audio input settings

### Issue: Chat Not Responding
**Solutions:**
- Check server is running
- Verify API endpoint is accessible
- Check browser console for errors
- Verify network connection

### Issue: Slow Performance
**Solutions:**
- Close other browser tabs
- Disable browser extensions
- Clear browser cache
- Check system resources
- Use production build

## Performance Benchmarks

Target metrics:
- **Page Load Time**: < 3 seconds
- **Time to Interactive**: < 5 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Cumulative Layout Shift**: < 0.1
- **Largest Contentful Paint**: < 2.5 seconds

Use Lighthouse in Chrome DevTools to measure these metrics.

## Accessibility Testing

- [ ] Test with keyboard navigation (Tab, Enter, Space)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast ratios (WCAG AA compliant)
- [ ] Check focus indicators are visible
- [ ] Verify all images have alt text
- [ ] Test with browser zoom (200%, 300%)

## Security Testing

- [ ] Test input validation (XSS attempts)
- [ ] Verify HTTPS in production
- [ ] Check CORS settings
- [ ] Test SQL injection (if using dynamic queries)
- [ ] Verify sensitive data is not exposed in client-side code
- [ ] Check CSP headers
- [ ] Test rate limiting (if implemented)

## Reporting Bugs

When reporting bugs, include:
1. Browser and version
2. Operating system
3. Steps to reproduce
4. Expected behavior
5. Actual behavior
6. Screenshots/videos
7. Console errors
8. Network tab information

## Test Results Template

```markdown
## Test Results - [Date]

**Environment:** [Local/Production]
**Browser:** [Chrome 120.0]
**OS:** [Windows 11]
**Tester:** [Your Name]

### Passed Tests
- ✅ Navigation
- ✅ Streaming
- ✅ Recording
- ...

### Failed Tests
- ❌ 3D Rendering - Shape not loading on Safari
  - Error: WebGL context lost
  - Priority: High

### Notes
- Overall performance is good
- Mobile experience needs improvement
- Suggest adding loading indicators
```

## Continuous Testing

Set up automated testing in CI/CD:
1. Run on every pull request
2. Test on multiple browsers
3. Check performance metrics
4. Verify accessibility
5. Security scans

## Support

For testing assistance:
- Check the documentation
- Review console logs
- Open an issue on GitHub
- Contact the development team

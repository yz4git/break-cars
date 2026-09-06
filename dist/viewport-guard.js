// iPhone Safari gameplay viewport guard.
// Keep one-finger game taps/pointer controls intact; block only browser zoom/pan gestures.
(() => {
  const prevent = e => e.preventDefault();

  // Safari still emits proprietary gesture events even with touch-action:none.
  for (const type of ['gesturestart', 'gesturechange', 'gestureend']) {
    document.addEventListener(type, prevent, { passive: false, capture: true });
  }

  // Block pinch/pan only when more than one finger is active.
  document.addEventListener('touchmove', e => {
    if (e.touches && e.touches.length > 1) e.preventDefault();
  }, { passive: false, capture: true });

  document.addEventListener('touchstart', e => {
    if (e.touches && e.touches.length > 1) e.preventDefault();
  }, { passive: false, capture: true });

  // Prevent Safari smart-zoom from double taps/clicks without delaying normal single taps.
  document.addEventListener('dblclick', prevent, { passive: false, capture: true });

  // The game is a fixed full-screen surface. Safari can retain a visual-viewport
  // pan offset after browser chrome/orientation transitions, so pin page scroll to origin.
  const pinViewport = () => {
    if (window.scrollX !== 0 || window.scrollY !== 0) window.scrollTo(0, 0);
    const vv = window.visualViewport;
    if (!vv) return;
    document.documentElement.style.setProperty('--vv-width', `${vv.width}px`);
    document.documentElement.style.setProperty('--vv-height', `${vv.height}px`);
    document.documentElement.style.setProperty('--vv-left', `${vv.offsetLeft}px`);
    document.documentElement.style.setProperty('--vv-top', `${vv.offsetTop}px`);
  };

  window.addEventListener('scroll', pinViewport, { passive: true });
  window.addEventListener('orientationchange', pinViewport, { passive: true });
  window.addEventListener('pageshow', pinViewport, { passive: true });
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', pinViewport, { passive: true });
    window.visualViewport.addEventListener('scroll', pinViewport, { passive: true });
  }
  pinViewport();
})();

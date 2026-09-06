(() => {
  const scoreEl = document.getElementById('score');
  const aliveEl = document.getElementById('alive');
  if (!scoreEl || !aliveEl) return;

  const fx = document.createElement('div');
  fx.id = 'impact-feedback';
  fx.innerHTML = '<b></b><span></span>';
  document.body.appendChild(fx);

  let previousScore = 0;
  let previousAlive = 12;
  let combo = 0;
  let lastImpactAt = 0;
  let hideTimer = 0;

  const selectedMode = () => document.querySelector('.mode-select [data-mode].selected')?.dataset.mode || 'colosseum';
  const readScore = () => Number((scoreEl.textContent || '0').replace(/[^0-9]/g, '')) || 0;
  const readAlive = () => Number((aliveEl.textContent || '12').match(/\d+/)?.[0] || 12);

  function reset() {
    previousScore = readScore();
    previousAlive = readAlive();
    combo = 0;
    fx.classList.remove('show', 'wreck', 'big');
  }

  function show(label, points, wreck = false, big = false) {
    const now = performance.now();
    combo = now - lastImpactAt < 1400 ? combo + 1 : 1;
    lastImpactAt = now;
    fx.querySelector('b').textContent = label;
    fx.querySelector('span').textContent = `+${points}${combo >= 2 ? `  ×${combo}` : ''}`;
    fx.classList.toggle('wreck', wreck);
    fx.classList.toggle('big', big);
    fx.classList.remove('show');
    void fx.offsetWidth;
    fx.classList.add('show');
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => fx.classList.remove('show'), wreck ? 1250 : 850);
  }

  const observer = new MutationObserver(() => {
    const score = readScore();
    const alive = readAlive();
    const delta = score - previousScore;
    const destroyed = alive < previousAlive;

    if (selectedMode() === 'colosseum' && document.body.classList.contains('playing') && delta > 0) {
      if (destroyed && delta >= 400) show('WRECK', delta, true, true);
      else if (delta >= 220) show('BIG HIT', delta, false, true);
      else if (delta >= 90) show('SMASH', delta, false, false);
      else show('IMPACT', delta, false, false);
    }

    previousScore = score;
    previousAlive = alive;
  });

  observer.observe(scoreEl, { childList: true, characterData: true, subtree: true });
  observer.observe(aliveEl, { childList: true, characterData: true, subtree: true });

  document.getElementById('start')?.addEventListener('click', () => setTimeout(reset, 0));
  document.getElementById('retry')?.addEventListener('click', () => setTimeout(reset, 0));
  document.getElementById('home')?.addEventListener('click', reset);
  for (const button of document.querySelectorAll('.mode-select [data-mode]')) button.addEventListener('click', reset);

  reset();
})();

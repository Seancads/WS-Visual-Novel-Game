// Nav scroll effect
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 60), { passive: true });

// Scroll reveal animations
const io = new IntersectionObserver(e => {
  e.forEach(x => {
    if (x.isIntersecting) {
      x.target.classList.add('visible');
      io.unobserve(x.target);
    }
  });
}, { threshold: .1 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// Character stage carousel
const slots = document.querySelectorAll('.cslot');
const strips = document.querySelectorAll('.cstrip-item');
let autoTimer;

function activate(idx) {
  slots.forEach(s => s.classList.toggle('active', +s.dataset.i === idx));
  strips.forEach(s => s.classList.toggle('active', +s.dataset.i === idx));
}

function startAuto() {
  let i = 0;
  autoTimer = setInterval(() => {
    i = (i + 1) % 6;
    activate(i);
  }, 4200);
}

function userPick(idx) {
  clearInterval(autoTimer);
  activate(idx);
  setTimeout(startAuto, 8000);
}

slots.forEach(s => s.addEventListener('click', () => userPick(+s.dataset.i)));
strips.forEach(s => s.addEventListener('click', () => userPick(+s.dataset.i)));
startAuto();

// ---------- WORKING DOWNLOAD BUTTONS ----------
// Change this path to the real location of your .exe or .zip file
const GAME_FILE_PATH = 'game/dist/Echoes Of Valor.exe';
let isDownloading = false; // Prevent multiple simultaneous downloads

function downloadGame() {
  // Prevent multiple downloads at once
  if (isDownloading) return;
  isDownloading = true;

  // Create a temporary anchor and trigger download
  const link = document.createElement('a');
  link.href = GAME_FILE_PATH;
  link.download = 'Echoes Of Valor.exe';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Reset flag after a short delay
  setTimeout(() => {
    isDownloading = false;
  }, 1000);
}

// Consolidate all download button listeners to avoid duplicate triggers
const downloadButtons = new Set([
  document.getElementById('downloadBtnHero'),
  document.getElementById('realDownloadBtn'),
  ...document.querySelectorAll('.dlbtn')
].filter(btn => btn !== null));

downloadButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    downloadGame();
  });
});
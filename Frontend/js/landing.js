/* ═══════════════════════════════════════════════════
   LANDING PAGE JAVASCRIPT
   ═══════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initializePulseAnimation();
    animateStatsOnScroll();
});

// Pulse Line Animation for Demo
function initializePulseAnimation() {
    const pulseLine = document.getElementById('pulseLine');
    if (!pulseLine) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = pulseLine.offsetWidth;
    canvas.height = 80;
    pulseLine.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    let offset = 0;
    
    function drawPulse() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Gold gradient stroke
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        gradient.addColorStop(0, '#D4AF37');
        gradient.addColorStop(1, '#F5C542');
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2.5;
        ctx.shadowBlur = 8;
        ctx.shadowColor = 'rgba(212, 175, 55, 0.4)';
        
        ctx.beginPath();
        
        for (let x = 0; x < canvas.width; x++) {
            const y = canvas.height / 2 + 
                     Math.sin((x + offset) * 0.05) * 15 +
                     Math.sin((x + offset) * 0.1) * 8;
            
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        
        ctx.stroke();
        offset += 1.5;
        
        requestAnimationFrame(drawPulse);
    }
    
    drawPulse();
}

// Animate stats on scroll
function animateStatsOnScroll() {
    const statCards = document.querySelectorAll('.stat-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('fade-in');
                }, index * 100);
            }
        });
    }, { threshold: 0.5 });
    
    statCards.forEach(card => {
        observer.observe(card);
    });
}

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

console.log('%c Elite Health Command ', 
    'background: linear-gradient(135deg, #D4AF37, #F5C542); color: white; font-size: 16px; font-weight: bold; padding: 10px 20px;');
console.log('Premium Military Health Monitoring System - Active');
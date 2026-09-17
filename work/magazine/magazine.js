(()=>{
const bar=document.querySelector('.reader-bar'), progress=document.querySelector('.reading-progress'), label=document.querySelector('.current-chapter');
const dialog=document.getElementById('contents-dialog'), trigger=document.querySelector('.menu-button');
trigger.addEventListener('click',()=>{dialog.showModal();document.body.classList.add('menu-open')});
function closeMenu(){dialog.close()}
document.querySelector('.close-menu').addEventListener('click',closeMenu);
dialog.addEventListener('close',()=>{document.body.classList.remove('menu-open');trigger.focus({preventScroll:true})});
dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right)closeMenu()}});
dialog.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>closeMenu()));
const chapters=[...document.querySelectorAll('.chapter')];let ticking=false;
function update(){const y=window.scrollY,max=document.documentElement.scrollHeight-innerHeight;progress.style.transform=`scaleX(${max>0?Math.min(1,y/max):0})`;bar.classList.toggle('scrolled',y>90);let current='人文旅行手册';for(const ch of chapters){if(ch.getBoundingClientRect().top<160)current=ch.dataset.chapter;else break}label.textContent=current;ticking=false}
addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(update);ticking=true}},{passive:true});addEventListener('resize',update);update();
function revealAppendix(){const id=decodeURIComponent(location.hash.slice(1));if(id==='sources'||id==='credits'){const section=document.getElementById(id);section.querySelector('details').open=true;requestAnimationFrame(()=>section.scrollIntoView({behavior:'instant',block:'start'}))}}
addEventListener('hashchange',revealAppendix);revealAppendix();
})();

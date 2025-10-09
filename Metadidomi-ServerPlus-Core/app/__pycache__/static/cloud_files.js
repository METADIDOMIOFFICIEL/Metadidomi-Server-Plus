// JS extrait de cloud_files.html
var socket = io();
let allFiles = [];
let currentCategory = 'all';

function getVideoThumbnail(url, time, callback) {
  const video = document.createElement('video');
  video.src = url;
  video.crossOrigin = 'anonymous';
  video.muted = true;
  video.preload = 'auto';
  video.addEventListener('loadeddata', function() {
    video.currentTime = time;
  });
  video.addEventListener('seeked', function() {
    const canvas = document.createElement('canvas');
    canvas.width = 96;
    canvas.height = 60;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    callback(canvas.toDataURL('image/jpeg'));
  });
}

function renderFiles(files) {
  const grid = document.getElementById('fileGrid');
  grid.innerHTML = '';
  if (files.length === 0) {
    grid.innerHTML = '<p>Aucun fichier disponible</p>';
  } else {
    files.forEach(f => {
      const ext = f.name.split('.').pop().toLowerCase();
      let cat = 'other';
      if(['mp4','webm','mkv','avi','ogg'].includes(ext)) cat = 'video';
      else if(['mp3','wav','ogg','flac'].includes(ext)) cat = 'audio';
      else if(['pdf','doc','docx','txt','ppt','xls'].includes(ext)) cat = 'doc';

      if(currentCategory!=='all' && currentCategory!==cat) return;

      // Correction : on récupère bien les compteurs depuis l'API
      let views = f.views || 0;
      let downloads = f.downloads || 0;
      let plays = f.plays || 0;

      let thumb = '/static/icons/file.png';
      if(cat==='video') thumb = '/thumbnails/'+f.name+'.jpg';
      else if(cat==='audio') thumb = '/static/icons/music.png';
      else if(cat==='doc') thumb = '/static/icons/doc.png';

      // Détection automatique des chapitres pour les vidéos
      let chapters = [];
      if(cat==='video'){
        // Utilise la durée réelle si disponible
        let duration = f.duration || 1200;
        let nChapters = 5;
        let labels = [];
        let times = [];
        for(let i=0; i<nChapters; i++){
          let t = Math.floor(duration * i / nChapters);
          times.push(t);
          labels.push(i===0 ? 'Début' : (i===nChapters-1 ? 'Fin' : `Partie ${i}`));
        }
        chapters = labels.map((label, i) => {
          // Miniature de chaque partie si dispo, sinon SVG
          let thumbPart = f.thumbnails && f.thumbnails[i] ? f.thumbnails[i] : null;
          let thumbHtml = thumbPart ? `<img src='${thumbPart}' style='width:48px;height:32px;border-radius:6px;object-fit:cover;margin-right:8px;'>` : `<svg width='48' height='32'><rect width='48' height='32' rx='6' fill='#222'/><text x='24' y='20' text-anchor='middle' font-size='12' fill='#fff'>${label}</text></svg>`;
          return { label, time: times[i], thumbHtml };
        });
      }

      const card = document.createElement('div');
      card.className = 'card';

      // Ajout gestion appui long (téléchargement)
      let longPressTimer;
      card.addEventListener('mousedown', function(e) {
        longPressTimer = setTimeout(() => {
          incrementViewCount(f.name, 'download');
          window.open('/download/'+f.name,'_blank');
        }, 600); // 600ms pour appui long
      });
      card.addEventListener('mouseup', function(e) {
        clearTimeout(longPressTimer);
      });
      card.addEventListener('mouseleave', function(e) {
        clearTimeout(longPressTimer);
      });

      card.onclick = () => {
        incrementViewCount(f.name, cat); // Incrémente dès le clic sur la carte
        if(cat==='audio') openMediaModal('audio','/download/'+f.name,ext, f.name);
        else if(cat==='video') openMediaModal('video','/download/'+f.name,ext, f.name, chapters);
        else window.open('/download/'+f.name,'_blank');
      };
      card.innerHTML = `
        <div class="thumb" style="background-image:url('${thumb}')">
          <span class="file-type-icon">
            ${cat === 'video' ? `<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M8 5v14l11-7z" fill="#e50914"/></svg>` :
              cat === 'audio' ? `<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M9 17V5l12-2v14" stroke="#1db954" stroke-width="2"/><circle cx="6" cy="18" r="3" fill="#1db954"/></svg>` :
              cat === 'doc' ? `<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" fill="#2196f3"/><text x="8" y="16" font-size="8" fill="#fff">DOC</text></svg>` :
              `<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" fill="#aaa"/></svg>`
            }
          </span>
        </div>
        <div class="card-content">
          <div class="card-title">${f.name}</div>
          <div class="card-meta">
            ${(f.size/1024).toFixed(1)} Ko • ${f.mtime}
            <span style="margin-left:10px;color:#888;font-size:0.95em;vertical-align:middle;display:inline-flex;gap:12px;">
              <span title="Vues"><svg width='16' height='16' viewBox='0 0 24 24' fill='none' style='vertical-align:middle;'><path d='M1 12a11 11 0 0 1 22 0 11 11 0 0 1-22 0zm11-4a4 4 0 1 1 0 8 4 4 0 0 1 0-8z' stroke='#2196f3' stroke-width='2' fill='none'/><circle cx='12' cy='12' r='3' fill='#2196f3'/></svg> ${views}</span>
              <span title="Écoutes"><svg width='16' height='16' viewBox='0 0 24 24' fill='none' style='vertical-align:middle;'><path d='M3 10v4a1 1 0 0 0 1 1h3v2a2 2 0 0 0 4 0v-2h3a1 1 0 0 0 1-1v-4' stroke='#1db954' stroke-width='2' fill='none'/></svg> ${plays}</span>
              <span title="Téléchargements"><svg width='16' height='16' viewBox='0 0 24 24' fill='none' style='vertical-align:middle;'><path d='M12 3v12m0 0l-4-4m4 4l4-4M4 19h16' stroke='#e50914' stroke-width='2' fill='none'/></svg> ${downloads}</span>
            </span>
          </div>
        </div>
      `;
      grid.appendChild(card);
      // Génère la miniature à la volée pour les vidéos
      if(cat==='video') {
        getVideoThumbnail('/download/'+f.name, (f.duration||120)*0.1, function(dataUrl) {
          card.querySelector('.thumb').style.backgroundImage = `url('${dataUrl}')`;
        });
      }
    });
  }
}

function filterFiles(query) {
  query = query.toLowerCase();
  const filtered = allFiles.filter(f => f.name.toLowerCase().includes(query));
  renderFiles(filtered);
}

function switchCategory(cat) {
  currentCategory = cat;
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.querySelector(`nav button[onclick="switchCategory('${cat}')"]`).classList.add('active');
  renderFiles(allFiles);
}

socket.on('files_update', function(files) { allFiles = files; renderFiles(allFiles); });
fetch('/api/files').then(r => r.json()).then(data => { allFiles = data.files; renderFiles(allFiles); });
setInterval(() => socket.emit('ping_user'), 30000);

function incrementViewCount(name, type) {
  fetch('/api/increment_view', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, type })
  }).then(() => {
    // Après l'incrémentation, on rafraîchit la liste
    fetch('/api/files').then(r => r.json()).then(data => { allFiles = data.files; renderFiles(allFiles); });
  });
}

function openMediaModal(type, src, ext, name, chapters=[]) {
  incrementViewCount(name, type); // Ajout de l'incrémentation
  const container = document.getElementById('mediaPlayerContainer');
  container.innerHTML = '';
  if(type==='audio'){
    container.innerHTML = `
      <div class="audio-player-box">
        <div class="audio-title">${name || 'Lecture audio'}</div>
        <audio controls autoplay controlsList="nodownload" src="${src}"></audio>
        <div style="margin-top:10px;color:#aaa;font-size:0.95em;">Format : ${ext.toUpperCase()}</div>
        <button class="download-btn" style="margin-top:12px;padding:6px 18px;border-radius:6px;background:#2196f3;color:#fff;border:none;cursor:pointer;font-size:1em;" onclick="incrementViewCount('${name}','download');window.open('${src}','_blank');">Télécharger</button>
      </div>
    `;
  } else if(type==='video'){
    const videoBox = document.createElement('div');
    videoBox.style.display = 'flex';
    videoBox.style.flexDirection = 'column';
    videoBox.style.alignItems = 'center';
    videoBox.style.justifyContent = 'center';
    videoBox.style.width = '100%';
    // Lecteur vidéo
    const video = document.createElement('video');
    video.controls = true;
    video.autoplay = true;
    video.setAttribute('controlsList', 'nodownload');
    video.style.width = '100%';
    video.innerHTML = `<source src="${src}" type="video/${ext}">`;
    videoBox.appendChild(video);
    // Champitrage
    let duration = chapters.length ? chapters[chapters.length-1].time+1 : 1200;
    let nChapters = chapters.length || 5;
    if(nChapters && chapters.length === 0) {
      let labels = [];
      let times = [];
      for(let i=0; i<nChapters; i++){
        let t = Math.floor(duration * i / nChapters);
        times.push(t);
        labels.push(i===0 ? 'Début' : (i===nChapters-1 ? 'Fin' : `Partie ${i}`));
      }
      chapters = labels.map((label, i) => ({ label, time: times[i] }));
    }
    if(chapters.length > 0){
      const chaptersDiv = document.createElement('div');
      chaptersDiv.style.margin = '18px 0 0 0';
      chaptersDiv.style.display = 'flex';
      chaptersDiv.style.flexWrap = 'wrap';
      chaptersDiv.style.gap = '10px';
      chapters.forEach((ch,i) => {
        const btn = document.createElement('button');
        btn.style = 'background:#181818;color:#fff;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:1em;display:flex;align-items:center;';
        btn.onclick = function(){ video.currentTime = ch.time; };
        btn.innerHTML = `<img class='chapter-thumb' src='/static/icons/file.png' style='width:48px;height:32px;border-radius:6px;object-fit:cover;margin-right:8px;'>${ch.label}`;
        chaptersDiv.appendChild(btn);
        getVideoThumbnail(src, ch.time, function(dataUrl) {
          btn.querySelector('.chapter-thumb').src = dataUrl;
        });
      });
      videoBox.appendChild(chaptersDiv);
    }
    // Bouton de téléchargement pour la vidéo
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'download-btn';
    downloadBtn.style = 'margin-top:16px;padding:6px 18px;border-radius:6px;background:#2196f3;color:#fff;border:none;cursor:pointer;font-size:1em;';
    downloadBtn.textContent = 'Télécharger';
    downloadBtn.onclick = function(){ incrementViewCount(name,'download'); window.open(src,'_blank'); };
    videoBox.appendChild(downloadBtn);
    container.appendChild(videoBox);
  }
  document.getElementById('mediaModal').style.display = 'flex';
}

function closeMediaModal(){
  document.getElementById('mediaModal').style.display='none';
  document.getElementById('mediaPlayerContainer').innerHTML='';
}

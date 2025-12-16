/* ==========================================================================
   Module AR Moteur Hemi - JavaScript
   ========================================================================== */

/**
 * Configuration des etats pedagogiques
 */
var STATES = {
  'state_a': {
    src: 'assets/models/hemi_state_a_full.glb',
    label: 'Complet',
    description: 'Vue d\'ensemble'
  },
  'state_b': {
    src: 'assets/models/hemi_state_b_no_blower.glb',
    label: 'Sans blower',
    description: 'Bloc visible'
  },
  'state_c': {
    src: 'assets/models/hemi_state_c_bloc.glb',
    label: 'Bloc seul',
    description: 'Structure de base'
  }
};

/**
 * Configuration des phases pedagogiques (enrichies avec le "pourquoi")
 */
var PHASES = [
  {
    id: 0,
    name: 'Contexte',
    consigne: '<strong>Contexte :</strong> Ce module presente un moteur Hemi V8 suralimente. <em>Pourquoi "Hemi" ?</em> Ce nom vient des chambres de combustion hemispheriques qui optimisent le rendement.',
    state: 'state_a'
  },
  {
    id: 1,
    name: 'Vue globale',
    consigne: '<strong>Observation :</strong> Identifiez les sous-ensembles : bloc, blower (rouge), distributeur. <em>Pourquoi un blower ?</em> Il force plus d\'air dans les cylindres pour augmenter la puissance.',
    state: 'state_a'
  },
  {
    id: 2,
    name: 'Inspection',
    consigne: '<strong>Inspection :</strong> Sans le blower, le bloc est visible. <em>Pourquoi retirer le blower ?</em> Pour acceder aux composants internes lors de la maintenance.',
    state: 'state_b'
  },
  {
    id: 3,
    name: 'Structure',
    consigne: '<strong>Structure :</strong> Le bloc seul revele la disposition en V a 90°. <em>Pourquoi un V8 ?</em> Compact et equilibre, il offre puissance et douceur de fonctionnement.',
    state: 'state_c'
  },
  {
    id: 4,
    name: 'Synthese',
    consigne: '<strong>Synthese :</strong> Vue complete. Vous pouvez maintenant identifier chaque composant et comprendre son role dans l\'ensemble.',
    state: 'state_a'
  }
];

/**
 * Configuration des vues expertes predefinies
 */
var EXPERT_VIEWS = {
  'front':  { orbit: '0deg 75deg 2.5m', fov: '45deg', label: 'Vue avant' },
  'back':   { orbit: '180deg 75deg 2.5m', fov: '45deg', label: 'Vue arriere' },
  'left':   { orbit: '270deg 75deg 2.5m', fov: '45deg', label: 'Vue gauche' },
  'right':  { orbit: '90deg 75deg 2.5m', fov: '45deg', label: 'Vue droite' },
  'top':    { orbit: '0deg 0deg 3m', fov: '50deg', label: 'Vue dessus' },
  'reset':  { orbit: '35deg 75deg 2.5m', fov: '45deg', label: 'Vue initiale' }
};

var currentPhase = 0;
var currentState = 'state_a';

/**
 * Initialisation au chargement
 */
document.addEventListener('DOMContentLoaded', function() {
  var modelViewer = document.getElementById('moteur-hemi');

  modelViewer.addEventListener('load', function() {
    console.log('[AR Module] Modele 3D charge');
    initHotspots();
  });

  modelViewer.addEventListener('error', function(e) {
    console.error('[AR Module] Erreur de chargement:', e);
  });

  // Initialiser les controles
  initStateButtons();
  initPhaseButtons();
  initViewButtons();

  // Afficher phase 0
  setPhase(0);
});

/**
 * Initialise les boutons d'etat
 */
function initStateButtons() {
  var buttons = document.querySelectorAll('.state-btn');

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var stateId = this.getAttribute('data-state');
      setState(stateId);
    });
  });
}

/**
 * Initialise les boutons de phase
 */
function initPhaseButtons() {
  var buttons = document.querySelectorAll('.phase-btn');

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var phaseId = parseInt(this.getAttribute('data-phase'), 10);
      setPhase(phaseId);
    });
  });
}

/**
 * Initialise les boutons de vues expertes
 */
function initViewButtons() {
  var buttons = document.querySelectorAll('.view-btn');

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var viewId = this.getAttribute('data-view');
      setExpertView(viewId);
    });
  });
}

/**
 * Change la vue de la camera vers une vue experte predéfinie
 */
function setExpertView(viewId) {
  if (!EXPERT_VIEWS[viewId]) {
    console.error('[AR Module] Vue inconnue:', viewId);
    return;
  }

  var modelViewer = document.getElementById('moteur-hemi');
  var view = EXPERT_VIEWS[viewId];

  // Appliquer la nouvelle position de camera avec animation
  modelViewer.cameraOrbit = view.orbit;
  modelViewer.fieldOfView = view.fov;

  console.log('[AR Module] Vue changee:', view.label);
}

/**
 * Change l'etat du modele 3D
 */
function setState(stateId) {
  if (!STATES[stateId]) {
    console.error('[AR Module] Etat inconnu:', stateId);
    return;
  }

  currentState = stateId;

  var modelViewer = document.getElementById('moteur-hemi');
  var state = STATES[stateId];

  // Changer le modele
  modelViewer.src = state.src;

  // Mettre a jour les boutons
  var buttons = document.querySelectorAll('.state-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if (btn.getAttribute('data-state') === stateId) {
      btn.classList.add('active');
    }
  });

  // Gerer la visibilite des hotspots selon l'etat
  updateHotspotsVisibility(stateId);

  console.log('[AR Module] Etat change:', stateId);
}

/**
 * Configuration des hotspots par etat
 * Chaque etat a ses propres hotspots pedagogiques (2-3 max selon le referentiel)
 */
var HOTSPOTS_CONFIG = {
  'state_a': ['hotspot-state-a'],  // Blower, Echappement, Culasse externe
  'state_b': ['hotspot-state-b'],  // Culasses hemispheriques, Surface bloc
  'state_c': ['hotspot-state-c']   // Disposition V, Logement cylindres
};

/**
 * Met a jour la visibilite des hotspots selon l'etat
 * Seuls les hotspots pertinents pour l'etat actuel sont affiches
 */
function updateHotspotsVisibility(stateId) {
  // Masquer tous les hotspots
  var allHotspots = document.querySelectorAll('.hotspot');
  allHotspots.forEach(function(hotspot) {
    hotspot.style.display = 'none';
  });

  // Afficher uniquement les hotspots de l'etat courant
  var activeClasses = HOTSPOTS_CONFIG[stateId] || [];
  activeClasses.forEach(function(className) {
    var hotspotsToShow = document.querySelectorAll('.' + className);
    hotspotsToShow.forEach(function(hotspot) {
      hotspot.style.display = 'block';
    });
  });

  // Log pour debug
  var visibleCount = document.querySelectorAll('.hotspot[style="display: block;"]').length;
  console.log('[AR Module] Hotspots visibles pour ' + stateId + ':', visibleCount);
}

/**
 * Change la phase pedagogique
 */
function setPhase(phaseId) {
  if (phaseId < 0 || phaseId >= PHASES.length) {
    console.error('[AR Module] Phase invalide:', phaseId);
    return;
  }

  currentPhase = phaseId;
  var phase = PHASES[phaseId];

  // Mettre a jour la consigne
  var consigneEl = document.querySelector('.consigne-bandeau p');
  if (consigneEl) {
    consigneEl.innerHTML = phase.consigne;
  }

  // Changer l'etat associe
  setState(phase.state);

  // Mettre a jour les boutons de phase
  var buttons = document.querySelectorAll('.phase-btn');
  buttons.forEach(function(btn) {
    btn.classList.remove('active');
    if (parseInt(btn.getAttribute('data-phase'), 10) === phaseId) {
      btn.classList.add('active');
    }
  });

  console.log('[AR Module] Phase changee:', phaseId, '-', phase.name);
}

/**
 * Initialise les hotspots pour l'accessibilite
 */
function initHotspots() {
  var hotspots = document.querySelectorAll('.hotspot');

  hotspots.forEach(function(hotspot) {
    hotspot.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.focus();
      }
    });

    hotspot.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  });

  console.log('[AR Module] ' + hotspots.length + ' hotspots initialises');
}

/**
 * Navigation phase suivante
 */
function nextPhase() {
  if (currentPhase < PHASES.length - 1) {
    setPhase(currentPhase + 1);
  }
}

/**
 * Navigation phase precedente
 */
function prevPhase() {
  if (currentPhase > 0) {
    setPhase(currentPhase - 1);
  }
}

/**
 * MODE DEBUG : Double-cliquez sur le modele pour obtenir les coordonnees exactes
 * Activez avec : enableDebugMode() dans la console
 */
var debugModeActive = false;
var lastMousePos = { x: 0, y: 0 };

function enableDebugMode() {
  var modelViewer = document.getElementById('moteur-hemi');
  debugModeActive = true;

  // Creer un indicateur visuel
  var debugBanner = document.createElement('div');
  debugBanner.id = 'debug-banner';
  debugBanner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#e94560;color:#fff;padding:10px;text-align:center;z-index:9999;font-weight:bold;';
  debugBanner.innerHTML = 'MODE DEBUG ACTIF - DOUBLE-CLIQUEZ sur le modele | <button onclick="captureCenter()" style="margin-left:10px;padding:5px 10px;cursor:pointer;">Capturer centre ecran</button> <button onclick="disableDebugMode()" style="margin-left:10px;padding:5px 10px;cursor:pointer;">Desactiver</button>';
  document.body.prepend(debugBanner);

  // Suivre la position de la souris
  modelViewer.addEventListener('mousemove', debugMouseMove);
  modelViewer.addEventListener('dblclick', debugClickHandler);

  console.log('[DEBUG] Mode debug active.');
  console.log('[DEBUG] DOUBLE-CLIQUEZ sur le modele pour capturer les coordonnees.');
  console.log('[DEBUG] Ou utilisez captureCenter() pour capturer le centre de l\'ecran.');
}

function debugMouseMove(event) {
  var modelViewer = document.getElementById('moteur-hemi');
  var rect = modelViewer.getBoundingClientRect();
  lastMousePos.x = event.clientX - rect.left;
  lastMousePos.y = event.clientY - rect.top;
}

function debugClickHandler(event) {
  event.preventDefault();
  event.stopPropagation();

  var modelViewer = document.getElementById('moteur-hemi');
  var rect = modelViewer.getBoundingClientRect();
  var x = event.clientX - rect.left;
  var y = event.clientY - rect.top;

  capturePosition(x, y);
}

function captureCenter() {
  var modelViewer = document.getElementById('moteur-hemi');
  var rect = modelViewer.getBoundingClientRect();
  var x = rect.width / 2;
  var y = rect.height / 2;

  capturePosition(x, y);
}

function capturePosition(x, y) {
  var modelViewer = document.getElementById('moteur-hemi');

  console.log('[DEBUG] Capture a x=' + x.toFixed(0) + ', y=' + y.toFixed(0));

  // Obtenir la position 3D du point
  var hit = modelViewer.positionAndNormalFromPoint(x, y);

  if (hit) {
    var pos = hit.position;
    var norm = hit.normal;

    var posStr = pos.x.toFixed(3) + 'm ' + pos.y.toFixed(3) + 'm ' + pos.z.toFixed(3) + 'm';
    var normStr = norm.x.toFixed(2) + ' ' + norm.y.toFixed(2) + ' ' + norm.z.toFixed(2);

    console.log('==================================================');
    console.log('[DEBUG] POSITION CAPTUREE:');
    console.log('  data-position="' + posStr + '"');
    console.log('  data-normal="' + normStr + '"');
    console.log('==================================================');

    // Copier dans le presse-papier
    var clipboardText = posStr;
    navigator.clipboard.writeText(clipboardText).then(function() {
      console.log('[DEBUG] Position copiee: ' + clipboardText);
    }).catch(function() {
      console.log('[DEBUG] Impossible de copier dans le presse-papier');
    });

    // Afficher visuellement
    alert('POSITION CAPTUREE\n\n' + posStr + '\n\nNormal: ' + normStr);
  } else {
    console.log('[DEBUG] Aucune surface detectee a cette position');
    alert('Aucune surface detectee.\nEssayez de cliquer directement sur le modele 3D.');
  }
}

function disableDebugMode() {
  var modelViewer = document.getElementById('moteur-hemi');
  debugModeActive = false;

  modelViewer.removeEventListener('mousemove', debugMouseMove);
  modelViewer.removeEventListener('dblclick', debugClickHandler);

  var banner = document.getElementById('debug-banner');
  if (banner) banner.remove();

  console.log('[DEBUG] Mode debug desactive.');
}

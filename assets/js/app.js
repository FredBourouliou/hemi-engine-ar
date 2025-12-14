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
 * Configuration des phases pedagogiques
 */
var PHASES = [
  {
    id: 0,
    name: 'Contexte',
    consigne: '<strong>Contexte :</strong> Ce module presente un moteur Hemi V8 suralimente. Explorez librement le modele 3D.',
    state: 'state_a'
  },
  {
    id: 1,
    name: 'Vue globale',
    consigne: '<strong>Observation :</strong> Identifiez les principaux sous-ensembles : bloc moteur, culasses, blower, echappement.',
    state: 'state_a'
  },
  {
    id: 2,
    name: 'Inspection',
    consigne: '<strong>Inspection :</strong> Observez le bloc moteur sans le blower. Reperez les culasses hemispheriques.',
    state: 'state_b'
  },
  {
    id: 3,
    name: 'Structure',
    consigne: '<strong>Structure :</strong> Analysez le bloc moteur seul. Notez la disposition en V des cylindres.',
    state: 'state_c'
  },
  {
    id: 4,
    name: 'Synthese',
    consigne: '<strong>Synthese :</strong> Revenez a la vue complete. Vous pouvez maintenant identifier chaque composant.',
    state: 'state_a'
  }
];

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
 * Met a jour la visibilite des hotspots selon l'etat
 */
function updateHotspotsVisibility(stateId) {
  var hotspotBlower = document.querySelector('[slot="hotspot-blower"]');

  if (hotspotBlower) {
    // Le blower n'est visible que dans l'etat A (complet)
    if (stateId === 'state_a') {
      hotspotBlower.style.display = 'block';
    } else {
      hotspotBlower.style.display = 'none';
    }
  }
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

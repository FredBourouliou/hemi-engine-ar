/* ==========================================================================
   Module AR Moteur Hemi - JavaScript
   ========================================================================== */

/**
 * Initialisation du module pedagogique
 * - Gestion des hotspots
 * - Accessibilite clavier
 */

document.addEventListener('DOMContentLoaded', function() {
  const modelViewer = document.getElementById('moteur-hemi');

  // Attendre que le modele soit charge
  modelViewer.addEventListener('load', function() {
    console.log('[AR Module] Modele 3D charge');
    initHotspots();
  });

  // Gestion erreur de chargement
  modelViewer.addEventListener('error', function(e) {
    console.error('[AR Module] Erreur de chargement:', e);
  });
});

/**
 * Initialise les hotspots pour l'accessibilite
 */
function initHotspots() {
  const hotspots = document.querySelectorAll('.hotspot');

  hotspots.forEach(function(hotspot) {
    // Support clavier (Enter/Space pour toggle)
    hotspot.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.focus();
      }
    });

    // Fermer annotation au clic ailleurs (mobile)
    hotspot.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  });

  console.log('[AR Module] ' + hotspots.length + ' hotspots initialises');
}

/**
 * Mise a jour de la consigne pedagogique
 * @param {string} texte - Nouvelle consigne a afficher
 */
function updateConsigne(texte) {
  var consigne = document.querySelector('.consigne-bandeau p');
  if (consigne) {
    consigne.innerHTML = texte;
  }
}

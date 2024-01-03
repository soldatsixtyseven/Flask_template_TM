console.log("Script bien chargé")

function forgotPassword() {
    var email = document.getElementById('email').value;
  
    // Vous pouvez ajouter ici des validations supplémentaires pour l'adresse e-mail
  
    // Envoi de l'adresse e-mail à votre serveur (côté serveur) pour le traitement
    // Dans cet exemple, nous supposons que le serveur a une API pour la récupération de mot de passe
    // Vous devrez implémenter cette partie côté serveur (par exemple, en utilisant PHP)
  
    // Exemple fictif :
    fetch('/api/recover-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: email }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Un lien de récupération a été envoyé à votre adresse e-mail.');
      } else {
        alert('Échec de la récupération de mot de passe. Veuillez vérifier votre adresse e-mail.');
      }
    })
    .catch(error => {
      console.error('Erreur lors de la récupération de mot de passe:', error);
    });
  }
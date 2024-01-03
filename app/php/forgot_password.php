<?php
// Supposons que vous ayez une connexion à votre base de données

// Traitement de la demande de récupération de mot de passe
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $data = json_decode(file_get_contents('php://input'), true);
  $email = $data['email'];

  // Vérifiez si l'e-mail existe dans la base de données
  // Si oui, générez un nouveau mot de passe, mettez à jour la base de données et envoyez-le par e-mail
  // Sinon, renvoyez un message d'erreur

  // Exemple fictif :
  $userExists = checkUserExists($email);

  if ($userExists) {
    // Générez un nouveau mot de passe
    $newPassword = generateRandomPassword();

    // Mettez à jour le mot de passe dans la base de données
    updatePasswordInDatabase($email, $newPassword);

    // Envoyez le nouveau mot de passe par e-mail
    sendNewPasswordByEmail($email, $newPassword);

    // Réponse JSON
    echo json_encode(['success' => true]);
  } else {
    // L'e-mail n'existe pas dans la base de données
    echo json_encode(['error' => 'Adresse e-mail non valide']);
  }
} else {
  // Requête invalide
  http_response_code(400);
  echo json_encode(['error' => 'Méthode non autorisée']);
}

function checkUserExists($email) {
  // Vérifiez si l'e-mail existe dans votre base de données
  // Vous devrez implémenter cette logique en fonction de votre configuration spécifique
  // Retourne true si l'utilisateur existe, sinon false
  // Exemple fictif :
  // return (mysqli_query($connexion, "SELECT * FROM utilisateurs WHERE email = '$email'")->num_rows > 0);
}

function generateRandomPassword() {
  // Générez un nouveau mot de passe aléatoire
  $length = 12;
  $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  $password = '';
  for ($i = 0; $i < $length; $i++) {
    $password .= $characters[rand(0, strlen($characters) - 1)];
  }
  return $password;
}

function updatePasswordInDatabase($email, $newPassword) {
  // Mettez à jour le mot de passe dans votre base de données
  // Vous devrez implémenter cette logique en fonction de votre configuration spécifique
  // Exemple fictif :
  // mysqli_query($connexion, "UPDATE utilisateurs SET mot_de_passe = '$newPassword' WHERE email = '$email'");
}

function sendNewPasswordByEmail($email, $newPassword) {
  // Envoyez le nouveau mot de passe par e-mail
  $subject = 'Nouveau mot de passe';
  $message = 'Votre nouveau mot de passe est : ' . $newPassword;
  $headers = 'From: webmaster@votre-site.com' . "\r\n" .
      'Reply-To: webmaster@votre-site.com' . "\r\n" .
      'X-Mailer: PHP/' . phpversion();

  mail($email, $subject, $message, $headers);
}
?>



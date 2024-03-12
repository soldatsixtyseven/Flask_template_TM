function addCategory() {
    // Créez une nouvelle entrée de catégorie
    var categoryEntry = document.createElement('div');
    categoryEntry.className = 'category-entry';

    // Ajoutez les champs nécessaires
    categoryEntry.innerHTML = `
        <div class="category-entry">   
            <div class="category-box" id="category-box-name">
                <input type="text" name="category_name[]" required placeholder="Nom">
            </div>
            <div class="category-box-year">
                <input type="text" name="year_min[]" required placeholder="0000">
            </div>
            <div class="category-box-year">
                <input type="text" name="year_max[]" required placeholder="0000">
            </div>
            <div class="category-box">
                <input type="text" name="start_time[]" required placeholder="00:00">
            </div>
            <div class="category-box">
                <input type="text" name="price[]" required placeholder="...CHF">
            </div>
            <div class="category-box">
                <input type="text" name="distance[]" required placeholder="... km">
            </div>
            <div class="category-box">
                <input type="text" name="ascent[]" required placeholder="... m">
            </div>
            <div class="category-box">
                <input type="text" name="descent[]" required placeholder="... m">
            </div>
            <button type="button" onclick="removeCategory(this)" class="delete">-</button>
        </div>
    `;

    // Ajoutez l'entrée de catégorie au conteneur
    document.getElementById('categories-container').appendChild(categoryEntry);
}

function removeCategory(button) {
    // Récupérez le conteneur parent de la catégorie à supprimer
    var categoryEntry = button.parentElement;

    // Supprimez la catégorie du conteneur
    categoryEntry.remove();
}

document.addEventListener("DOMContentLoaded", function() {
    const leftScrollButton = document.querySelector(".left-scroll");
    const rightScrollButton = document.querySelector(".right-scroll");
    const courseSection = document.querySelector(".course-section-index");

    leftScrollButton.addEventListener("click", function() {
        courseSection.scrollBy({
            left: -350, // Décalage vers la gauche
            behavior: "smooth"
        });
    });

    rightScrollButton.addEventListener("click", function() {
        courseSection.scrollBy({
            left: 350, // Décalage vers la droite
            behavior: "smooth"
        });
    });
});

// Instruction de redirection de l'utilisateur en fonction de son moyen de paiement
document.addEventListener("DOMContentLoaded", function() {
    // Sélection du bouton "Continuer"
    const continueBtn = document.getElementById("continue-btn-user");

    // Détermination de la réaction à la sélection du bouton "continuer"
    continueBtn.addEventListener("click", function() {
        // Sélection du moyen de paiement choisi
        const selectedPayment = document.querySelector('input[name="payment"]:checked').id;

        // Redirection en fonction du moyen de paiement
        switch (selectedPayment) {
            case "choix1":
                window.location.href = "/paiement/twint";
                break;
            case "choix2":
                window.location.href = "/paiement/postfinance";
                break;
            case "choix3":
                window.location.href = "/paiement/paypal";
                break;
            case "choix4":
                window.location.href = "/paiement/carte-bancaire";
                break;
            default:
                // Si le choix est invalide, on affiche le message suivant :
                alert("Veuillez choisir un moyen de paiement");
        }
    });
});

// Instruction de redirection de l'administrateur en fonction du moyen de paiement choisi
document.addEventListener("DOMContentLoaded", function() {
    // Sélection du bouton "Continuer"
    const continueBtn = document.getElementById("continue-btn-admin");

    // Détermination de la réaction à la sélection du bouton "continuer"
    continueBtn.addEventListener("click", function() {
        // Sélection du moyen de paiement choisi
        const selectedPayment = document.querySelector('input[name="payment"]:checked').id;

        // Redirection en fonction du moyen de paiement
        switch (selectedPayment) {
            case "choix1":
                window.location.href = "/paiement/twint";
                break;
            case "choix2":
                window.location.href = "/paiement/paypal";
                break;
            case "choix3":
                window.location.href = "/paiement/cash";
                break;
            default:
                // Si le choix est invalide, on affiche le message suivant :
                alert("Veuillez choisir un moyen de paiement");
        }
    });
});
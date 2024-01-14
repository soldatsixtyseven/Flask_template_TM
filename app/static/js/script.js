function addCategory() {
    // Créez une nouvelle entrée de catégorie
    var categoryEntry = document.createElement('div');
    categoryEntry.className = 'category-entry';

    // Ajoutez les champs nécessaires
    categoryEntry.innerHTML = `
        <div class="category-entry">   
            <div class="category-box">
                <input type="text" name="category_name[]" required placeholder="Nom">
            </div>
            <div class="category-box">
                <input type="text" name="year[]" required placeholder="0000-0000">
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
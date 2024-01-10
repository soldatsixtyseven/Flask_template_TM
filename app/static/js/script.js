function addCategory() {
    // Créez une nouvelle entrée de catégorie
    var categoryEntry = document.createElement('div');
    categoryEntry.className = 'category-entry';

    // Ajoutez les champs nécessaires
    categoryEntry.innerHTML = `
            <div class="entry-box">
                <input type="text" name="category_name[]" required>
                <label for="category_name">Nom de la catégorie</label>
            </div>
            <div class="entry-box">
                <input type="text" name="year[]" required>
                <label for="year">Années</label>
            </div>
            <div class="entry-box">
                <input type="text" name="start_time[]" required>
                <label for="start_time">Heure de départ</label>
            </div>
            <div class="entry-box">
                <input type="text" name="price[]" required>
                <label for="price">Prix</label>
            </div>
            <div class="entry-box">
                <input type="text" name="distance[]" required>
                <label for="distance">Distance</label>
            </div>
            <div class="entry-box">
                <input type="text" name="ascent[]" required>
                <label for="ascent">Montée</label>
            </div>
            <div class="entry-box">
                <input type="text" name="descent[]" required>
                <label for="descent">Descente</label>
            </div>
        <button type="button" onclick="removeCategory(this)">-</button>
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
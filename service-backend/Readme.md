## Service backend

> Ce project consite à utilisé l'un des algorithmes choisis afin de pouvoir obtenir un backend qui peut encrypter correctement

### Description du payload à signer dans une image
- un identifiant du créateur : UUID
- un horodatage 
- un identifiant de la plateforme
- un hasb de vérification 
    - ceci permettra de pouvoir non seulement détecteru les erreur lors de l'extraction
    - mais aussi sera comme un salting de tout le message


### Methode de cryptage de formation des données de la payload

Il faut implémenter à la fois : 
- Le codes read-solomon
- La répétition du payload au sein de l'image

### Flux d'interaction

- Flux d'insertion

    > Le créateur uploade son image sur la plateforme. Le serveur construit le payload (magic + user ID + timestamp). Le serveur signe le payload avec sa clé privée ECDSA → on obtient le payload signé. Le payload signé est encodé avec Reed-Solomon → payload protégé. Le payload protégé est éventuellement répété N fois. L'algorithme stéganographique (DCT ou spread spectrum, choisi après l'axe A) insère les bits dans l'image. L'image signée est renvoyée au créateur.

- Flux de lecture

    > Un utilisateur uploade une image à vérifier. L'algorithme stéganographique extrait les bits. Si répétition : vote majoritaire sur les N copies. Décodage Reed-Solomon → récupération du payload signé (avec correction d'erreurs). Vérification de la signature ECDSA avec la clé publique de la plateforme. Si valide : afficher l'auteur (user ID → nom via la BDD) et la date de signature. Si invalide : l'image n'est pas signée par la plateforme, ou la signature a été trop dégradée.


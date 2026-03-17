## Project TPI
Proposer une solution afin d'assurer une traçabilité sur du contenu (image) produit par des créateurs à l'aide de la stéganographie.

### Thématiques
Web, Computer Vision, Analyse d’images, Cryptographie, Signatures, IA Génératives

### Ressources
Il n'y a pas de solution unique identifiée et pour cette raison, il n'y a pas de ressource disponible pour ce projet

### Objectifs
- Fournir une plateforme web qui mettra en œuvre les solutions implémentées et permettra de les utiliser
- Fonctionnalités attendues 
    - Être capable de fournir une image qui sera signée par la plateforme (au nom de la personne l'ayant importé, que l'on désignera comme auteur)
    - Être capable d'authentifier une signature dans une image existante (signée par votre plateforme)
    - Proposer une solutions pour tenter d'identifier si une image a été générée par une IA
- Complexité
    - Etudier et tester les algorithmes / approches existantes dans le domaine de la stéganographie
    - Après les avoir étudiées, proposer différentes solutions pour la mise en oeuvre de la signature
    - Construire une solution qui rendra la signature ajoutée résistante à la compression
    - Lorsque l'on compresse certains formats d'image, l'altération de l'image peut entrainer une perte de données (problématique vis à vis du format JPG, à investiguer)
    - Lorsqu'une image est enregistrée à plusieurs reprise, elle se dégrade, la signature doit résister un minimum (identifier les limites ?)
- Ouvertures
    - Vous pouvez proposer d'autres fonctionnalités que vous jugez utile dans ce contexte
    - Vous pouvez construire votre propre algorithme s'il apporte une solution à un problème
    - Vous pouvez vous appuyer sur des IA pour certaines fonctionnalités si c'est pertinent

### Description des service

- Algorithmes de la stéganographie
    
    - > Ce bloc consiste à effectuer une étude comparatives ( invisibilité, capacité, robustesse) des différents algorithmes de la steganographie, les catégoriser les tester et faire une selection de ceux qui seront utilisés dans les services.

    - Domaine Spatial
        - LSB
    - Domaine fréquentiel
        - DCT
        - Spread Spectrum

    - > Les Critères de Comparaison des algorithmes
        - Invisibilité : ( calcule le PSNR (Peak Signal-to-Noise Ratio ) )
        - Capacité : calcule du nombre de bits à cacher par images ( bpp : bit per picture )
        - Robustesse : ( surtout face à la compression, aux réenregistrements, aux manipulations ( crop, rotation , ajout de bruit ) ) avec le calcule du BER ( Bit Error Rate)




